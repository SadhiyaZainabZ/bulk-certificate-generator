from pydantic import BaseModel, EmailStr, Field


class RecipientInput(BaseModel):
    name: str = Field(..., min_length=2, max_length=80)
    email: EmailStr
    achievement: str = Field(..., min_length=5, max_length=300)


class JobCreate(BaseModel):
    event_name: str = Field(..., min_length=2, max_length=120)
    event_date: str = Field(..., min_length=2, max_length=60)
    issuer: str = Field(..., min_length=2, max_length=100)
    recipients: list[RecipientInput] = Field(..., min_length=1, max_length=1000)


class CertificateResult(BaseModel):
    recipient_id: int
    name: str
    status: str
    download_url: str | None = None
    error: str | None = None


class JobResponse(BaseModel):
    job_id: str
    status: str
    total: int
    completed: int
    successful: int
    failed: int
    progress_percent: float
    certificates: list[CertificateResult]
