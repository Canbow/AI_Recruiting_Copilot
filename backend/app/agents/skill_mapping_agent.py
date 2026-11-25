import logging
from typing import Dict, Any, List
from app.schemas.state import RecruiterState

logger = logging.getLogger(__name__)

# Standard skill alias taxonomy dictionary
CANONICAL_TAXONOMY = {
    "reactjs": "React",
    "react.js": "React",
    "react": "React",
    "nextjs": "Next.js",
    "next.js": "Next.js",
    "golang": "Go",
    "go": "Go",
    "k8s": "Kubernetes",
    "kubernetes": "Kubernetes",
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "fastapi": "FastAPI",
    "docker": "Docker",
    "containerization": "Docker",
    "python": "Python",
    "python3": "Python",
    "aws": "AWS",
    "amazon web services": "AWS",
    "qdrant": "Qdrant",
    "langchain": "LangChain",
    "langgraph": "LangGraph",
    "typescript": "TypeScript",
    "ts": "TypeScript",
    "javascript": "JavaScript",
    "js": "JavaScript",
    "node": "Node.js",
    "nodejs": "Node.js",
    "node.js": "Node.js",
    "redis": "Redis",
    "graphql": "GraphQL",
    "rest": "REST APIs",
    "restful": "REST APIs",
    "rest apis": "REST APIs",
    "git": "Git",
    "ci/cd": "CI/CD",
    "linux": "Linux"
}

def normalize_skill(skill: str) -> str:
    cleaned = skill.strip().lower()
    return CANONICAL_TAXONOMY.get(cleaned, skill.strip())

async def skill_mapping_agent(state: RecruiterState) -> Dict[str, Any]:
    """
    Node 2: Normalizes extracted candidate skills into an industry canonical taxonomy.
    """
    parsed_profile = state.get("parsed_profile")
    if not parsed_profile:
        return {
            "error_flag": True,
            "error_log": ["SkillMappingAgent: Missing parsed profile in state."],
            "current_step": "skill_mapping_failed"
        }

    raw_skills = parsed_profile.primary_skills + parsed_profile.secondary_skills
    canonical_set = set()
    
    for s in raw_skills:
        canonical_name = normalize_skill(s)
        canonical_set.add(canonical_name)
        
    canonical_list = sorted(list(canonical_set))
    logger.info(f"Normalized {len(raw_skills)} raw skills to {len(canonical_list)} canonical taxonomy skills.")
    
    return {
        "canonical_skills": canonical_list,
        "current_step": "skill_mapping_complete",
        "error_flag": False
    }
