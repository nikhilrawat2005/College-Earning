from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Optional

class SignupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    full_name = StringField('Full Name', validators=[DataRequired(), Length(max=100)])
    college_name = StringField('College Name', validators=[DataRequired(), Length(max=100)])
    year = StringField('Year', validators=[DataRequired(), Length(max=20)])               # e.g., "1st Year"
    class_name = StringField('Class (Program)', validators=[DataRequired(), Length(max=20)])  # e.g., "Computer Science"
    section = StringField('Section', validators=[DataRequired(), Length(max=10)])         # e.g., "A"
    phone_number = StringField('Phone Number', validators=[DataRequired(), Length(max=20)])
    short_bio = TextAreaField('Short Bio', validators=[Length(max=500)])
    is_worker = BooleanField('I want to offer my skills')
    skills = TextAreaField('Skills (comma separated)', validators=[Optional(), Length(max=500)])

    def validate_skills(form, field):
        if form.is_worker.data and not field.data:
            raise ValidationError('Please list your skills.')


class LoginForm(FlaskForm):
    login_input = StringField('Username or Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])


class VerifyForm(FlaskForm):
    code = StringField('Verification Code', validators=[DataRequired(), Length(min=6, max=6)])


class EditProfileForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(max=100)])
    college_name = StringField('College Name', validators=[DataRequired(), Length(max=100)])
    year = StringField('Year', validators=[DataRequired(), Length(max=20)])
    class_name = StringField('Class (Program)', validators=[DataRequired(), Length(max=20)])
    section = StringField('Section', validators=[DataRequired(), Length(max=10)])
    phone_number = StringField('Phone Number', validators=[DataRequired(), Length(max=20)])
    short_bio = TextAreaField('Short Bio', validators=[Length(max=500)])
    is_worker = BooleanField('I offer my skills')
    skills = TextAreaField('Skills (comma separated)', validators=[Optional(), Length(max=500)])

    def validate_skills(form, field):
        if form.is_worker.data and not field.data:
            raise ValidationError('Please list your skills.')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('new_password')])