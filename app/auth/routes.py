from flask import render_template, redirect, url_for, flash, session, request, Blueprint, current_app, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
import os
from datetime import datetime, timedelta
from app.extensions import db, limiter
from app.models import PendingUser, User
from app.forms import SignupForm, LoginForm, VerifyForm, ChangePasswordForm
from app.user_service import UserService
from app.email_service import EmailService
from app.data.services_data import SERVICES_DATA

auth_bp = Blueprint('auth', __name__)


def append_user_to_csv(user):
    import csv
    os.makedirs('exports', exist_ok=True)
    file_path = 'exports/users.csv'
    file_exists = os.path.isfile(file_path)

    with open(file_path, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow([
                'username', 'email', 'full_name',
                'college_name', 'year', 'class_name',
                'section', 'phone_number',
                'is_worker', 'skills', 'created_at'
            ])

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


# =====================================================
# AVAILABILITY CHECK (AJAX)
# =====================================================
@auth_bp.route('/check-availability', methods=['GET'])
@limiter.limit("30 per minute")
def check_availability():
    field = request.args.get('field')
    value = request.args.get('value')

    if field not in ['username', 'email'] or not value:
        return jsonify({'available': False, 'message': 'Invalid request'}), 400

    # Clean up expired pending users first
    UserService.cleanup_expired_pending_users()

    # Check in User table
    user_exists = User.query.filter_by(**{field: value}).first() is not None
    if user_exists:
        return jsonify({'available': False, 'message': f'{field.capitalize()} already taken'})

    # Check in PendingUser table (non-expired)
    pending = PendingUser.query.filter_by(**{field: value}).first()
    if pending and (datetime.utcnow() - pending.created_at <= timedelta(minutes=15)):
        return jsonify({'available': False, 'message': f'{field.capitalize()} already pending verification'})

    return jsonify({'available': True, 'message': f'{field.capitalize()} is available'})


# =====================================================
# SIGNUP
# =====================================================
@auth_bp.route('/signup', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def signup():
    # Clean expired pending users
    UserService.cleanup_expired_pending_users()

    form = SignupForm()
    skill_categories = SERVICES_DATA

    if form.validate_on_submit():
        try:
            # Check existing user
            existing_user = User.query.filter(
                (User.email == form.email.data) |
                (User.username == form.username.data)
            ).first()

            if existing_user:
                flash("Username or email already registered.", "warning")
                return redirect(url_for('auth.signup'))

            # Check pending (non-expired)
            existing_pending = PendingUser.query.filter(
                (PendingUser.email == form.email.data) |
                (PendingUser.username == form.username.data)
            ).first()

            if existing_pending:
                flash("Username or email already pending verification. Please check your email or wait 15 minutes.", "warning")
                return redirect(url_for('auth.signup'))

            # Create pending user (no image yet)
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
                is_worker=form.is_worker.data,
                commit=False
            )

            db.session.flush()

            # Create verification code
            code = UserService.create_verification_code(pending.id, commit=False)

            # Commit everything
            db.session.commit()

            # Send OTP email
            try:
                EmailService.send_verification_email_async(
                    pending.email,
                    pending.username,
                    code
                )
            except Exception as e:
                current_app.logger.error(f"Email failed: {e}")
                flash("Account created but failed to send email. Try resend.", "warning")

            # Store minimal session data
            session['pending_skills'] = form.skills.data or ''
            session['pending_id'] = pending.id

            flash('Verification code sent to your email.', 'success')
            return redirect(url_for('auth.verify', pending_id=pending.id))

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Signup error: {e}")
            flash(f'Registration error: {str(e)}', 'danger')

    return render_template(
        'signup.html',
        form=form,
        skill_categories=skill_categories
    )


# =====================================================
# VERIFY EMAIL
# =====================================================
@auth_bp.route('/verify/<int:pending_id>', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def verify(pending_id):

    if session.get('pending_id') != pending_id:
        flash('Invalid verification session.', 'warning')
        return redirect(url_for('auth.signup'))

    form = VerifyForm()

    if form.validate_on_submit():
        user, message = UserService.verify_pending_user(
            pending_id,
            form.code.data
        )

        if user:
            # Now handle profile image if uploaded during signup
            # The image file is still in the form data? Actually during signup, the image was uploaded but not saved yet.
            # We need to retrieve the file from the signup form data. But we don't have the file here.
            # So we must have saved it temporarily or passed it along. But we removed temp image system.
            # Alternative: Do not allow image upload during signup. Or rework signup to handle image after verification.
            # Given the complexity, let's simplify: Do NOT allow profile image upload during signup.
            # Users can upload after login via edit profile.
            # So remove profile_image from SignupForm and template.

            # For now, we'll set default.
            user.profile_image = 'default_profile.png'

            if 'pending_skills' in session:
                skills = session.pop('pending_skills')
                if skills:
                    user.skills = skills

            db.session.commit()

            login_user(user)
            append_user_to_csv(user)

            EmailService.send_welcome_email_async(
                user.email,
                user.username
            )

            session.pop('pending_id', None)

            flash('Email verified! Welcome to Aaj Ka Freelancer.', 'success')

            return redirect(url_for('main.dashboard'))

        else:
            flash(f'Verification failed: {message}', 'danger')

    return render_template(
        'verify.html',
        form=form,
        pending_id=pending_id
    )


# =====================================================
# LOGIN
# =====================================================
@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = UserService.authenticate_user(
            form.login_input.data,
            form.password.data
        )

        if user:
            login_user(user)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('main.dashboard'))

        flash('Invalid username/email or password.', 'danger')

    return render_template('login.html', form=form)


# =====================================================
# LOGOUT
# =====================================================
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.landing'))


# =====================================================
# CHANGE PASSWORD
# =====================================================
@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():

    form = ChangePasswordForm()

    if form.validate_on_submit():

        if not check_password_hash(
                current_user.password_hash,
                form.old_password.data):
            flash('Current password is incorrect.', 'danger')
            return redirect(url_for('auth.change_password'))

        UserService.change_password(
            current_user,
            form.new_password.data
        )

        flash('Password changed successfully.', 'success')

        return redirect(
            url_for(
                'main.profile',
                username=current_user.username
            )
        )

    return render_template(
        'change_password.html',
        form=form
    )


# =====================================================
# RESEND VERIFICATION CODE
# =====================================================
@auth_bp.route('/resend-code/<int:pending_id>')
@limiter.limit("3 per minute")
def resend_code(pending_id):

    pending = db.session.get(PendingUser, pending_id)

    if not pending:
        flash('Invalid request.', 'warning')
        return redirect(url_for('auth.signup'))

    # Create new verification code
    code = UserService.create_verification_code(
        pending_id,
        commit=True
    )

    # Send email again
    try:
        EmailService.send_verification_email(
            pending.email,
            pending.username,
            code
        )
    except Exception as e:
        flash(f"Failed to resend verification email: {str(e)}", "danger")
        return redirect(url_for('auth.verify', pending_id=pending_id))

    flash('New verification code sent.', 'success')
    return redirect(url_for('auth.verify', pending_id=pending_id))