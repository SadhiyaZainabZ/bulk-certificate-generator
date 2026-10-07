from sqlalchemy.orm import Session
from .certificate import create_certificate
from .models import Job, Recipient


def process_job(job_id, database_factory):
    db: Session = database_factory()

    try:
        job = db.get(Job, job_id)
        if not job:
            return

        job.status = "processing"
        db.commit()

        recipients = (
            db.query(Recipient)
            .filter(Recipient.job_id == job_id)
            .order_by(Recipient.id)
            .all()
        )

        for recipient in recipients:
            try:
                if not recipient.name.strip():
                    raise ValueError("Recipient name cannot be empty.")

                path = create_certificate(
                    recipient_name=recipient.name,
                    achievement=recipient.achievement,
                    event_name=job.event_name,
                    event_date=job.event_date,
                    issuer=job.issuer,
                    recipient_id=recipient.id,
                )

                recipient.status = "success"
                recipient.file_path = path
                recipient.error_message = None
                job.successful += 1

            except Exception as exc:
                recipient.status = "failed"
                recipient.error_message = str(exc)
                job.failed += 1

            finally:
                job.completed += 1
                db.commit()

        job.status = (
            "completed"
            if job.failed == 0
            else "completed_with_errors"
        )
        db.commit()

    finally:
        db.close()
