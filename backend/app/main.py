import logging
import uuid
from typing import Optional, List
from pydantic import BaseModel, Field
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.schemas.job import JobDescription
from app.schemas.state import RecruiterState
from app.graph.workflow import recruiter_graph
from app.services.parser import parse_pdf_bytes, clean_text, semantic_section_chunker
from app.services.qdrant_service import qdrant_service
from app.services.database import init_db, SessionLocal, CandidateRecord, EvaluationRecord

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Multi-agent recruitment copilot powered by LangGraph, Qdrant, and OpenAI."
)

# Cross-Origin Resource Sharing (CORS) Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class EvaluateRequest(BaseModel):
    job_description: JobDescription
    candidate_id: Optional[str] = None
    raw_resume_text: Optional[str] = None

@app.on_event("startup")
def on_startup():
    init_db()
    logger.info("Recruiting Copilot API initialized and ready.")

# Centralized Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled server error on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": 500,
            "error_code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred while processing the request.",
            "detail": str(exc)
        }
    )

@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "qdrant_connected": qdrant_service.client is not None
    }

@app.post(f"{settings.API_V1_STR}/resumes/upload", tags=["Resumes"])
async def upload_resume(
    file: Optional[UploadFile] = File(None),
    raw_text: Optional[str] = Form(None),
    tenant_id: str = Form("default_org")
):
    candidate_id = f"cand_{uuid.uuid4().hex[:8]}"
    content = ""
    
    if file:
        file_bytes = await file.read()
        if file.filename.lower().endswith(".pdf"):
            content = parse_pdf_bytes(file_bytes)
        else:
            content = file_bytes.decode("utf-8", errors="ignore")
    elif raw_text:
        content = raw_text
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Must provide either an uploaded file or raw_text form field."
        )
        
    cleaned = clean_text(content)
    if len(cleaned) < 30:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Resume text contains insufficient information."
        )
        
    chunks = semantic_section_chunker(cleaned, candidate_id)
    
    qdrant_service.upsert_chunks(
        candidate_id=candidate_id,
        chunks=chunks,
        metadata={"tenant_id": tenant_id, "years_experience": 3.0}
    )
    
    db = SessionLocal()
    try:
        rec = CandidateRecord(
            id=candidate_id,
            full_name="Uploaded Candidate",
            years_experience=3.0,
            skills_json="[]"
        )
        db.add(rec)
        db.commit()
    finally:
        db.close()
        
    return {
        "candidate_id": candidate_id,
        "chunks_indexed": len(chunks),
        "status": "SUCCESS",
        "message": "Resume parsed and semantically indexed into Qdrant."
    }

@app.post(f"{settings.API_V1_STR}/evaluate", tags=["Evaluation"])
async def evaluate_candidate(request_data: EvaluateRequest):
    """
    Executes the 5-Agent LangGraph Workflow:
    1. Resume Extraction
    2. Skill Mapping (Taxonomy Normalization)
    3. Gap Analysis (Grounded Scoring & Fast-Reject check)
    4. Parallel Question Generation (Technical Gaps + Behavioral Leadership)
    5. Executive Scorecard Creation
    """
    job_description = request_data.job_description
    target_text = request_data.raw_resume_text or ""
    cid = request_data.candidate_id or f"cand_{uuid.uuid4().hex[:8]}"
    
    if not target_text and request_data.candidate_id:
        hits = qdrant_service.search(query=job_description.title, limit=5)
        matched_chunks = [h["payload"]["content"] for h in hits if h["payload"].get("candidate_id") == request_data.candidate_id]
        target_text = "\n\n".join(matched_chunks)
        
    if not target_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must provide either raw_resume_text or a valid candidate_id with indexed vectors."
        )

    initial_state: RecruiterState = {
        "candidate_id": cid,
        "raw_resume_text": target_text,
        "job_description": job_description,
        "parsed_profile": None,
        "canonical_skills": [],
        "gap_analysis": None,
        "skill_gaps": [],
        "hard_criteria_passed": True,
        "interview_questions": [],
        "final_scorecard": None,
        "current_step": "initialized",
        "error_flag": False,
        "error_log": []
    }
    
    logger.info(f"Invoking LangGraph DAG for Candidate {cid} against Job '{job_description.title}'")
    final_output = await recruiter_graph.ainvoke(initial_state)
    
    scorecard = final_output.get("final_scorecard")
    if scorecard:
        db = SessionLocal()
        try:
            eval_record = EvaluationRecord(
                id=f"eval_{uuid.uuid4().hex[:8]}",
                candidate_id=cid,
                job_id=job_description.job_id,
                overall_score=scorecard.overall_score,
                recommendation=scorecard.recommendation,
                scorecard_json=scorecard.model_dump_json()
            )
            db.add(eval_record)
            db.commit()
        finally:
            db.close()
            
    return {
        "candidate_id": cid,
        "job_id": job_description.job_id,
        "parsed_profile": final_output.get("parsed_profile"),
        "canonical_skills": final_output.get("canonical_skills"),
        "gap_analysis": final_output.get("gap_analysis"),
        "interview_questions": final_output.get("interview_questions"),
        "final_scorecard": final_output.get("final_scorecard"),
        "execution_steps_completed": final_output.get("current_step")
    }

@app.get(f"{settings.API_V1_STR}/candidates/search", tags=["Search"])
def search_candidates(
    query: str,
    tenant_id: str = "default_org",
    min_years_experience: float = 0.0,
    limit: int = 10
):
    results = qdrant_service.search(
        query=query,
        tenant_id=tenant_id,
        min_exp=min_years_experience,
        limit=limit
    )
    return {"query": query, "results_count": len(results), "hits": results}
