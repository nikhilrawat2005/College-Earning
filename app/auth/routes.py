# app/auth/routes.py
from flask import render_template, redirect, url_for, flash, session, request, Blueprint
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash

from app import db
from app.models import PendingUser
from app.forms import SignupForm, LoginForm, VerifyForm, ChangePasswordForm
from app.user_service import UserService
from app.email_service import EmailService
from app.extensions import limiter

auth_bp = Blueprint('auth', __name__)

# ---------- Helper: CSV export ----------
def append_user_to_csv(user):
    import os, csv
    os.makedirs('exports', exist_ok=True)
    file_path = 'exports/users.csv'
    file_exists = os.path.isfile(file_path)
    with open(file_path, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['username', 'email', 'full_name', 'college_name', 'year', 'class_name', 'section', 'phone_number', 'is_worker', 'skills', 'created_at'])
        writer.writerow([
            user.username,
            user.email,
            user.full_name,
            user.college_name,
            user.year,
            user.class_name,
            user.section,
            user.phone_number,
            user.is_worker,
            user.skills or '',
            user.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])

# ---------- Routes ----------
@auth_bp.route('/signup', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        try:
            pending = UserService.create_pending_user(
                username=form.username.data,
                email=form.email.data,
                password=form.password.data,
                full_name=form.full_name.data,
                college_name=form.college_name.data,
                year=form.year.data,
                class_name=form.class_name.data,
                section=form.section.data,
                phone_number=form.phone_number.data,
                short_bio=form.short_bio.data,
                is_worker=form.is_worker.data
            )
            # Store skills in session (if worker)
            if form.is_worker.data:
                session['pending_skills'] = form.skills.data
            else:
                session['pending_skills'] = ''

            code = UserService.create_verification_code(pending.id)
            email_sent = EmailService.send_verification_email(pending.email, pending.username, code)
            if not email_sent:
                flash("Failed to send verification email. Check server logs.", "danger")
                return redirect(url_for('auth.signup'))
            session['pending_id'] = pending.id
            flash('Verification code sent to your email.', 'success')
            return redirect(url_for('auth.verify', pending_id=pending.id))
        except Exception as e:
            flash(f'Registration error: {str(e)}', 'danger')
    return render_template('signup.html', form=form)


@auth_bp.route('/verify/<int:pending_id>', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def verify(pending_id):
    if session.get('pending_id') != pending_id:
        flash('Invalid verification session.', 'warning')
        return redirect(url_for('auth.signup'))

    form = VerifyForm()
    if form.validate_on_submit():
        user, message = UserService.verify_pending_user(pending_id, form.code.data)
        if user:
            # Restore skills from session if any
            if 'pending_skills' in session:
                skills = session['pending_skills']
                if skills:
                    user.skills = skills
                    db.session.commit()
                session.pop('pending_skills', None)

            login_user(user)
            # Export to CSV after skills are set
            append_user_to_csv(user)
            EmailService.send_welcome_email(user.email, user.username)
            session.pop('pending_id', None)
            flash('Email verified! Welcome to College Earning.', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash(f'Verification failed: {message}', 'danger')
    return render_template('verify.html', form=form, pending_id=pending_id)


@auth_bp.route('/resend-code/<int:pending_id>')
@limiter.limit("3 per minute")
def resend_code(pending_id):
    pending = db.session.get(PendingUser, pending_id)
    if not pending:
        flash('Invalid request.', 'warning')
        return redirect(url_for('auth.signup'))
    code = UserService.create_verification_code(pending_id)
    EmailService.send_verification_email(pending.email, pending.username, code)
    flash('New verification code sent.', 'success')
    return redirect(url_for('auth.verify', pending_id=pending_id))


@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = UserService.authenticate_user(form.login_input.data, form.password.data)
        if user:
            login_user(user)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('main.dashboard'))
        flash('Invalid username/email or password.', 'danger')
    return render_template('login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.landing'))


@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not check_password_hash(current_user.password_hash, form.old_password.data):
            flash('Current password is incorrect.', 'danger')
            return redirect(url_for('auth.change_password'))
        UserService.change_password(current_user, form.new_password.data)
        flash('Password changed successfully.', 'success')
        return redirect(url_for('main.profile', username=current_user.username))
    return render_template('change_password.html', form=form)