import pytest

def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "project" in data

def test_upload_resume_raw_text(client, sample_resume_text):
    response = client.post(
        "/api/v1/resumes/upload",
        data={"raw_text": sample_resume_text, "tenant_id": "test_org"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUCCESS"
    assert "candidate_id" in data
    assert data["chunks_indexed"] >= 1

def test_evaluate_candidate_api(client, sample_resume_text, sample_job_description):
    payload = {
        "job_description": sample_job_description.model_dump(),
        "raw_resume_text": sample_resume_text
    }
    response = client.post("/api/v1/evaluate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "parsed_profile" in data
    assert "gap_analysis" in data
    assert "interview_questions" in data
    assert "final_scorecard" in data
    assert data["final_scorecard"]["recommendation"] in ["STRONG_HIRE", "HIRE"]

def test_search_candidates_api(client):
    response = client.get("/api/v1/candidates/search?query=Python+FastAPI")
    assert response.status_code == 200
    data = response.json()
    assert "hits" in data
