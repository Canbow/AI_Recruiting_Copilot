import logging
from typing import Dict, Any, List
from langgraph.graph import StateGraph, START, END

from app.schemas.state import RecruiterState
from app.agents.extraction_agent import resume_extraction_agent
from app.agents.skill_mapping_agent import skill_mapping_agent
from app.agents.gap_analysis_agent import gap_analysis_agent
from app.agents.interview_agent import tech_questions_node, behavioral_questions_node
from app.agents.report_agent import report_creation_agent, fast_reject_report_node

logger = logging.getLogger(__name__)

def check_extraction_success(state: RecruiterState) -> List[str]:
    """
    Conditional Edge 1: Verifies whether resume extraction succeeded.
    """
    if state.get("error_flag", False) or not state.get("parsed_profile"):
        logger.warning("Resume extraction failed. Halting workflow.")
        return [END]
    return ["skill_mapping"]

def check_candidate_qualification(state: RecruiterState) -> List[str]:
    """
    Conditional Edge 2: Evaluates hard criteria pass/fail.
    Returns:
    - ["fast_reject_report"] to skip question generation and save token costs.
    - ["tech_questions", "behavioral_questions"] to trigger parallel fan-out!
    """
    if not state.get("hard_criteria_passed", False):
        logger.info("Candidate did not meet hard mandatory criteria. Routing to Fast-Track Rejection.")
        return ["fast_reject_report"]
    logger.info("Candidate passed hard criteria. Routing to Parallel Interview Generation.")
    return ["tech_questions", "behavioral_questions"]

def build_recruiter_graph() -> StateGraph:
    """
    Constructs the hybrid multi-agent DAG in LangGraph:
    - Sequential analytical spine: Extraction -> Mapping -> Gap Analysis
    - Conditional decision routing: Quality check + Hard criteria gating
    - Parallel execution (Fan-out / Fan-in): Technical + Behavioral question synthesis
    """
    workflow = StateGraph(RecruiterState)
    
    # 1. Register Agent Nodes
    workflow.add_node("resume_extraction", resume_extraction_agent)
    workflow.add_node("skill_mapping", skill_mapping_agent)
    workflow.add_node("gap_analysis", gap_analysis_agent)
    workflow.add_node("tech_questions", tech_questions_node)
    workflow.add_node("behavioral_questions", behavioral_questions_node)
    workflow.add_node("report_creation", report_creation_agent)
    workflow.add_node("fast_reject_report", fast_reject_report_node)
    
    # 2. Entry Point
    workflow.add_edge(START, "resume_extraction")
    
    # 3. Conditional Edge 1: Quality Check
    workflow.add_conditional_edges(
        "resume_extraction",
        check_extraction_success,
        ["skill_mapping", END]
    )
    
    # 4. Sequential Edge: Mapping -> Gap Analysis
    workflow.add_edge("skill_mapping", "gap_analysis")
    
    # 5. Conditional Edge 2: Hard Criteria Gate & Parallel Fan-Out
    workflow.add_conditional_edges(
        "gap_analysis",
        check_candidate_qualification,
        ["fast_reject_report", "tech_questions", "behavioral_questions"]
    )
    
    # 6. Parallel Fan-In: Both question branches merge into Report Creation
    workflow.add_edge("tech_questions", "report_creation")
    workflow.add_edge("behavioral_questions", "report_creation")
    
    # 7. Terminal Edges
    workflow.add_edge("report_creation", END)
    workflow.add_edge("fast_reject_report", END)
    
    return workflow

# Compiled runnable graph
recruiter_graph = build_recruiter_graph().compile()
