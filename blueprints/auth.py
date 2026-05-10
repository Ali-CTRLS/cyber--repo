"""Authentication blueprint — login, register, logout."""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from models import db, User
from forms import LoginForm, RegisterForm

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return _redirect_by_role(current_user)

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash(f"Welcome back, {user.name}!", "success")
            return _redirect_by_role(user)
        flash("Invalid username or password.", "error")

    return render_template("auth/login.html", form=form)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return _redirect_by_role(current_user)

    form = RegisterForm()
    if form.validate_on_submit():
        # Check if username already exists
        if User.query.filter_by(username=form.username.data).first():
            flash("Username already taken. Please choose another.", "error")
            return render_template("auth/register.html", form=form)

        user = User(
            username=form.username.data,
            password_hash=generate_password_hash(form.password.data),
            name=form.name.data,
            role="patient",
            age=form.age.data,
            gender=form.gender.data if form.gender.data else None,
            contact_no=form.contact_no.data,
            address=form.address.data,
        )
        db.session.add(user)
        db.session.commit()
        flash("Account created successfully! Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("auth.login"))


def _redirect_by_role(user):
    """Redirect user to the correct dashboard based on their role."""
    if user.role == "doctor":
        return redirect(url_for("doctor.dashboard"))
    return redirect(url_for("patient.dashboard"))
