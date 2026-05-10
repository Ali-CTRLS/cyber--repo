"""Patient blueprint — dashboard and injury management."""

from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from forms import InjuryForm
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
        from flask import abort
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
        from flask import abort
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
        return redirect(url_for("patient.doctors"))

    return render_template("patient/injury_form.html", form=form)


@patient_bp.route("/doctors")
@login_required
def doctors():
    if current_user.role != "patient":
        from flask import abort
        abort(403)

    doctors = (
        User.query.filter_by(role="doctor", is_available=True)
        .order_by(User.name.asc())
        .all()
    )

    return render_template("patient/doctors.html", doctors=doctors)
