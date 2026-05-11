"""Patient blueprint — dashboard and injury management."""

import io

from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file, abort
from flask_login import login_required, current_user

from encryption import decrypt_file
from forms import InjuryForm, AppointmentForm
from models import Injury, Appointment, Report, BodyPart, User, db

patient_bp = Blueprint("patient", __name__, url_prefix="/patient")

BODY_PART_TO_SPECIALTY = {
    BodyPart.THIGH: "Orthopedic - Lower Limb",
    BodyPart.KNEE: "Orthopedic - Knee Specialist",
    BodyPart.ANKLE: "Orthopedic - Foot & Ankle",
    BodyPart.SHOULDER: "Orthopedic - Upper Limb",
}


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

    form = AppointmentForm()
    if form.validate_on_submit():
        appointment = Appointment(
            appointment_date=form.appointment_date.data,
            patient_id=current_user.id,
            doctor_id=doctor.id,
        )
        db.session.add(appointment)
        db.session.commit()

        flash("Appointment request sent.", "success")
        return redirect(url_for("patient.appointments"))

    return render_template("patient/appointment_book.html", form=form, doctor=doctor)


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

    return render_template("patient/appointments.html", appointments=appointments)


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
