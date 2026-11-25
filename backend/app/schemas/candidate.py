from typing import List, Optional
from pydantic import BaseModel, Field

class ExperienceItem(BaseModel):
    company: str = Field(description="Name of the employing company")
    role: str = Field(description="Candidate's job title")
    duration_months: int = Field(default=0, description="Total months in this role")
    key_accomplishments: List[str] = Field(default_factory=list, description="Measurable achievements/bullet points")
    technologies_used: List[str] = Field(default_factory=list, description="Specific frameworks/tools used in this role")

class EducationItem(BaseModel):
    institution: str = Field(description="University or college name")
    degree: str = Field(description="Degree name (e.g., B.Tech, M.S.)")
    graduation_year: Optional[int] = Field(default=None, description="Year of graduation")

class CandidateProfile(BaseModel):
    full_name: str = Field(description="Candidate's full name")
    email: Optional[str] = Field(default=None, description="Contact email")
    phone: Optional[str] = Field(default=None, description="Contact phone")
    location: Optional[str] = Field(default=None, description="City/Country or Remote")
    years_experience: float = Field(ge=0.0, description="Total calculated professional experience in years")
    primary_skills: List[str] = Field(min_length=1, description="Core technical proficiencies evidenced in work history")
    secondary_skills: List[str] = Field(default_factory=list, description="Peripheral tools or libraries mentioned")
    work_history: List[ExperienceItem] = Field(default_factory=list)
    education: List[EducationItem] = Field(default_factory=list)

class SkillGap(BaseModel):
    skill_name: str
    is_mandatory: bool = True
    candidate_evidence: Optional[str] = Field(default=None, description="Direct quote from resume validating competency")
    status: str = Field(description="'VERIFIED', 'SUPERFICIAL', or 'MISSING'")
    severity: str = Field(description="'CRITICAL', 'MODERATE', or 'NONE'")
    notes: str = Field(description="Reasoning behind evaluation")
