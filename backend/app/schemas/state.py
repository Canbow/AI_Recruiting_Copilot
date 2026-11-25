from typing import List, Optional, Annotated, Dict, Any
from typing_extensions import TypedDict
import operator
from pydantic import BaseModel, Field
from app.schemas.candidate import CandidateProfile, SkillGap
from app.schemas.job import JobDescription, MatchResult

class InterviewQuestion(BaseModel):
    category: str = Field(description="'TECHNICAL_GAP' or 'BEHAVIORAL_LEADERSHIP'")
    target_skill_or_competency: str
    question_prompt: str
    context_or_probe_reason: str
    what_a_great_answer_sounds_like: str

class ExecutiveScorecard(BaseModel):
    candidate_name: str
    job_title: str
    overall_score: float = Field(ge=0.0, le=100.0)
    recommendation: str = Field(description="'STRONG_HIRE', 'HIRE', 'LEAN_HIRE', or 'REJECT'")
    key_strengths: List[str]
    critical_risks_or_gaps: List[str]
    executive_summary: str
    suggested_interview_focus: str

class RecruiterState(TypedDict):
    """
    Stateful multi-agent DAG state in LangGraph.
    Uses reducers (operator.add) to safely concatenate outputs from concurrent parallel nodes.
    """
    # Ingestion inputs
    candidate_id: str
    raw_resume_text: str
    job_description: JobDescription
    
    # Node 1: Resume Extraction Agent
    parsed_profile: Optional[CandidateProfile]
    
    # Node 2: Skill Mapping Agent
    canonical_skills: List[str]
    
    # Node 3: Gap Analysis Agent
    gap_analysis: Optional[MatchResult]
    skill_gaps: List[SkillGap]
    hard_criteria_passed: bool
    
    # Node 4: Parallel Question Generation (Fan-out / Fan-in)
    # operator.add ensures that concurrent branch updates are merged into the list!
    interview_questions: Annotated[List[InterviewQuestion], operator.add]
    
    # Node 5: Report Creation Agent
    final_scorecard: Optional[ExecutiveScorecard]
    
    # Execution Tracking & Error Handling
    current_step: str
    error_flag: bool
    error_log: Annotated[List[str], operator.add]
