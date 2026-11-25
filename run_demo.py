#!/usr/bin/env python3
"""
AI Recruiting Copilot - Standalone CLI Pipeline Demo
Runs the 5-Agent LangGraph Workflow directly in your terminal.
"""

import asyncio
import sys
import os

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "backend")))

from app.schemas.job import JobDescription
from app.schemas.state import RecruiterState
from app.graph.workflow import recruiter_graph

SAMPLE_RESUME = """
HEMANTH L
hailexample@gmail.com | IIIT Pune

WORK EXPERIENCE
AI Engineer Intern — Infosys Springboard
- Developed modular Python-based ML workflows for exoplanet habitability prediction.
- Built Stacking ensemble models using XGBoost, Random Forest, and Scikit-learn.
- Implemented REST APIs using FastAPI and Flask for real-time model scoring.

Backend Engineer — Tech Labs
- Engineered high-throughput microservices using Go, Docker, and WebSockets.
- Built semantic vector search pipelines using Qdrant and PostgreSQL for candidate matching.
- Automated testing workflows using Pytest with 85% test coverage.

TECHNICAL SKILLS
Languages: Python, Go, TypeScript, SQL
Technologies & Frameworks: FastAPI, Docker, Kubernetes, Qdrant, PostgreSQL, Next.js, LangGraph, LangChain
"""

SAMPLE_JD = JobDescription(
    job_id="job_senior_ai_backend",
    title="Senior AI Backend Engineer",
    department="Core Engineering",
    min_years_experience=3.0,
    mandatory_skills=["Python", "FastAPI", "Docker", "Qdrant"],
    preferred_skills=["Go", "Kubernetes", "Next.js"],
    responsibilities=["Orchestrate multi-agent pipelines with LangGraph", "Optimize vector database search latency"],
    raw_text="Seeking Senior AI Backend Engineer proficient in Python, FastAPI, Docker, and Qdrant."
)

async def main():
    print("\n" + "="*75)
    print("🚀 STARTING AI RECRUITING COPILOT (LANGGRAPH MULTI-AGENT PIPELINE)")
    print("="*75)
    print(f"Target Job: {SAMPLE_JD.title}")
    print(f"Mandatory Requirements: {', '.join(SAMPLE_JD.mandatory_skills)}\n")
    
    initial_state: RecruiterState = {
        "candidate_id": "cand_demo_terminal",
        "raw_resume_text": SAMPLE_RESUME,
        "job_description": SAMPLE_JD,
        "parsed_profile": None,
        "canonical_skills": [],
        "gap_analysis": None,
        "skill_gaps": [],
        "hard_criteria_passed": True,
        "interview_questions": [],
        "final_scorecard": None,
        "current_step": "initialized",
        "error_flag": False,
        "error_log": []
    }
    
    print("⚡ Executing LangGraph DAG across 5 Autonomous Agents...")
    final_state = await recruiter_graph.ainvoke(initial_state)
    
    profile = final_state.get("parsed_profile")
    gap = final_state.get("gap_analysis")
    questions = final_state.get("interview_questions", [])
    scorecard = final_state.get("final_scorecard")
    
    print("\n" + "-"*75)
    print("1️⃣  RESUME EXTRACTION AGENT (Structured Output)")
    print(f"   Candidate: {profile.full_name if profile else 'N/A'}")
    print(f"   Experience: {profile.years_experience if profile else 0} Years")
    print(f"   Extracted Primary Skills: {', '.join(profile.primary_skills if profile else [])}")
    
    print("\n" + "-"*75)
    print("2️⃣  SKILL MAPPING AGENT (Taxonomy Normalization)")
    print(f"   Canonical Normalized Skills: {', '.join(final_state.get('canonical_skills', []))}")
    
    print("\n" + "-"*75)
    print("3️⃣  GAP ANALYSIS AGENT (Grounded Scoring & Gating)")
    print(f"   Overall Alignment Score: {gap.overall_match_percentage if gap else 0}%")
    print(f"   Hard Criteria Passed: {gap.hard_criteria_passed if gap else False}")
    print(f"   Matched Mandatory: {', '.join(gap.matched_mandatory_skills if gap else [])}")
    print(f"   Missing Mandatory: {', '.join(gap.missing_mandatory_skills if gap else ['None (100% Coverage)'])}")
    
    print("\n" + "-"*75)
    print(f"4️⃣  PARALLEL QUESTION GENERATION AGENT ({len(questions)} Questions Synthesized)")
    for i, q in enumerate(questions, 1):
        print(f"   [{i}] ({q.category}) - Target: {q.target_skill_or_competency}")
        print(f"       Prompt: {q.question_prompt}")
        print(f"       Look For: {q.what_a_great_answer_sounds_like}\n")
        
    print("-"*75)
    print("5️⃣  EXECUTIVE SCORECARD AGENT")
    print(f"   Recommendation: {scorecard.recommendation if scorecard else 'N/A'}")
    print(f"   Overall Score: {scorecard.overall_score if scorecard else 0}%")
    print(f"   Executive Summary:\n   {scorecard.executive_summary if scorecard else 'N/A'}")
    print("="*75 + "\n")

if __name__ == "__main__":
    asyncio.run(main())
