"""InjuryAssist — Flask application entry point."""

import os

from flask import Flask, redirect, url_for
from flask_login import LoginManager
from werkzeug.security import generate_password_hash

from config import Config
from models import db, User


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Ensure folders exist
    os.makedirs(os.path.join(app.instance_path), exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Init extensions
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "error"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Register blueprints
    from blueprints.auth import auth_bp
    from blueprints.patient import patient_bp
    from blueprints.doctor import doctor_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(patient_bp)
    app.register_blueprint(doctor_bp)

    # Root redirect
    @app.route("/")
    def index():
        return redirect(url_for("auth.login"))

    # Create tables and seed doctors on first run
    with app.app_context():
        db.create_all()
        _seed_doctors()

    return app


def _seed_doctors():
    """Seed the database with sample doctors if none exist."""
    if User.query.filter_by(role="doctor").count() > 0:
        return

    doctors = [
        {
            "username": "dr.ahmed",
            "password_hash": generate_password_hash("doctor123"),
            "name": "Dr. Ahmed Hassan",
            "role": "doctor",
            "age": 45,
            "gender": "Male",
            "contact_no": "0501234567",
            "address": "Building A, Room 101",
            "is_available": True,
            "availability_slot": "Sun-Wed 9:00-14:00",
            "doctor_type": "specialized",
            "specialty": "Orthopedic - Knee Specialist",
            "certification_level": "Senior Consultant",
            "clinic_room": "A-101",
        },
        {
            "username": "dr.sara",
            "password_hash": generate_password_hash("doctor123"),
            "name": "Dr. Sara Ali",
            "role": "doctor",
            "age": 38,
            "gender": "Female",
            "contact_no": "0509876543",
            "address": "Building B, Room 205",
            "is_available": True,
            "availability_slot": "Mon-Thu 10:00-16:00",
            "doctor_type": "specialized",
            "specialty": "Orthopedic - Lower Limb",
            "certification_level": "Consultant",
            "clinic_room": "B-205",
        },
        {
            "username": "dr.omar",
            "password_hash": generate_password_hash("doctor123"),
            "name": "Dr. Omar Khalid",
            "role": "doctor",
            "age": 50,
            "gender": "Male",
            "contact_no": "0551112233",
            "address": "Building A, Room 303",
            "is_available": True,
            "availability_slot": "Sat-Wed 8:00-13:00",
            "doctor_type": "general",
            "specialty": "General Orthopedics",
            "certification_level": "Senior Consultant",
            "clinic_room": "A-303",
        },
        {
            "username": "dr.nora",
            "password_hash": generate_password_hash("doctor123"),
            "name": "Dr. Nora Yusuf",
            "role": "doctor",
            "age": 35,
            "gender": "Female",
            "contact_no": "0554445566",
            "address": "Building C, Room 102",
            "is_available": True,
            "availability_slot": "Sun-Thu 11:00-17:00",
            "doctor_type": "specialized",
            "specialty": "Orthopedic - Upper Limb",
            "certification_level": "Consultant",
            "clinic_room": "C-102",
        },
        {
            "username": "dr.khaled",
            "password_hash": generate_password_hash("doctor123"),
            "name": "Dr. Khaled Mostafa",
            "role": "doctor",
            "age": 42,
            "gender": "Male",
            "contact_no": "0507778899",
            "address": "Building B, Room 110",
            "is_available": True,
            "availability_slot": "Sat-Tue 9:00-15:00",
            "doctor_type": "specialized",
            "specialty": "Orthopedic - Foot & Ankle",
            "certification_level": "Associate Consultant",
            "clinic_room": "B-110",
        },
    ]

    for doc_data in doctors:
        db.session.add(User(**doc_data))

    db.session.commit()
    print(f"[SEED] Created {len(doctors)} sample doctors.")


# Run the app
if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
