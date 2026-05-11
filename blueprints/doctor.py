"""Doctor blueprint — dashboard and appointment actions."""

from flask import Blueprint, render_template, abort, redirect, url_for, flash
from flask_login import login_required, current_user

from forms import AppointmentActionForm
from models import Appointment, AppointmentStatus, Injury, db

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

    action_form = AppointmentActionForm()
    return render_template("doctor/dashboard.html", appointments=appointments, action_form=action_form)


def _get_doctor_appointment(appointment_id):
    appointment = Appointment.query.filter_by(id=appointment_id, doctor_id=current_user.id).first()
    if not appointment:
        abort(404)
    return appointment


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

    appointment.status = AppointmentStatus.CANCELLED
    db.session.commit()
    flash("Appointment cancelled.", "success")
    return redirect(url_for("doctor.appointment_detail", appointment_id=appointment.id))
