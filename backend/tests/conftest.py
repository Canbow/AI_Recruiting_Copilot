import sys
import os
import pytest
from fastapi.testclient import TestClient

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app
from app.schemas.job import JobDescription
from app.schemas.candidate import CandidateProfile, ExperienceItem, EducationItem

@pytest.fixture
def sample_resume_text() -> str:
    return """
    Hemanth L
    hailexample@gmail.com | Pune, India
    
    WORK EXPERIENCE
    AI Engineer Intern | Infosys Springboard
    - Developed modular Python-based ML workflows for exoplanet habitability prediction.
    - Built Stacking ensemble models using XGBoost, Random Forest, and Scikit-learn.
    - Implemented REST APIs using FastAPI and Flask for real-time model scoring.
    
    Backend Engineer | Tech Labs
    - Engineered high-throughput microservices using Go and Docker.
    - Built vector search pipelines using Qdrant and PostgreSQL for semantic retrieval.
    - Automated testing pipelines using Pytest with 85% test coverage.
    
    TECHNICAL SKILLS
    Languages: Python, Go, TypeScript, SQL
    Technologies: FastAPI, Docker, Kubernetes, Qdrant, PostgreSQL, Next.js, LangGraph, React
    
    EDUCATION
    B.Tech in Computer Science and Engineering | IIIT Pune (2027)
    """

@pytest.fixture
def sample_job_description() -> JobDescription:
    return JobDescription(
        job_id="job_backend_lead_101",
        title="Senior AI Backend Engineer",
        department="Engineering",
        min_years_experience=3.0,
        mandatory_skills=["Python", "FastAPI", "Docker", "Qdrant"],
        preferred_skills=["Go", "Kubernetes", "Next.js"],
        responsibilities=["Build autonomous multi-agent pipelines", "Deploy vector search infrastructure"],
        raw_text="Looking for a Senior AI Backend Engineer proficient in Python, FastAPI, Docker, and Vector Databases."
    )

@pytest.fixture
def sample_parsed_profile() -> CandidateProfile:
    return CandidateProfile(
        full_name="Hemanth L",
        email="hailexample@gmail.com",
        location="Pune, India",
        years_experience=3.5,
        primary_skills=["Python", "FastAPI", "Docker", "Qdrant", "Go"],
        secondary_skills=["PostgreSQL", "Next.js"],
        work_history=[
            ExperienceItem(
                company="Tech Labs",
                role="Backend Engineer",
                duration_months=42,
                key_accomplishments=["Engineered high-throughput microservices using Go and Docker."],
                technologies_used=["Python", "FastAPI", "Qdrant", "Docker"]
            )
        ],
        education=[
            EducationItem(institution="IIIT Pune", degree="B.Tech Computer Science", graduation_year=2027)
        ]
    )

@pytest.fixture
def client():
    return TestClient(app)
