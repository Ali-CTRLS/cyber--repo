"""Doctor blueprint — dashboard and appointment actions."""

import os
import uuid
from datetime import datetime, timedelta

from flask import Blueprint, render_template, abort, redirect, url_for, flash, current_app
from flask_login import login_required, current_user

from encryption import generate_key, encrypt_file
from forms import AppointmentActionForm, ReportForm
from models import Appointment, AppointmentStatus, Injury, Report, db

doctor_bp = Blueprint("doctor", __name__, url_prefix="/doctor")


@doctor_bp.route("/dashboard")
@login_required
def dashboard():
    if current_user.role != "doctor":
        abort(403)

    appointments = (
        Appointment.query.filter_by(doctor_id=current_user.id)
        .order_by(Appointment.created_at.desc())
        .all()
    )

    cancel_allowed = {appt.id: _cancel_allowed(appt) for appt in appointments}
    action_form = AppointmentActionForm()
    return render_template(
        "doctor/dashboard.html",
        appointments=appointments,
        action_form=action_form,
        cancel_allowed=cancel_allowed,
    )


def _get_doctor_appointment(appointment_id):
    appointment = Appointment.query.filter_by(id=appointment_id, doctor_id=current_user.id).first()
    if not appointment:
        abort(404)
    return appointment


def _cancel_allowed(appointment) -> bool:
    if appointment.status in (AppointmentStatus.CANCELLED, AppointmentStatus.COMPLETED):
        return False

    now = datetime.now()
    return appointment.appointment_date > now + timedelta(hours=24)


@doctor_bp.route("/appointment/<int:appointment_id>")
@login_required
def appointment_detail(appointment_id):
    if current_user.role != "doctor":
        abort(403)

    appointment = _get_doctor_appointment(appointment_id)
    latest_injury = (
        Injury.query.filter_by(patient_id=appointment.patient_id)
        .order_by(Injury.created_at.desc())
        .first()
    )

    action_form = AppointmentActionForm()
    return render_template(
        "doctor/appointment_detail.html",
        appointment=appointment,
        latest_injury=latest_injury,
        action_form=action_form,
        cancel_allowed=_cancel_allowed(appointment),
    )


@doctor_bp.route("/appointment/<int:appointment_id>/confirm", methods=["POST"])
@login_required
def confirm_appointment(appointment_id):
    if current_user.role != "doctor":
        abort(403)

    form = AppointmentActionForm()
    if not form.validate_on_submit():
        abort(400)

    appointment = _get_doctor_appointment(appointment_id)
    if appointment.status != AppointmentStatus.PENDING:
        flash("Only pending appointments can be confirmed.", "warning")
        return redirect(url_for("doctor.appointment_detail", appointment_id=appointment.id))

    appointment.status = AppointmentStatus.CONFIRMED
    db.session.commit()
    flash("Appointment confirmed.", "success")
    return redirect(url_for("doctor.appointment_detail", appointment_id=appointment.id))


@doctor_bp.route("/appointment/<int:appointment_id>/cancel", methods=["POST"])
@login_required
def cancel_appointment(appointment_id):
    if current_user.role != "doctor":
        abort(403)

    form = AppointmentActionForm()
    if not form.validate_on_submit():
        abort(400)

    appointment = _get_doctor_appointment(appointment_id)
    if appointment.status == AppointmentStatus.CANCELLED:
        flash("Appointment is already cancelled.", "warning")
        return redirect(url_for("doctor.appointment_detail", appointment_id=appointment.id))

    if appointment.status == AppointmentStatus.COMPLETED:
        flash("Completed appointments cannot be cancelled.", "warning")
        return redirect(url_for("doctor.appointment_detail", appointment_id=appointment.id))

    if not _cancel_allowed(appointment):
        flash("Cancellations must be at least 24 hours before the appointment.", "error")
        return redirect(url_for("doctor.appointment_detail", appointment_id=appointment.id))

    appointment.status = AppointmentStatus.CANCELLED
    db.session.commit()
    flash("Appointment cancelled.", "success")
    return redirect(url_for("doctor.appointment_detail", appointment_id=appointment.id))


@doctor_bp.route("/appointment/<int:appointment_id>/report", methods=["GET", "POST"])
@login_required
def create_report(appointment_id):
    if current_user.role != "doctor":
        abort(403)

    appointment = _get_doctor_appointment(appointment_id)
    if appointment.report:
        flash("A report already exists for this appointment.", "warning")
        return redirect(url_for("doctor.appointment_detail", appointment_id=appointment.id))

    if appointment.status != AppointmentStatus.CONFIRMED:
        flash("Confirm the appointment before writing a report.", "warning")
        return redirect(url_for("doctor.appointment_detail", appointment_id=appointment.id))

    form = ReportForm()
    if form.validate_on_submit():
        encrypted_path = None
        encryption_key = generate_key()

        uploaded_file = form.report_file.data
        if uploaded_file and uploaded_file.filename:
            encrypted_name = f"{uuid.uuid4().hex}.enc"
            encrypted_path = os.path.join(current_app.config["UPLOAD_FOLDER"], encrypted_name)

            encrypted_bytes = encrypt_file(uploaded_file.read(), encryption_key)
            with open(encrypted_path, "wb") as encrypted_file:
                encrypted_file.write(encrypted_bytes)

        report = Report(
            diagnosis=form.diagnosis.data,
            treatment_plan=form.treatment_plan.data,
            encrypted_file_path=encrypted_path,
            encryption_key=encryption_key,
            appointment_id=appointment.id,
        )
        db.session.add(report)
        appointment.status = AppointmentStatus.COMPLETED
        db.session.commit()

        flash("Report saved and appointment completed.", "success")
        return redirect(url_for("doctor.appointment_detail", appointment_id=appointment.id))

    return render_template("doctor/report_form.html", form=form, appointment=appointment)
