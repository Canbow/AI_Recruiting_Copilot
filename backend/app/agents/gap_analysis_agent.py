import logging
from typing import Dict, Any, List
from app.schemas.candidate import SkillGap
from app.schemas.job import JobDescription, MatchResult
from app.schemas.state import RecruiterState
from app.config import settings

logger = logging.getLogger(__name__)

async def gap_analysis_agent(state: RecruiterState) -> Dict[str, Any]:
    """
    Node 3: Compares Candidate profile & canonical skills against Job Requirements.
    Calculates overall match score and identifies critical gaps.
    """
    profile = state.get("parsed_profile")
    candidate_skills = set(state.get("canonical_skills", []))
    jd: JobDescription = state.get("job_description")
    
    if not profile or not jd:
        return {
            "error_flag": True,
            "error_log": ["GapAnalysisAgent: Missing parsed profile or Job Description."],
            "current_step": "gap_analysis_failed"
        }
        
    mandatory_reqs = set(jd.mandatory_skills)
    preferred_reqs = set(jd.preferred_skills)
    
    # Analyze mandatory matches & gaps
    matched_mandatory = list(candidate_skills.intersection(mandatory_reqs))
    missing_mandatory = list(mandatory_reqs.difference(candidate_skills))
    
    # Analyze preferred matches
    matched_preferred = list(candidate_skills.intersection(preferred_reqs))
    
    # Calculate structured SkillGaps with grounding citations
    skill_gaps: List[SkillGap] = []
    
    # Create text search blob from work accomplishments
    accomplishments_text = " ".join([
        " ".join(item.key_accomplishments) for item in profile.work_history
    ]) + " " + " ".join(profile.primary_skills)
    
    for skill in mandatory_reqs:
        if skill in candidate_skills:
            # Check for grounding evidence in work history
            evidence = None
            for item in profile.work_history:
                for bullet in item.key_accomplishments:
                    if skill.lower() in bullet.lower():
                        evidence = f"{item.company}: {bullet}"
                        break
                if evidence:
                    break
                    
            if evidence:
                status = "VERIFIED"
                severity = "NONE"
                notes = f"Grounding evidence found in accomplishments: {evidence}"
            else:
                status = "SUPERFICIAL"
                severity = "MODERATE"
                notes = "Skill listed in primary list, but lacks detailed project accomplishments."
                
            skill_gaps.append(SkillGap(
                skill_name=skill,
                is_mandatory=True,
                candidate_evidence=evidence,
                status=status,
                severity=severity,
                notes=notes
            ))
        else:
            skill_gaps.append(SkillGap(
                skill_name=skill,
                is_mandatory=True,
                candidate_evidence=None,
                status="MISSING",
                severity="CRITICAL",
                notes=f"Missing non-negotiable requirement for {jd.title}."
            ))

    # Experience gap
    exp_gap = max(0.0, jd.min_years_experience - profile.years_experience)
    
    # Scoring algorithm
    # Mandatory skills account for 70% weight, experience 20%, preferred skills 10%
    mandatory_score = (len(matched_mandatory) / max(1, len(mandatory_reqs))) * 70.0
    experience_score = min(1.0, profile.years_experience / max(1.0, jd.min_years_experience)) * 20.0
    preferred_score = (len(matched_preferred) / max(1, len(preferred_reqs))) * 10.0 if preferred_reqs else 10.0
    
    overall_match = round(mandatory_score + experience_score + preferred_score, 2)
    
    # Hard criteria predicate: candidate must satisfy >= 50% mandatory skills
    mandatory_ratio = len(matched_mandatory) / max(1, len(mandatory_reqs))
    hard_criteria_passed = (mandatory_ratio >= 0.50) and (exp_gap <= 2.0)
    
    verdict = (
        f"Qualified candidate with {overall_match}% match."
        if hard_criteria_passed
        else f"Unqualified candidate: missing {len(missing_mandatory)} critical mandatory skills."
    )
    
    match_result = MatchResult(
        candidate_id=state.get("candidate_id", "unknown"),
        job_id=jd.job_id,
        overall_match_percentage=overall_match,
        hard_criteria_passed=hard_criteria_passed,
        matched_mandatory_skills=matched_mandatory,
        missing_mandatory_skills=missing_mandatory,
        matched_preferred_skills=matched_preferred,
        experience_gap_years=exp_gap,
        summary_verdict=verdict
    )
    
    logger.info(f"Gap Analysis complete: Match={overall_match}%, HardCriteriaPassed={hard_criteria_passed}")
    
    return {
        "gap_analysis": match_result,
        "skill_gaps": skill_gaps,
        "hard_criteria_passed": hard_criteria_passed,
        "current_step": "gap_analysis_complete",
        "error_flag": False
    }
