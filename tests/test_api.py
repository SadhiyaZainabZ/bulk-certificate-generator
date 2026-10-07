import time
from pathlib import Path

from app import certificate
from app.database import SessionLocal
from app.models import Recipient


def wait_for_completion(client, job_id):
    for _ in range(50):
        response = client.get(f"/jobs/{job_id}")
        data = response.json()

        if data["status"] in {"completed", "completed_with_errors"}:
            return data

        time.sleep(0.05)

    raise AssertionError("Job did not finish in time")


def payload():
    return {
        "event_name": "Python Bootcamp",
        "event_date": "October 07, 2026",
        "issuer": "Code Academy",
        "recipients": [
            {
                "name": "Aarav Kumar",
                "email": "aarav@example.com",
                "achievement": "for successfully completing the Python Bootcamp",
            },
            {
                "name": "Meera Shah",
                "email": "meera@example.com",
                "achievement": "for successfully completing the Python Bootcamp",
            },
        ],
    }


def test_create_generation_job(client):
    response = client.post("/jobs", json=payload())

    assert response.status_code == 202
    assert "job_id" in response.json()


def test_input_validation(client):
    data = payload()
    data["recipients"][0]["email"] = "wrong-email"

    response = client.post("/jobs", json=data)

    assert response.status_code == 422


def test_certificate_generation(client):
    response = client.post("/jobs", json=payload())
    job_id = response.json()["job_id"]

    data = wait_for_completion(client, job_id)

    assert data["successful"] == 2
    assert data["failed"] == 0
    assert data["progress_percent"] == 100.0

    recipient_id = data["certificates"][0]["recipient_id"]

    db = SessionLocal()
    recipient = db.get(Recipient, recipient_id)

    assert recipient.file_path
    assert Path(recipient.file_path).exists()

    db.close()


def test_job_status_progress(client):
    response = client.post("/jobs", json=payload())
    job_id = response.json()["job_id"]

    data = wait_for_completion(client, job_id)

    assert data["total"] == 2
    assert data["completed"] == 2
    assert data["status"] == "completed"


def test_individual_certificate_failure(client, monkeypatch):
    original = certificate.create_certificate

    def fake_create(*args, **kwargs):
        if kwargs["recipient_name"] == "Aarav Kumar":
            raise RuntimeError("Demo PDF generation failure")

        return original(*args, **kwargs)

    monkeypatch.setattr(
        "app.service.create_certificate",
        fake_create,
    )

    response = client.post("/jobs", json=payload())
    job_id = response.json()["job_id"]

    data = wait_for_completion(client, job_id)

    assert data["successful"] == 1
    assert data["failed"] == 1
    assert data["status"] == "completed_with_errors"

    failed = [
        item for item in data["certificates"]
        if item["status"] == "failed"
    ][0]

    assert "Demo PDF generation failure" in failed["error"]


def test_retrieve_generated_certificate(client):
    response = client.post("/jobs", json=payload())
    job_id = response.json()["job_id"]

    data = wait_for_completion(client, job_id)
    recipient_id = data["certificates"][0]["recipient_id"]

    download = client.get(
        f"/certificates/{recipient_id}/download"
    )

    assert download.status_code == 200
    assert download.headers["content-type"] == "application/pdf"
    assert download.content.startswith(b"%PDF")
