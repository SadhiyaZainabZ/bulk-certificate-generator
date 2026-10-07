from uuid import uuid4

from fastapi import (
    BackgroundTasks,
    Depends,
    FastAPI,
    HTTPException,
)

from fastapi.responses import Response

from sqlalchemy.orm import Session

from .database import (
    Base,
    SessionLocal,
    engine,
)

from .models import Job, Recipient

from .schemas import (
    CertificateResult,
    JobCreate,
    JobResponse,
)

from .service import process_job


# Create database tables if they do not exist.
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="CertiFlow API",
    description="Bulk certificate generation made simple.",
    version="1.0.0",
)


def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


@app.get("/health")
def health():

    return {
        "status": "ok",
        "service": "CertiFlow"
    }


@app.post(
    "/jobs",
    response_model=dict,
    status_code=202
)
def create_job(
    payload: JobCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):

    job_id = uuid4().hex[:10]

    job = Job(
        id=job_id,
        event_name=payload.event_name.strip(),
        event_date=payload.event_date.strip(),
        issuer=payload.issuer.strip(),
        status="queued",
        total=len(payload.recipients),
    )

    db.add(job)
    db.flush()

    for item in payload.recipients:

        db.add(
            Recipient(
                job_id=job_id,
                name=item.name.strip(),
                email=str(item.email),
                achievement=item.achievement.strip(),
                status="pending",
            )
        )

    db.commit()

    background_tasks.add_task(
        process_job,
        job_id,
        SessionLocal
    )

    return {
        "message": "Certificate generation started",
        "job_id": job_id,
        "status_url": f"/jobs/{job_id}",
    }


@app.get(
    "/jobs/{job_id}",
    response_model=JobResponse
)
def get_job(
    job_id: str,
    db: Session = Depends(get_db)
):

    job = db.get(Job, job_id)

    if not job:

        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    results = []

    for recipient in job.recipients:

        results.append(
            CertificateResult(
                recipient_id=recipient.id,
                name=recipient.name,
                status=recipient.status,

                download_url=(
                    f"/certificates/"
                    f"{recipient.id}/download"
                    if recipient.status == "success"
                    else None
                ),

                error=recipient.error_message,
            )
        )

    progress = (
        round(
            (job.completed / job.total) * 100,
            2
        )
        if job.total
        else 100.0
    )

    return JobResponse(
        job_id=job.id,
        status=job.status,
        total=job.total,
        completed=job.completed,
        successful=job.successful,
        failed=job.failed,
        progress_percent=progress,
        certificates=results,
    )


@app.get(
    "/certificates/{recipient_id}/download"
)
def download_certificate(
    recipient_id: int,
    db: Session = Depends(get_db),
):

    recipient = db.get(
        Recipient,
        recipient_id
    )

    if not recipient:

        raise HTTPException(
            status_code=404,
            detail="Certificate record not found",
        )

    if (
        recipient.status != "success"
        or not recipient.file_data
    ):

        raise HTTPException(
            status_code=409,
            detail="Certificate is not available yet",
        )

    safe_name = (
        recipient.name
        .replace(" ", "_")
    )

    filename = (
        f"{safe_name}_certificate.pdf"
    )

    return Response(
        content=recipient.file_data,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
                f'attachment; filename="{filename}"'
        },
    )

# from pathlib import Path
# from uuid import uuid4

# from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException
# from fastapi.responses import FileResponse
# from sqlalchemy.orm import Session

# from .database import Base, SessionLocal, engine
# from .models import Job, Recipient
# from .schemas import CertificateResult, JobCreate, JobResponse
# from .service import process_job

# Base.metadata.create_all(bind=engine)

# app = FastAPI(
#     title="CertiFlow API",
#     description="Bulk certificate generation made simple.",
#     version="1.0.0",
# )


# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


# @app.get("/health")
# def health():
#     return {"status": "ok", "service": "CertiFlow"}


# @app.post("/jobs", response_model=dict, status_code=202)
# def create_job(
#     payload: JobCreate,
#     background_tasks: BackgroundTasks,
#     db: Session = Depends(get_db),
# ):
#     job_id = uuid4().hex[:10]

#     job = Job(
#         id=job_id,
#         event_name=payload.event_name.strip(),
#         event_date=payload.event_date.strip(),
#         issuer=payload.issuer.strip(),
#         status="queued",
#         total=len(payload.recipients),
#     )

#     db.add(job)
#     db.flush()

#     for item in payload.recipients:
#         db.add(
#             Recipient(
#                 job_id=job_id,
#                 name=item.name.strip(),
#                 email=str(item.email),
#                 achievement=item.achievement.strip(),
#                 status="pending",
#             )
#         )

#     db.commit()

#     background_tasks.add_task(process_job, job_id, SessionLocal)

#     return {
#         "message": "Certificate generation started",
#         "job_id": job_id,
#         "status_url": f"/jobs/{job_id}",
#     }


# @app.get("/jobs/{job_id}", response_model=JobResponse)
# def get_job(job_id: str, db: Session = Depends(get_db)):
#     job = db.get(Job, job_id)

#     if not job:
#         raise HTTPException(status_code=404, detail="Job not found")

#     results = []

#     for recipient in job.recipients:
#         results.append(
#             CertificateResult(
#                 recipient_id=recipient.id,
#                 name=recipient.name,
#                 status=recipient.status,
#                 download_url=(
#                     f"/certificates/{recipient.id}/download"
#                     if recipient.status == "success"
#                     else None
#                 ),
#                 error=recipient.error_message,
#             )
#         )

#     progress = (
#         round((job.completed / job.total) * 100, 2)
#         if job.total
#         else 100.0
#     )

#     return JobResponse(
#         job_id=job.id,
#         status=job.status,
#         total=job.total,
#         completed=job.completed,
#         successful=job.successful,
#         failed=job.failed,
#         progress_percent=progress,
#         certificates=results,
#     )


# @app.get("/certificates/{recipient_id}/download")
# def download_certificate(
#     recipient_id: int,
#     db: Session = Depends(get_db),
# ):
#     recipient = db.get(Recipient, recipient_id)

#     if not recipient:
#         raise HTTPException(
#             status_code=404,
#             detail="Certificate record not found",
#         )

#     if recipient.status != "success" or not recipient.file_path:
#         raise HTTPException(
#             status_code=409,
#             detail="Certificate is not available yet",
#         )

#     path = Path(recipient.file_path)

#     if not path.exists():
#         raise HTTPException(
#             status_code=404,
#             detail="Certificate file not found",
#         )

#     safe_name = recipient.name.replace(" ", "_")

#     return FileResponse(
#         path=path,
#         media_type="application/pdf",
#         filename=f"{safe_name}_certificate.pdf",
#     )
