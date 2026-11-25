import asyncio
import pytest
from app.schemas.state import RecruiterState
from app.agents.extraction_agent import resume_extraction_agent, heuristic_extract_profile
from app.agents.skill_mapping_agent import skill_mapping_agent, normalize_skill
from app.agents.gap_analysis_agent import gap_analysis_agent
from app.agents.interview_agent import tech_questions_node, behavioral_questions_node
from app.agents.report_agent import report_creation_agent, fast_reject_report_node

def test_resume_extraction_agent_heuristic(sample_resume_text):
    state: RecruiterState = {
        "candidate_id": "test_cand_1",
        "raw_resume_text": sample_resume_text,
        "job_description": None,
        "parsed_profile": None,
        "canonical_skills": [],
        "gap_analysis": None,
        "skill_gaps": [],
        "hard_criteria_passed": True,
        "interview_questions": [],
        "final_scorecard": None,
        "current_step": "init",
        "error_flag": False,
        "error_log": []
    }
    output = asyncio.run(resume_extraction_agent(state))
    assert output["error_flag"] is False
    profile = output["parsed_profile"]
    assert profile is not None
    assert "Python" in profile.primary_skills
    assert "FastAPI" in profile.primary_skills

def test_skill_normalization():
    assert normalize_skill("reactjs") == "React"
    assert normalize_skill("React.js") == "React"
    assert normalize_skill("k8s") == "Kubernetes"
    assert normalize_skill("golang") == "Go"
    assert normalize_skill("postgres") == "PostgreSQL"
    assert normalize_skill("FASTAPI") == "FastAPI"

def test_skill_mapping_agent(sample_parsed_profile):
    state = {
        "parsed_profile": sample_parsed_profile,
        "current_step": "extraction_done"
    }
    output = asyncio.run(skill_mapping_agent(state))
    canonical = output["canonical_skills"]
    assert "Python" in canonical
    assert "FastAPI" in canonical
    assert "Go" in canonical

def test_gap_analysis_qualified_candidate(sample_parsed_profile, sample_job_description):
    state = {
        "candidate_id": "cand_1",
        "parsed_profile": sample_parsed_profile,
        "canonical_skills": ["Python", "FastAPI", "Docker", "Qdrant", "Go"],
        "job_description": sample_job_description
    }
    output = asyncio.run(gap_analysis_agent(state))
    assert output["error_flag"] is False
    assert output["hard_criteria_passed"] is True
    match_result = output["gap_analysis"]
    assert match_result.overall_match_percentage >= 70.0
    assert len(match_result.missing_mandatory_skills) == 0

def test_gap_analysis_unqualified_candidate(sample_job_description):
    from app.schemas.candidate import CandidateProfile
    weak_profile = CandidateProfile(
        full_name="Junior Dev",
        years_experience=0.5,
        primary_skills=["HTML", "CSS"],
        work_history=[]
    )
    state = {
        "candidate_id": "cand_weak",
        "parsed_profile": weak_profile,
        "canonical_skills": ["HTML", "CSS"],
        "job_description": sample_job_description
    }
    output = asyncio.run(gap_analysis_agent(state))
    assert output["hard_criteria_passed"] is False
    assert output["gap_analysis"].overall_match_percentage < 40.0
    assert len(output["gap_analysis"].missing_mandatory_skills) > 0

def test_parallel_interview_generation(sample_parsed_profile, sample_job_description):
    from app.schemas.candidate import SkillGap
    gaps = [
        SkillGap(skill_name="Kubernetes", is_mandatory=False, status="MISSING", severity="MODERATE", notes="No evidence"),
        SkillGap(skill_name="Qdrant", is_mandatory=True, status="SUPERFICIAL", severity="MODERATE", notes="Brief mention")
    ]
    state = {
        "parsed_profile": sample_parsed_profile,
        "job_description": sample_job_description,
        "skill_gaps": gaps
    }
    tech_out = asyncio.run(tech_questions_node(state))
    beh_out = asyncio.run(behavioral_questions_node(state))
    
    assert len(tech_out["interview_questions"]) >= 1
    assert tech_out["interview_questions"][0].category == "TECHNICAL_GAP"
    
    assert len(beh_out["interview_questions"]) >= 1
    assert beh_out["interview_questions"][0].category == "BEHAVIORAL_LEADERSHIP"

def test_report_creation_agent(sample_parsed_profile, sample_job_description):
    from app.schemas.job import MatchResult
    match = MatchResult(
        candidate_id="cand_1",
        job_id="job_1",
        overall_match_percentage=88.5,
        hard_criteria_passed=True,
        matched_mandatory_skills=["Python", "FastAPI"],
        missing_mandatory_skills=[],
        matched_preferred_skills=["Go"],
        summary_verdict="Strong match"
    )
    state = {
        "parsed_profile": sample_parsed_profile,
        "job_description": sample_job_description,
        "gap_analysis": match,
        "interview_questions": []
    }
    output = asyncio.run(report_creation_agent(state))
    scorecard = output["final_scorecard"]
    assert scorecard is not None
    assert scorecard.recommendation == "STRONG_HIRE"
    assert scorecard.overall_score == 88.5
