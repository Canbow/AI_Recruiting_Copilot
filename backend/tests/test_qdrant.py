import pytest
from app.services.parser import semantic_section_chunker, clean_text
from app.services.qdrant_service import QdrantVectorService

def test_semantic_chunker():
    text = """
    Jane Developer
    
    WORK EXPERIENCE
    Software Engineer at Acme Corp
    Built microservices in Go.
    
    TECHNICAL SKILLS
    Python, FastAPI, Docker, Kubernetes
    
    EDUCATION
    BS in Computer Science
    """
    chunks = semantic_section_chunker(text, "cand_test_42")
    assert len(chunks) >= 2
    sections = [c["section"] for c in chunks]
    assert "EXPERIENCE" in sections
    assert "SKILLS" in sections

def test_qdrant_vector_service():
    service = QdrantVectorService()
    
    # 1. Upsert chunks
    chunks = [
        {"section": "EXPERIENCE", "content": "Led backend API development in Python and FastAPI."},
        {"section": "SKILLS", "content": "Python, Docker, Kubernetes, PostgreSQL"}
    ]
    service.upsert_chunks(
        candidate_id="cand_test_100",
        chunks=chunks,
        metadata={"tenant_id": "test_org", "years_experience": 4.0}
    )
    
    # 2. Search with pre-filtering
    results = service.search(query="FastAPI backend engineer", tenant_id="test_org", min_exp=3.0, limit=5)
    assert len(results) >= 1
    assert results[0]["payload"]["candidate_id"] == "cand_test_100"
    assert results[0]["score"] > 0.0
    
    # 3. Filter by higher experience than candidate has -> should return empty
    empty_results = service.search(query="FastAPI", tenant_id="test_org", min_exp=10.0, limit=5)
    assert len(empty_results) == 0
