from typing import List, Optional
from pydantic import BaseModel, Field

class JobDescription(BaseModel):
    job_id: str = Field(description="Unique identifier for the job posting")
    title: str = Field(description="Target role title, e.g. Senior Backend Engineer")
    department: str = Field(default="Engineering")
    location: str = Field(default="Remote")
    min_years_experience: float = Field(ge=0.0, description="Minimum mandatory years of experience")
    mandatory_skills: List[str] = Field(description="Non-negotiable required technical skills")
    preferred_skills: List[str] = Field(default_factory=list, description="Bonus / good-to-have technical skills")
    responsibilities: List[str] = Field(default_factory=list)
    raw_text: str = Field(description="Raw text of the job description")

class MatchResult(BaseModel):
    candidate_id: str
    job_id: str
    overall_match_percentage: float = Field(ge=0.0, le=100.0)
    hard_criteria_passed: bool
    matched_mandatory_skills: List[str]
    missing_mandatory_skills: List[str]
    matched_preferred_skills: List[str]
    experience_gap_years: float = Field(default=0.0)
    summary_verdict: str
