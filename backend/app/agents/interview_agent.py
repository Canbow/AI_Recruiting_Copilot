import logging
from typing import Dict, Any, List
from app.schemas.state import RecruiterState, InterviewQuestion

logger = logging.getLogger(__name__)

async def tech_questions_node(state: RecruiterState) -> Dict[str, Any]:
    """
    Parallel Branch 4A: Synthesizes technical probe questions specifically targeting identified skill gaps.
    """
    gaps = state.get("skill_gaps", [])
    jd = state.get("job_description")
    
    probe_targets = [gap for gap in gaps if gap.status in ["SUPERFICIAL", "MISSING"]][:3]
    if not probe_targets and gaps:
        probe_targets = gaps[:2]
        
    tech_questions: List[InterviewQuestion] = []
    
    for gap in probe_targets:
        skill = gap.skill_name
        if gap.status == "MISSING":
            prompt = f"How would you approach designing or implementing a solution using {skill}, and how does your past architectural experience transfer to this stack?"
            reason = f"Candidate's resume lacks direct evidence of mandatory requirement '{skill}'."
            criteria = f"Listen for core conceptual understanding, architectural tradeoffs, and hands-on familiarity."
        else:
            prompt = f"Can you walk us through a challenging production debugging scenario or scale optimization you personally led using {skill}?"
            reason = f"Candidate lists '{skill}', but project accomplishments lack deep measurable metrics."
            criteria = f"Look for depth: mentions of concurrency, latency bottlenecks, memory profiling, or production incidents."
            
        tech_questions.append(InterviewQuestion(
            category="TECHNICAL_GAP",
            target_skill_or_competency=skill,
            question_prompt=prompt,
            context_or_probe_reason=reason,
            what_a_great_answer_sounds_like=criteria
        ))
        
    logger.info(f"Generated {len(tech_questions)} technical gap interview questions.")
    # Return ONLY interview_questions so parallel branches merge cleanly via operator.add reducer!
    return {
        "interview_questions": tech_questions
    }

async def behavioral_questions_node(state: RecruiterState) -> Dict[str, Any]:
    """
    Parallel Branch 4B: Synthesizes behavioral, ownership, and leadership questions based on work history.
    """
    behavioral_questions = [
        InterviewQuestion(
            category="BEHAVIORAL_LEADERSHIP",
            target_skill_or_competency="Technical Disagreement & Cross-Functional Alignment",
            question_prompt="Tell me about a time you strongly disagreed with an engineering or product decision. How did you present your case and arrive at a consensus?",
            context_or_probe_reason="Assessing communication maturity and ability to drive constructive technical alignment.",
            what_a_great_answer_sounds_like="Presents data-driven arguments, listens objectively, commits to team decision even if differing."
        ),
        InterviewQuestion(
            category="BEHAVIORAL_LEADERSHIP",
            target_skill_or_competency="Production Incident Ownership & Post-Mortem",
            question_prompt="Describe a production outage or critical regression caused by code you deployed. How did you respond under pressure, mitigate the impact, and ensure it never happens again?",
            context_or_probe_reason="Assessing extreme ownership, blameless post-mortem culture, and defensive engineering practices.",
            what_a_great_answer_sounds_like="Takes direct ownership without blaming others, focuses on telemetry/root cause, implements permanent automated tests/circuit breakers."
        )
    ]
    
    logger.info(f"Generated {len(behavioral_questions)} behavioral interview questions.")
    # Return ONLY interview_questions so parallel branches merge cleanly via operator.add reducer!
    return {
        "interview_questions": behavioral_questions
    }
