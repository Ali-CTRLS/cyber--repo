"""SQLAlchemy models for InjuryAssist platform."""

import enum
from datetime import datetime, timezone

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# ── Enums ────────────────────────────────────────────────────────────────────


class BodyPart(enum.Enum):
    THIGH = "Thigh"
    KNEE = "Knee"
    ANKLE = "Ankle"
    SHOULDER = "Shoulder"


class AppointmentStatus(enum.Enum):
    PENDING = "Pending"
    CONFIRMED = "Confirmed"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


# ── User model (shared auth for patients & doctors) ─────────────────────────


class User(db.Model, UserMixin):
    """Single user table with a 'role' column to distinguish patients from doctors."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="patient")  # 'patient' or 'doctor'
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    contact_no = db.Column(db.String(20))
    address = db.Column(db.String(200))

    # Doctor-specific fields (nullable for patients)
    is_available = db.Column(db.Boolean, default=True)
    availability_slot = db.Column(db.String(100))
    doctor_type = db.Column(db.String(20))        # 'general' or 'specialized'
    specialty = db.Column(db.String(100))
    certification_level = db.Column(db.String(50))
    clinic_room = db.Column(db.String(20))

    # Relationships
    injuries = db.relationship("Injury", backref="patient", lazy=True)
    patient_appointments = db.relationship(
        "Appointment", backref="patient", lazy=True, foreign_keys="Appointment.patient_id"
    )
    doctor_appointments = db.relationship(
        "Appointment", backref="doctor", lazy=True, foreign_keys="Appointment.doctor_id"
    )

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"


# ── Injury ───────────────────────────────────────────────────────────────────


class Injury(db.Model):
    __tablename__ = "injuries"

    id = db.Column(db.Integer, primary_key=True)
    body_part = db.Column(db.Enum(BodyPart), nullable=False)
    athlete_description = db.Column(db.Text, nullable=False)
    is_critical = db.Column(db.Boolean, default=False)
    recommendation = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    patient_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    def __repr__(self):
        return f"<Injury {self.body_part.value} - Patient #{self.patient_id}>"


# ── Appointment ──────────────────────────────────────────────────────────────


class Appointment(db.Model):
    __tablename__ = "appointments"

    id = db.Column(db.Integer, primary_key=True)
    appointment_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.Enum(AppointmentStatus), default=AppointmentStatus.PENDING, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    patient_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # Relationship to report
    report = db.relationship("Report", backref="appointment", uselist=False, lazy=True)

    def __repr__(self):
        return f"<Appointment #{self.id} - {self.status.value}>"


# ── Report ───────────────────────────────────────────────────────────────────


class Report(db.Model):
    __tablename__ = "reports"

    id = db.Column(db.Integer, primary_key=True)
    diagnosis = db.Column(db.Text, nullable=False)
    treatment_plan = db.Column(db.Text, nullable=False)
    generated_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    encrypted_file_path = db.Column(db.String(300))
    encryption_key = db.Column(db.String(100))  # base64-encoded AES key
    original_filename = db.Column(db.String(255))
    original_mimetype = db.Column(db.String(100))
    appointment_id = db.Column(db.Integer, db.ForeignKey("appointments.id"), nullable=False)

    def __repr__(self):
        return f"<Report #{self.id} for Appointment #{self.appointment_id}>"
