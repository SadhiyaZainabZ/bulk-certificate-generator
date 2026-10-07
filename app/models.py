from sqlalchemy import Column, Integer, String, Text, ForeignKey, LargeBinary
from sqlalchemy.orm import relationship

from .database import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(String, primary_key=True)
    event_name = Column(String, nullable=False)
    event_date = Column(String, nullable=False)
    issuer = Column(String, nullable=False)

    status = Column(String, default="queued", nullable=False)

    total = Column(Integer, default=0)
    completed = Column(Integer, default=0)
    successful = Column(Integer, default=0)
    failed = Column(Integer, default=0)

    recipients = relationship(
        "Recipient",
        back_populates="job",
        cascade="all, delete-orphan",
    )


class Recipient(Base):
    __tablename__ = "recipients"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    job_id = Column(
        String,
        ForeignKey("jobs.id"),
        nullable=False
    )

    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    achievement = Column(Text, nullable=False)

    status = Column(
        String,
        default="pending",
        nullable=False
    )

    # Keeps the old field so the existing tests continue to work.
    # The actual downloadable PDF is stored in file_data.
    file_path = Column(String, nullable=True)

    # PDF bytes stored directly in PostgreSQL/SQLite.
    file_data = Column(LargeBinary, nullable=True)

    file_name = Column(String, nullable=True)

    error_message = Column(Text, nullable=True)

    job = relationship(
        "Job",
        back_populates="recipients"
    )


# from sqlalchemy import Column, Integer, String, Text, ForeignKey
# from sqlalchemy.orm import relationship
# from .database import Base


# class Job(Base):
#     __tablename__ = "jobs"

#     id = Column(String, primary_key=True)
#     event_name = Column(String, nullable=False)
#     event_date = Column(String, nullable=False)
#     issuer = Column(String, nullable=False)
#     status = Column(String, default="queued", nullable=False)
#     total = Column(Integer, default=0)
#     completed = Column(Integer, default=0)
#     successful = Column(Integer, default=0)
#     failed = Column(Integer, default=0)

#     recipients = relationship(
#         "Recipient",
#         back_populates="job",
#         cascade="all, delete-orphan",
#     )


# class Recipient(Base):
#     __tablename__ = "recipients"

#     id = Column(Integer, primary_key=True, autoincrement=True)
#     job_id = Column(String, ForeignKey("jobs.id"), nullable=False)
#     name = Column(String, nullable=False)
#     email = Column(String, nullable=False)
#     achievement = Column(Text, nullable=False)
#     status = Column(String, default="pending", nullable=False)
#     file_path = Column(String, nullable=True)
#     error_message = Column(Text, nullable=True)

#     job = relationship("Job", back_populates="recipients")
