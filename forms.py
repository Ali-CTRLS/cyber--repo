"""Flask-WTF form classes for InjuryAssist."""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, IntegerField, TextAreaField, BooleanField
from wtforms.fields import FileField
from wtforms.validators import DataRequired, Length, EqualTo, Optional


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=4)])


class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=4)])
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password", message="Passwords must match")]
    )
    name = StringField("Full Name", validators=[DataRequired(), Length(max=120)])
    age = IntegerField("Age", validators=[Optional()])
    gender = SelectField("Gender", choices=[("", "Select..."), ("Male", "Male"), ("Female", "Female")], validators=[Optional()])
    contact_no = StringField("Contact Number", validators=[Optional(), Length(max=20)])
    address = TextAreaField("Address", validators=[Optional(), Length(max=200)])


class InjuryForm(FlaskForm):
    body_part = SelectField(
        "Body Part",
        choices=[("", "Select body part..."), ("THIGH", "Thigh"), ("KNEE", "Knee"), ("ANKLE", "Ankle"), ("SHOULDER", "Shoulder")],
        validators=[DataRequired()],
    )
    athlete_description = TextAreaField("Describe your injury", validators=[DataRequired(), Length(min=10, max=1000)])
    is_critical = BooleanField("This is a critical/severe injury")


class InjuryCriticalForm(FlaskForm):
    is_critical = BooleanField("This is a critical/severe injury")


class AppointmentForm(FlaskForm):
    appointment_slot = SelectField("Appointment Time", validators=[DataRequired()])


class AppointmentActionForm(FlaskForm):
    """CSRF-protected empty form for simple appointment actions."""

    pass


class ReportForm(FlaskForm):
    diagnosis = TextAreaField("Diagnosis", validators=[DataRequired(), Length(min=10, max=2000)])
    treatment_plan = TextAreaField("Treatment Plan", validators=[DataRequired(), Length(min=10, max=2000)])
    report_file = FileField("Attach Report File (optional)", validators=[Optional()])
