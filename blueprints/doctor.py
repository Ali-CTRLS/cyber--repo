"""Doctor blueprint — dashboard stub."""

from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user

from models import Appointment

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

    return render_template("doctor/dashboard.html", appointments=appointments)
