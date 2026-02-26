# app/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Optional

class SignupForm(FlaskForm):
    # Order: Full Name, College, Year, Branch, Section, then rest
    full_name = StringField('Full Name', validators=[DataRequired(), Length(max=100)])
    college_name = SelectField('College', choices=[('ABES Engineering College', 'ABES Engineering College')],
                               validators=[DataRequired()])
    year = SelectField('Year', choices=[
        ('First Year', 'First Year'),
        ('Second Year', 'Second Year'),
        ('Third Year', 'Third Year'),
        ('Fourth Year', 'Fourth Year')
    ], validators=[DataRequired()])
    class_name = SelectField('Branch', choices=[
        ('CSE', 'CSE'),
        ('CSE (AIML)', 'CSE (AIML)'),
        ('ME', 'ME'),
        ('CS', 'CS'),
        ('ECE', 'ECE'),
        ('CSE (DS)', 'CSE (DS)')
    ], validators=[DataRequired()])
    section = StringField('Section', validators=[DataRequired()])

    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    phone_number = StringField('Phone Number', validators=[DataRequired(), Length(max=20)])
    short_bio = TextAreaField('Short Bio', validators=[Length(max=500)])
    is_worker = BooleanField('I want to offer my skills')
    # Hidden skills field will be populated by JS
    skills = TextAreaField('Skills (comma separated)', validators=[Optional(), Length(max=500)])

    # Custom validation for section based on branch
    def validate_section(form, field):
        branch = form.class_name.data
        if branch == 'CSE':
            allowed = [str(i) for i in range(11, 29)]
        else:
            allowed = ['A', 'B', 'C', 'D']
        if field.data not in allowed:
            raise ValidationError(f'Section must be one of: {", ".join(allowed)}')

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
    college_name = SelectField('College', choices=[('ABES Engineering College', 'ABES Engineering College')],
                               validators=[DataRequired()])
    year = SelectField('Year', choices=[
        ('First Year', 'First Year'),
        ('Second Year', 'Second Year'),
        ('Third Year', 'Third Year'),
        ('Fourth Year', 'Fourth Year')
    ], validators=[DataRequired()])
    class_name = SelectField('Branch', choices=[
        ('CSE', 'CSE'),
        ('CSE (AIML)', 'CSE (AIML)'),
        ('ME', 'ME'),
        ('CS', 'CS'),
        ('ECE', 'ECE'),
        ('CSE (DS)', 'CSE (DS)')
    ], validators=[DataRequired()])
    section = StringField('Section', validators=[DataRequired()])

    phone_number = StringField('Phone Number', validators=[DataRequired(), Length(max=20)])
    short_bio = TextAreaField('Short Bio', validators=[Length(max=500)])
    is_worker = BooleanField('I offer my skills')
    skills = TextAreaField('Skills (comma separated)', validators=[Optional(), Length(max=500)])

    def validate_section(form, field):
        branch = form.class_name.data
        if branch == 'CSE':
            allowed = [str(i) for i in range(11, 29)]
        else:
            allowed = ['A', 'B', 'C', 'D']
        if field.data not in allowed:
            raise ValidationError(f'Section must be one of: {", ".join(allowed)}')

    def validate_skills(form, field):
        if form.is_worker.data and not field.data:
            raise ValidationError('Please list your skills.')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('new_password')])