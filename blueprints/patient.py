"""Patient blueprint — dashboard and injury management."""

import io
from datetime import datetime, timedelta, time
from typing import Optional

from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file, abort
from flask_login import login_required, current_user

from encryption import decrypt_file
from forms import InjuryForm, InjuryCriticalForm, AppointmentForm, AppointmentActionForm
from models import Injury, Appointment, AppointmentStatus, Report, BodyPart, User, db

patient_bp = Blueprint("patient", __name__, url_prefix="/patient")

BODY_PART_TO_SPECIALTY = {
    BodyPart.THIGH: "Orthopedic - Lower Limb",
    BodyPart.KNEE: "Orthopedic - Knee Specialist",
    BodyPart.ANKLE: "Orthopedic - Foot & Ankle",
    BodyPart.SHOULDER: "Orthopedic - Upper Limb",
}

DAY_TO_INDEX = {
    "Mon": 0,
    "Tue": 1,
    "Wed": 2,
    "Thu": 3,
    "Fri": 4,
    "Sat": 5,
    "Sun": 6,
}


def _parse_time(value: str) -> Optional[time]:
    parts = value.split(":")
    if len(parts) != 2:
        return None
    try:
        return time(hour=int(parts[0]), minute=int(parts[1]))
    except ValueError:
        return None


def _parse_availability_slot(slot_text: str):
    if not slot_text:
        return None

    parts = slot_text.split()
    if len(parts) < 2:
        return None

    day_part = parts[0].strip()
    time_part = parts[1].strip()

    if "-" in day_part:
        start_day, end_day = day_part.split("-", 1)
    else:
        start_day = end_day = day_part

    if "-" not in time_part:
        return None

    start_time, end_time = time_part.split("-", 1)
    if start_day not in DAY_TO_INDEX or end_day not in DAY_TO_INDEX:
        return None

    start_clock = _parse_time(start_time)
    end_clock = _parse_time(end_time)
    if not start_clock or not end_clock:
        return None

    return start_day, end_day, start_clock, end_clock


def _day_in_range(day_idx: int, start_idx: int, end_idx: int) -> bool:
    if start_idx <= end_idx:
        return start_idx <= day_idx <= end_idx
    return day_idx >= start_idx or day_idx <= end_idx


def _build_available_slots(slot_text: str, days_ahead: int = 21, interval_minutes: int = 30):
    parsed = _parse_availability_slot(slot_text)
    if not parsed:
        return []

    start_day, end_day, start_clock, end_clock = parsed
    start_idx = DAY_TO_INDEX[start_day]
    end_idx = DAY_TO_INDEX[end_day]

    if (end_clock.hour, end_clock.minute) <= (start_clock.hour, start_clock.minute):
        return []

    now = datetime.now()
    slots = []
    for offset in range(days_ahead):
        day_date = now.date() + timedelta(days=offset)
        if not _day_in_range(day_date.weekday(), start_idx, end_idx):
            continue

        start_dt = datetime.combine(day_date, start_clock)
        end_dt = datetime.combine(day_date, end_clock)
        current = start_dt
        while current < end_dt:
            if current >= now + timedelta(minutes=15):
                slots.append(current)
            current += timedelta(minutes=interval_minutes)

    return slots


def _cancel_allowed(appointment) -> bool:
    if appointment.status in (AppointmentStatus.CANCELLED, AppointmentStatus.COMPLETED):
        return False

    now = datetime.now()
    return appointment.appointment_date > now + timedelta(hours=24)


@patient_bp.route("/dashboard")
@login_required
def dashboard():
    if current_user.role != "patient":
        abort(403)

    injuries = Injury.query.filter_by(patient_id=current_user.id).order_by(Injury.created_at.desc()).all()
    appointments = Appointment.query.filter_by(patient_id=current_user.id).order_by(Appointment.created_at.desc()).all()
    report_count = (
        Report.query.join(Appointment).filter(Appointment.patient_id == current_user.id).count()
    )

    return render_template(
        "patient/dashboard.html",
        injuries=injuries,
        appointments=appointments,
        report_count=report_count,
    )


@patient_bp.route("/injury/new", methods=["GET", "POST"])
@login_required
def new_injury():
    if current_user.role != "patient":
        abort(403)

    form = InjuryForm()
    if form.validate_on_submit():
        body_part = BodyPart[form.body_part.data]
        recommendation = BODY_PART_TO_SPECIALTY.get(body_part)

        injury = Injury(
            body_part=body_part,
            athlete_description=form.athlete_description.data,
            is_critical=form.is_critical.data,
            recommendation=recommendation,
            patient_id=current_user.id,
        )
        db.session.add(injury)
        db.session.commit()

        flash("Injury submitted successfully.", "success")
        return redirect(url_for("patient.doctors", body_part=body_part.name))

    return render_template("patient/injury_form.html", form=form)


@patient_bp.route("/injury/<int:injury_id>/edit", methods=["GET", "POST"])
@login_required
def edit_injury(injury_id):
    if current_user.role != "patient":
        abort(403)

    injury = Injury.query.filter_by(id=injury_id, patient_id=current_user.id).first()
    if not injury:
        abort(404)

    form = InjuryCriticalForm(is_critical=injury.is_critical)
    if form.validate_on_submit():
        injury.is_critical = form.is_critical.data
        db.session.commit()
        flash("Injury updated successfully.", "success")
        return redirect(url_for("patient.dashboard"))

    return render_template("patient/injury_edit.html", form=form, injury=injury)


@patient_bp.route("/doctors")
@login_required
def doctors():
    if current_user.role != "patient":
        abort(403)

    body_part_key = request.args.get("body_part")
    selected_body_part = None
    specialty_filter = None

    if body_part_key:
        try:
            selected_body_part = BodyPart[body_part_key]
            specialty_filter = BODY_PART_TO_SPECIALTY.get(selected_body_part)
        except KeyError:
            selected_body_part = None

    query = User.query.filter_by(role="doctor", is_available=True)
    if specialty_filter:
        query = query.filter(User.specialty == specialty_filter)

    doctors = query.order_by(User.name.asc()).all()

    return render_template(
        "patient/doctors.html",
        doctors=doctors,
        selected_body_part=selected_body_part,
        specialty_filter=specialty_filter,
    )


@patient_bp.route("/appointment/book/<int:doctor_id>", methods=["GET", "POST"])
@login_required
def book_appointment(doctor_id):
    if current_user.role != "patient":
        from flask import abort
        abort(403)

    doctor = User.query.filter_by(id=doctor_id, role="doctor").first()
    if not doctor:
        abort(404)

    slots = _build_available_slots(doctor.availability_slot)
    slot_choices = [("", "Select a time...")]
    slot_choices += [
        (slot.strftime("%Y-%m-%dT%H:%M"), slot.strftime("%a, %b %d • %I:%M %p"))
        for slot in slots
    ]

    form = AppointmentForm()
    form.appointment_slot.choices = slot_choices

    if form.validate_on_submit():
        allowed_values = {value for value, _ in slot_choices if value}
        selected_value = form.appointment_slot.data
        if selected_value not in allowed_values:
            flash("Selected time is not available. Please choose another slot.", "error")
            return redirect(request.url)

        selected_dt = datetime.strptime(selected_value, "%Y-%m-%dT%H:%M")
        appointment = Appointment(
            appointment_date=selected_dt,
            patient_id=current_user.id,
            doctor_id=doctor.id,
        )
        db.session.add(appointment)
        db.session.commit()

        flash("Appointment request sent.", "success")
        return redirect(url_for("patient.appointments"))

    return render_template(
        "patient/appointment_book.html",
        form=form,
        doctor=doctor,
        has_slots=bool(slots),
        slot_window_days=21,
        slot_interval_minutes=30,
    )


@patient_bp.route("/appointments")
@login_required
def appointments():
    if current_user.role != "patient":
        abort(403)

    appointments = (
        Appointment.query.filter_by(patient_id=current_user.id)
        .order_by(Appointment.appointment_date.desc())
        .all()
    )

    cancel_allowed = {appt.id: _cancel_allowed(appt) for appt in appointments}
    action_form = AppointmentActionForm()
    return render_template(
        "patient/appointments.html",
        appointments=appointments,
        cancel_allowed=cancel_allowed,
        action_form=action_form,
    )


@patient_bp.route("/appointment/<int:appointment_id>/cancel", methods=["POST"])
@login_required
def cancel_appointment(appointment_id):
    if current_user.role != "patient":
        abort(403)

    form = AppointmentActionForm()
    if not form.validate_on_submit():
        abort(400)

    appointment = Appointment.query.filter_by(id=appointment_id, patient_id=current_user.id).first()
    if not appointment:
        abort(404)

    if appointment.status == AppointmentStatus.CANCELLED:
        flash("Appointment is already cancelled.", "warning")
        return redirect(url_for("patient.appointments"))

    if appointment.status == AppointmentStatus.COMPLETED:
        flash("Completed appointments cannot be cancelled.", "warning")
        return redirect(url_for("patient.appointments"))

    if not _cancel_allowed(appointment):
        flash("Cancellations must be at least 24 hours before the appointment.", "error")
        return redirect(url_for("patient.appointments"))

    appointment.status = AppointmentStatus.CANCELLED
    db.session.commit()
    flash("Appointment cancelled.", "success")
    return redirect(url_for("patient.appointments"))


@patient_bp.route("/report/<int:report_id>")
@login_required
def report_view(report_id):
    if current_user.role != "patient":
        abort(403)

    report = Report.query.get_or_404(report_id)
    if report.appointment.patient_id != current_user.id:
        abort(403)

    return render_template("patient/report_view.html", report=report)


@patient_bp.route("/report/<int:report_id>/download")
@login_required
def report_download(report_id):
    if current_user.role != "patient":
        abort(403)

    report = Report.query.get_or_404(report_id)
    if report.appointment.patient_id != current_user.id:
        abort(403)

    if not report.encrypted_file_path:
        flash("No file was attached to this report.", "warning")
        return redirect(url_for("patient.report_view", report_id=report.id))

    with open(report.encrypted_file_path, "rb") as encrypted_file:
        decrypted_bytes = decrypt_file(encrypted_file.read(), report.encryption_key)

    return send_file(
        io.BytesIO(decrypted_bytes),
        as_attachment=True,
        download_name=f"report_{report.id}.bin",
        mimetype="application/octet-stream",
    )
