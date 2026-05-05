"""Patient blueprint — dashboard and injury management."""

from flask import Blueprint, render_template
from flask_login import login_required, current_user

from models import Injury, Appointment, Report

patient_bp = Blueprint("patient", __name__, url_prefix="/patient")


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
