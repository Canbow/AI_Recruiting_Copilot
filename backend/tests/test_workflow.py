import asyncio
import pytest
from app.graph.workflow import recruiter_graph
from app.schemas.state import RecruiterState

def test_full_graph_execution_qualified(sample_resume_text, sample_job_description):
    initial_state: RecruiterState = {
        "candidate_id": "cand_integration_test",
        "raw_resume_text": sample_resume_text,
        "job_description": sample_job_description,
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
    
    # Run through full LangGraph state machine
    final_state = asyncio.run(recruiter_graph.ainvoke(initial_state))
    
    # Assertions
    assert final_state["error_flag"] is False
    assert final_state["parsed_profile"] is not None
    assert len(final_state["canonical_skills"]) > 0
    assert final_state["gap_analysis"] is not None
    
    # Check that parallel fan-in reducer merged both question types
    questions = final_state["interview_questions"]
    assert len(questions) >= 2
    categories = {q.category for q in questions}
    assert "BEHAVIORAL_LEADERSHIP" in categories
    
    # Check final scorecard
    scorecard = final_state["final_scorecard"]
    assert scorecard is not None
    assert scorecard.overall_score >= 60.0
    assert scorecard.recommendation in ["STRONG_HIRE", "HIRE"]

def test_graph_conditional_fast_reject(sample_job_description):
    unqualified_text = """
    Random Person
    random@test.com
    EXPERIENCE: 2 months as Cashier.
    SKILLS: Cash handling, Customer Greeting.
    """
    initial_state: RecruiterState = {
        "candidate_id": "cand_unqualified",
        "raw_resume_text": unqualified_text,
        "job_description": sample_job_description,
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
    
    final_state = asyncio.run(recruiter_graph.ainvoke(initial_state))
    
    # Fast reject path should NOT generate interview questions to save API tokens!
    assert final_state["current_step"] == "fast_reject_complete"
    assert len(final_state["interview_questions"]) == 0
    assert final_state["final_scorecard"].recommendation == "REJECT"
