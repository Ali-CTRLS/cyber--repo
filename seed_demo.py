"""Seed demo data for InjuryAssist."""

from datetime import datetime, timedelta

from werkzeug.security import generate_password_hash

from app import create_app
from models import db, User, Injury, Appointment, Report, BodyPart, AppointmentStatus


def _get_or_create_patient(username, name, age, gender, contact_no, address):
    patient = User.query.filter_by(username=username).first()
    if patient:
        return patient, False

    patient = User(
        username=username,
        password_hash=generate_password_hash("patient123"),
        name=name,
        role="patient",
        age=age,
        gender=gender,
        contact_no=contact_no,
        address=address,
    )
    db.session.add(patient)
    return patient, True


def _seed_injuries(patient):
    if Injury.query.filter_by(patient_id=patient.id).count() > 0:
        return False

    injuries = [
        Injury(
            body_part=BodyPart.KNEE,
            athlete_description="Pain after running for 30 minutes.",
            is_critical=False,
            recommendation="Rest and apply cold compress.",
            patient_id=patient.id,
        ),
        Injury(
            body_part=BodyPart.SHOULDER,
            athlete_description="Sharp pain while lifting weights.",
            is_critical=True,
            recommendation="Avoid lifting and schedule assessment.",
            patient_id=patient.id,
        ),
    ]

    db.session.add_all(injuries)
    return True


def _seed_appointments(patient, doctors):
    if Appointment.query.filter_by(patient_id=patient.id).count() > 0:
        return False

    doctor_primary = doctors[0]
    doctor_secondary = doctors[1] if len(doctors) > 1 else doctors[0]
    now = datetime.now()

    pending = Appointment(
        appointment_date=now + timedelta(days=3, hours=2),
        status=AppointmentStatus.PENDING,
        patient_id=patient.id,
        doctor_id=doctor_primary.id,
    )
    confirmed = Appointment(
        appointment_date=now + timedelta(days=6, hours=1),
        status=AppointmentStatus.CONFIRMED,
        patient_id=patient.id,
        doctor_id=doctor_secondary.id,
    )
    completed = Appointment(
        appointment_date=now - timedelta(days=2),
        status=AppointmentStatus.COMPLETED,
        patient_id=patient.id,
        doctor_id=doctor_primary.id,
    )

    db.session.add_all([pending, confirmed, completed])
    db.session.flush()

    report = Report(
        diagnosis="Mild strain with no structural damage.",
        treatment_plan="Rest, ice, and follow up in one week.",
        appointment_id=completed.id,
    )
    db.session.add(report)
    return True


def seed_demo_data():
    app = create_app()
    with app.app_context():
        doctors = User.query.filter_by(role="doctor").order_by(User.id.asc()).all()
        if not doctors:
            print("No doctors found. Start the app once to seed doctors.")
            return

        made_changes = False

        patient_one, created_one = _get_or_create_patient(
            username="patient.ali",
            name="Ali Saeed",
            age=24,
            gender="Male",
            contact_no="0502223344",
            address="Student Housing 12",
        )
        patient_two, created_two = _get_or_create_patient(
            username="patient.mona",
            name="Mona Kareem",
            age=29,
            gender="Female",
            contact_no="0505556677",
            address="City Center 8",
        )

        made_changes = made_changes or created_one or created_two
        made_changes = made_changes or _seed_injuries(patient_one)
        made_changes = made_changes or _seed_injuries(patient_two)
        made_changes = made_changes or _seed_appointments(patient_one, doctors)
        made_changes = made_changes or _seed_appointments(patient_two, doctors)

        if made_changes:
            db.session.commit()
            print("Seeded demo patients, injuries, appointments, and reports.")
        else:
            print("Demo data already exists. No changes made.")


if __name__ == "__main__":
    seed_demo_data()
