from backend.app.services.analysis_job import AnalysisJob, QUEUED

def test_analysis_job_creation():
    job = AnalysisJob(
        job_id="test-job-1",
        repository_path="./compiler",
        status=QUEUED,
    )

    assert job.job_id == "test-job-1"
    assert job.repository_path == "./compiler"
    assert job.status == "queued"