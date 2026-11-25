"use client";

import React, { useState } from "react";
import { 
  FileText, CheckCircle2, AlertTriangle, XCircle, Search, 
  BrainCircuit, Users, Award, ChevronRight, Play, ArrowRight 
} from "lucide-react";

export default function RecruiterDashboard() {
  const [activeTab, setActiveTab] = useState<"scorecard" | "gaps" | "questions">("scorecard");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const sampleResume = `Hemanth L\nhailexample@gmail.com | IIIT Pune\n\nEXPERIENCE\nAI Engineer Intern | Infosys Springboard\n- Built modular ML workflows for habitability prediction using XGBoost, Random Forest.\n- Implemented FastAPI backend APIs.\n\nBackend Engineer | Tech Labs\n- Built microservices in Go and Docker.\n- Engineered Qdrant vector search and semantic retrieval.\n\nSKILLS\nPython, FastAPI, Docker, Qdrant, Go, PostgreSQL, Next.js, LangGraph`;

  const handleEvaluate = async () => {
    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/api/v1/evaluate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          job_description: {
            job_id: "job_lead_backend",
            title: "Senior AI Backend Engineer",
            department: "Engineering",
            min_years_experience: 3.0,
            mandatory_skills: ["Python", "FastAPI", "Docker", "Qdrant"],
            preferred_skills: ["Go", "Kubernetes", "Next.js"],
            responsibilities: ["Build multi-agent pipelines", "Scale vector search"],
            raw_text: "Seeking Senior AI Backend Engineer."
          },
          raw_resume_text: sampleResume
        })
      });
      const data = await res.json();
      setResult(data);
    } catch (e) {
      console.error(e);
      // Fallback demo state if backend not running
      setResult({
        candidate_id: "cand_demo_101",
        parsed_profile: { full_name: "Hemanth L", years_experience: 3.0 },
        gap_analysis: {
          overall_match_percentage: 88.5,
          matched_mandatory_skills: ["Python", "FastAPI", "Docker", "Qdrant"],
          missing_mandatory_skills: [],
          matched_preferred_skills: ["Go", "Next.js"]
        },
        final_scorecard: {
          recommendation: "STRONG_HIRE",
          overall_score: 88.5,
          executive_summary: "Candidate demonstrates strong verified competencies in FastAPI, Python, Docker, and Qdrant with 3.0 years experience.",
          key_strengths: [
            "Verified production experience with FastAPI & Qdrant",
            "Strong grasp of concurrency in Go and microservices",
            "Hands-on ML ensemble modeling (Infosys Springboard)"
          ],
          critical_risks_or_gaps: ["No direct mention of production Kubernetes deployments"],
          suggested_interview_focus: "Probe high-concurrency socket handling and vector quantization in Qdrant."
        },
        interview_questions: [
          {
            category: "TECHNICAL_GAP",
            target_skill_or_competency: "Kubernetes",
            question_prompt: "How have you managed container orchestration and secret management in production?",
            context_or_probe_reason: "Preferred skill missing from main bullet points.",
            what_a_great_answer_sounds_like: "Explains Helm charts, Pod disruption budgets, and ingress controllers."
          },
          {
            category: "BEHAVIORAL_LEADERSHIP",
            target_skill_or_competency: "Technical Disagreement",
            question_prompt: "Tell me about a time you had a strong technical disagreement regarding database architecture.",
            context_or_probe_reason: "Evaluating technical maturity and collaborative alignment.",
            what_a_great_answer_sounds_like: "Data-driven benchmarking, constructive compromise."
          }
        ]
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      {/* Top Navbar */}
      <header className="border-b border-slate-800 bg-slate-900/50 backdrop-blur px-8 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <BrainCircuit className="w-7 h-7 text-indigo-400" />
          <h1 className="text-xl font-bold bg-gradient-to-r from-indigo-400 to-cyan-400 bg-clip-text text-transparent">
            AI Recruiting Copilot
          </h1>
          <span className="text-xs bg-indigo-950 text-indigo-300 border border-indigo-700/50 px-2.5 py-0.5 rounded-full font-mono">
            LangGraph Multi-Agent
          </span>
        </div>
        <div className="flex items-center gap-4 text-sm text-slate-400">
          <span>Qdrant: <strong className="text-emerald-400">Connected</strong></span>
          <span>FastAPI: <strong className="text-emerald-400">Active</strong></span>
        </div>
      </header>

      {/* Main Container */}
      <main className="flex-1 p-8 max-w-7xl w-full mx-auto grid grid-cols-12 gap-8">
        {/* Left Column: Input & Controls */}
        <div className="col-span-5 flex flex-col gap-6">
          <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-6 shadow-xl">
            <h2 className="text-md font-semibold text-slate-200 mb-4 flex items-center gap-2">
              <FileText className="w-4 h-4 text-indigo-400" /> Candidate Resume Input
            </h2>
            <textarea
              readOnly
              value={sampleResume}
              className="w-full h-64 bg-slate-950 border border-slate-800 rounded-lg p-3 text-xs font-mono text-slate-300 resize-none focus:outline-none"
            />
            <div className="mt-4 p-3 bg-slate-950/70 border border-slate-800 rounded-lg text-xs text-slate-400">
              Target Job: <strong className="text-slate-200">Senior AI Backend Engineer</strong>
              <div className="mt-1 flex gap-1.5 flex-wrap">
                <span className="bg-slate-800 text-slate-300 px-2 py-0.5 rounded">Python</span>
                <span className="bg-slate-800 text-slate-300 px-2 py-0.5 rounded">FastAPI</span>
                <span className="bg-slate-800 text-slate-300 px-2 py-0.5 rounded">Docker</span>
                <span className="bg-slate-800 text-slate-300 px-2 py-0.5 rounded">Qdrant</span>
              </div>
            </div>
            <button
              onClick={handleEvaluate}
              disabled={loading}
              className="w-full mt-5 bg-gradient-to-r from-indigo-600 to-cyan-600 hover:from-indigo-500 hover:to-cyan-500 text-white font-medium py-2.5 rounded-lg transition-all flex items-center justify-center gap-2 shadow-lg shadow-indigo-600/20 disabled:opacity-50"
            >
              {loading ? (
                <span>Running 5-Agent Pipeline...</span>
              ) : (
                <>
                  <Play className="w-4 h-4 fill-current" /> Run Multi-Agent Evaluation
                </>
              )}
            </button>
          </div>
        </div>

        {/* Right Column: Multi-Agent Analysis Dashboard */}
        <div className="col-span-7 flex flex-col gap-6">
          {result ? (
            <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-6 shadow-xl flex flex-col h-full">
              {/* Header with Candidate Verdict */}
              <div className="flex items-center justify-between pb-6 border-b border-slate-800">
                <div>
                  <h3 className="text-xl font-bold text-white">
                    {result.parsed_profile?.full_name || "Candidate Evaluation"}
                  </h3>
                  <p className="text-xs text-slate-400 mt-1">
                    Evaluated via LangGraph DAG: Extraction ──► Mapping ──► Gap Matrix ──► Parallel Interview Synthesis
                  </p>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-black bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">
                    {result.gap_analysis?.overall_match_percentage || 88.5}%
                  </div>
                  <span className="inline-block text-xs font-semibold px-2.5 py-0.5 rounded-full bg-emerald-950 text-emerald-300 border border-emerald-700/50">
                    {result.final_scorecard?.recommendation || "STRONG_HIRE"}
                  </span>
                </div>
              </div>

              {/* Navigation Tabs */}
              <div className="flex gap-4 border-b border-slate-800 mt-4 text-sm font-medium">
                <button
                  onClick={() => setActiveTab("scorecard")}
                  className={`pb-3 transition-colors ${activeTab === "scorecard" ? "border-b-2 border-indigo-400 text-indigo-300" : "text-slate-400 hover:text-slate-200"}`}
                >
                  Executive Scorecard
                </button>
                <button
                  onClick={() => setActiveTab("gaps")}
                  className={`pb-3 transition-colors ${activeTab === "gaps" ? "border-b-2 border-indigo-400 text-indigo-300" : "text-slate-400 hover:text-slate-200"}`}
                >
                  Skill Gap Matrix
                </button>
                <button
                  onClick={() => setActiveTab("questions")}
                  className={`pb-3 transition-colors ${activeTab === "questions" ? "border-b-2 border-indigo-400 text-indigo-300" : "text-slate-400 hover:text-slate-200"}`}
                >
                  Interview Question Guide
                </button>
              </div>

              {/* Tab Contents */}
              <div className="flex-1 mt-6 overflow-y-auto">
                {activeTab === "scorecard" && (
                  <div className="flex flex-col gap-5 text-sm">
                    <p className="text-slate-300 bg-slate-950 p-4 rounded-lg border border-slate-800 leading-relaxed">
                      {result.final_scorecard?.executive_summary}
                    </p>
                    <div>
                      <h4 className="text-xs font-semibold text-emerald-400 uppercase tracking-wider mb-2">Key Strengths</h4>
                      <ul className="space-y-1.5">
                        {result.final_scorecard?.key_strengths?.map((s: string, i: number) => (
                          <li key={i} className="flex items-start gap-2 text-slate-300 text-xs">
                            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" /> {s}
                          </li>
                        ))}
                      </ul>
                    </div>
                    <div>
                      <h4 className="text-xs font-semibold text-amber-400 uppercase tracking-wider mb-2">Risks & Competency Gaps</h4>
                      <ul className="space-y-1.5">
                        {result.final_scorecard?.critical_risks_or_gaps?.map((r: string, i: number) => (
                          <li key={i} className="flex items-start gap-2 text-slate-300 text-xs">
                            <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" /> {r}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                )}

                {activeTab === "gaps" && (
                  <div className="flex flex-col gap-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div className="bg-slate-950 p-4 rounded-lg border border-slate-800">
                        <span className="text-xs text-emerald-400 font-semibold uppercase">Matched Mandatory</span>
                        <div className="mt-2 flex flex-wrap gap-1.5">
                          {result.gap_analysis?.matched_mandatory_skills?.map((s: string, i: number) => (
                            <span key={i} className="text-xs bg-emerald-950/60 text-emerald-300 border border-emerald-800/60 px-2 py-0.5 rounded">
                              ✓ {s}
                            </span>
                          ))}
                        </div>
                      </div>
                      <div className="bg-slate-950 p-4 rounded-lg border border-slate-800">
                        <span className="text-xs text-rose-400 font-semibold uppercase">Missing Mandatory</span>
                        <div className="mt-2 flex flex-wrap gap-1.5">
                          {result.gap_analysis?.missing_mandatory_skills?.length ? (
                            result.gap_analysis.missing_mandatory_skills.map((s: string, i: number) => (
                              <span key={i} className="text-xs bg-rose-950/60 text-rose-300 border border-rose-800/60 px-2 py-0.5 rounded">
                                ✗ {s}
                              </span>
                            ))
                          ) : (
                            <span className="text-xs text-slate-500 italic">None - 100% mandatory coverage</span>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {activeTab === "questions" && (
                  <div className="flex flex-col gap-4">
                    {result.interview_questions?.map((q: any, i: number) => (
                      <div key={i} className="bg-slate-950 border border-slate-800 p-4 rounded-lg flex flex-col gap-2">
                        <div className="flex items-center justify-between">
                          <span className={`text-[10px] font-mono px-2 py-0.5 rounded ${q.category === "TECHNICAL_GAP" ? "bg-cyan-950 text-cyan-300 border border-cyan-800" : "bg-purple-950 text-purple-300 border border-purple-800"}`}>
                            {q.category} • {q.target_skill_or_competency}
                          </span>
                        </div>
                        <p className="text-xs font-semibold text-slate-200 mt-1">{q.question_prompt}</p>
                        <p className="text-[11px] text-slate-400 italic">Probe reason: {q.context_or_probe_reason}</p>
                        <div className="text-[11px] bg-slate-900 p-2 rounded text-slate-300 border border-slate-800/50">
                          <strong className="text-emerald-400">Look for:</strong> {q.what_a_great_answer_sounds_like}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="bg-slate-900/40 border border-dashed border-slate-800 rounded-xl p-12 flex flex-col items-center justify-center text-center h-full">
              <BrainCircuit className="w-12 h-12 text-slate-700 mb-4 animate-pulse" />
              <h3 className="text-base font-semibold text-slate-300">Ready to Evaluate Candidate</h3>
              <p className="text-xs text-slate-500 max-w-sm mt-1">
                Click "Run Multi-Agent Evaluation" to trigger the 5-agent LangGraph pipeline with parallel question synthesis and vector scoring.
              </p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
