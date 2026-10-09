import asyncio

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.worker import create_analysis_worker
from backend.app.queue import get_analysis_queue
from backend.app.services.redis_state import get_analysis_state
from backend.app.database import get_database_connection


client = TestClient(app)


async def wait_for_job(queue, job_id: str, timeout: float = 60):
    deadline = asyncio.get_running_loop().time() + timeout

    while asyncio.get_running_loop().time() < deadline:
        job = await queue.getJob(job_id)

        if job is not None:
            state = await job.getState()

            if state == "completed":
                return job

            if state == "failed":
                raise AssertionError("Analysis job failed.")

        await asyncio.sleep(0.2)

    raise AssertionError("Analysis job timed out.")


def delete_analysis(analysis_id: int) -> None:
    connection = get_database_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            "DELETE FROM analyses WHERE id = %s",
            (analysis_id,),
        )

        connection.commit()
        cursor.close()

    finally:
        connection.close()


@pytest.mark.asyncio
async def test_full_analysis_pipeline():
    worker = await create_analysis_worker()
    queue = get_analysis_queue()

    database_id = None

    try:
        # Create the analysis through the API.
        response = client.post(
            "/api/v1/analyses",
            json={
                "repository_path": "./compiler",
                "limit": 5,
                "with_ai": False,
            },
        )

        assert response.status_code == 200

        created = response.json()

        analysis_id = created["analysis_id"]
        job_id = created["job_id"]

        assert created["status"] == "queued"

        # Check the initial Redis state.
        state = get_analysis_state(analysis_id)

        if state["status"] == "queued":
            assert state["stage"] == "queued"
            assert int(state["progress"]) == 0
        else:
            assert state["status"] == "running"
            assert state["stage"] in {"discovery", "analysis"}
            assert 0 <= int(state["progress"]) <= 100

        # Let the real worker process the job.
        job = await wait_for_job(queue, job_id)

        assert await job.getState() == "completed"

        # Check the final Redis state.
        state = get_analysis_state(analysis_id)

        assert state["status"] == "completed"
        assert state["stage"] == "completed"
        assert state["progress"] == "100"

        database_id = int(state["database_id"])

        assert database_id > 0

        # Check the analysis status endpoint.
        response = client.get(
            f"/api/v1/analyses/{analysis_id}"
        )

        assert response.status_code == 200

        status = response.json()

        assert status["analysis_id"] == analysis_id
        assert status["status"] == "completed"
        assert status["progress"] == 100
        assert status["database_id"] == database_id

        # Check claims.
        response = client.get(
            f"/api/v1/analyses/{analysis_id}/claims"
        )

        assert response.status_code == 200

        claims = response.json()

        assert claims["analysis_id"] == analysis_id
        assert isinstance(claims["claims"], list)

        # Check evidence.
        response = client.get(
            f"/api/v1/analyses/{analysis_id}/evidence"
        )

        assert response.status_code == 200

        evidence = response.json()

        assert evidence["analysis_id"] == analysis_id
        assert isinstance(evidence["evidence"], list)

        # Check analysis history.
        response = client.get("/api/v1/analyses")

        assert response.status_code == 200

        history = response.json()

        analysis = next(
            item
            for item in history["analyses"]
            if item["id"] == database_id
        )

        assert analysis["files_discovered"] > 0
        assert analysis["with_ai"] is False
        assert analysis["analysis_limit"] == 5

        # Check the database directly.
        connection = get_database_connection()

        try:
            cursor = connection.cursor(dictionary=True)

            cursor.execute(
                """
                SELECT
                    id,
                    repository_path,
                    files_discovered,
                    with_ai,
                    analysis_limit
                FROM analyses
                WHERE id = %s
                """,
                (database_id,),
            )

            analysis_row = cursor.fetchone()

            assert analysis_row is not None
            assert analysis_row["id"] == database_id
            assert analysis_row["files_discovered"] > 0
            assert analysis_row["with_ai"] == 0
            assert analysis_row["analysis_limit"] == 5

            cursor.execute(
                """
                SELECT COUNT(*) AS count
                FROM evidence
                WHERE analysis_id = %s
                """,
                (database_id,),
            )

            evidence_count = cursor.fetchone()["count"]

            cursor.execute(
                """
                SELECT COUNT(*) AS count
                FROM claims
                WHERE analysis_id = %s
                """,
                (database_id,),
            )

            claim_count = cursor.fetchone()["count"]

            assert evidence_count == len(evidence["evidence"])
            assert claim_count == len(claims["claims"])

            cursor.close()

        finally:
            connection.close()

    finally:
        # Remove the test analysis.
        if database_id is not None:
            delete_analysis(database_id)

        await worker.close()
        await queue.close()