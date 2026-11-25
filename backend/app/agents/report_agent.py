import logging
from typing import Dict, Any, List
from app.schemas.state import RecruiterState, ExecutiveScorecard

logger = logging.getLogger(__name__)

async def report_creation_agent(state: RecruiterState) -> Dict[str, Any]:
    """
    Node 5: Synthesizes candidate profile, gap matrix, and interview guide into an Executive Scorecard.
    """
    profile = state.get("parsed_profile")
    match_result = state.get("gap_analysis")
    jd = state.get("job_description")
    questions = state.get("interview_questions", [])
    
    candidate_name = profile.full_name if profile else "Candidate"
    job_title = jd.title if jd else "Target Position"
    score = match_result.overall_match_percentage if match_result else 50.0
    
    # Determine recommendation tier
    if score >= 85.0:
        recommendation = "STRONG_HIRE"
    elif score >= 70.0:
        recommendation = "HIRE"
    elif score >= 50.0:
        recommendation = "LEAN_HIRE"
    else:
        recommendation = "REJECT"
        
    strengths = []
    if match_result:
        for s in match_result.matched_mandatory_skills[:4]:
            strengths.append(f"Strong verified competency in mandatory requirement: {s}")
    if profile and profile.years_experience >= (jd.min_years_experience if jd else 0):
        strengths.append(f"Meets seniority requirement with {profile.years_experience} years professional experience.")
        
    risks = []
    if match_result and match_result.missing_mandatory_skills:
        for s in match_result.missing_mandatory_skills:
            risks.append(f"Lacks direct experience with mandatory skill: {s}")
    if match_result and match_result.experience_gap_years > 0:
        risks.append(f"Experience deficit: {match_result.experience_gap_years} years below posted minimum.")
        
    if not risks:
        risks.append("No critical hard skill deficits identified.")
        
    summary = (
        f"{candidate_name} evaluated for {job_title} with an overall alignment score of {score}%. "
        f"Recommendation is {recommendation}. "
        f"Verified skills: {', '.join(match_result.matched_mandatory_skills if match_result else [])}. "
        f"Gaps requiring probe: {', '.join(match_result.missing_mandatory_skills if match_result else [])}."
    )
    
    focus = (
        "Focus technical interview rounds on system design tradeoffs and probing the identified skill gaps. "
        "Use the generated behavioral rubric to verify cross-functional communication and ownership under production pressure."
    )
    
    scorecard = ExecutiveScorecard(
        candidate_name=candidate_name,
        job_title=job_title,
        overall_score=score,
        recommendation=recommendation,
        key_strengths=strengths,
        critical_risks_or_gaps=risks,
        executive_summary=summary,
        suggested_interview_focus=focus
    )
    
    logger.info(f"Generated Executive Scorecard for {candidate_name}: Recommendation={recommendation}")
    return {
        "final_scorecard": scorecard,
        "current_step": "pipeline_complete",
        "error_flag": False
    }

async def fast_reject_report_node(state: RecruiterState) -> Dict[str, Any]:
    """
    Conditional Branch: Fast-track rejection report generator when hard non-negotiable criteria are failed.
    Saves token costs by skipping the interview question generation phase entirely.
    """
    profile = state.get("parsed_profile")
    match_result = state.get("gap_analysis")
    jd = state.get("job_description")
    
    candidate_name = profile.full_name if profile else "Candidate"
    job_title = jd.title if jd else "Target Position"
    score = match_result.overall_match_percentage if match_result else 25.0
    
    risks = [f"Failed non-negotiable prerequisite: {s}" for s in (match_result.missing_mandatory_skills if match_result else [])]
    
    scorecard = ExecutiveScorecard(
        candidate_name=candidate_name,
        job_title=job_title,
        overall_score=score,
        recommendation="REJECT",
        key_strengths=["Document successfully processed."],
        critical_risks_or_gaps=risks,
        executive_summary=f"{candidate_name} did not meet minimum threshold for {job_title}. Fast-tracked rejection.",
        suggested_interview_focus="Interview not recommended due to missing core mandatory prerequisites."
    )
    
    logger.info(f"Generated Fast-Track Rejection Scorecard for {candidate_name}.")
    return {
        "final_scorecard": scorecard,
        "current_step": "fast_reject_complete",
        "error_flag": False
    }
