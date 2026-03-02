from flask import render_template, redirect, url_for, flash, session, request, Blueprint, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
import os
from app.extensions import db, limiter
from app.models import PendingUser
from app.forms import SignupForm, LoginForm, VerifyForm, ChangePasswordForm
from app.user_service import UserService
from app.email_service import EmailService
from app.data.services_data import ALL_SKILLS, SERVICES_DATA

auth_bp = Blueprint('auth', __name__)

# ---------- Helper: CSV export ----------
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
# SIGNUP
# =====================================================
@auth_bp.route('/signup', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def signup():
    form = SignupForm()
    skill_categories = SERVICES_DATA

    if form.validate_on_submit():
        try:
            from app.models import User, PendingUser

            # ===============================
            # Prevent duplicate signup
            # ===============================
            existing_user = User.query.filter(
                (User.email == form.email.data) |
                (User.username == form.username.data)
            ).first()

            existing_pending = PendingUser.query.filter(
                (PendingUser.email == form.email.data) |
                (PendingUser.username == form.username.data)
            ).first()

            if existing_user or existing_pending:
                flash(
                    "Username or email already registered or pending verification.",
                    "warning"
                )
                return redirect(url_for('auth.signup'))

            # ===============================
            # Create pending user
            # ===============================
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

            # ===============================
            # Save temp profile image
            # ===============================
            if form.profile_image.data:
                file = form.profile_image.data
                ext = file.filename.rsplit('.', 1)[1].lower()

                temp_filename = f"temp_{pending.id}.{ext}"
                temp_path = os.path.join(
                    current_app.config['TEMP_UPLOAD_FOLDER'],
                    temp_filename
                )

                file.save(temp_path)
                session['temp_profile_image'] = temp_filename

            # ===============================
            # Create verification code
            # ===============================
            code = UserService.create_verification_code(
                pending.id,
                commit=False
            )

            # ✅ IMPORTANT FIX
            # Commit FIRST
            db.session.commit()

            # ===============================
            # Send OTP Email AFTER commit
            # ===============================
            try:
                EmailService.send_verification_email_async(
                    pending.email,
                    pending.username,
                    code
                )
            except Exception as e:
                current_app.logger.error(f"Email failed: {e}")
                flash(
                    "Account created but failed to send email. Try resend.",
                    "warning"
                )

            # ===============================
            # Store session data
            # ===============================
            session['pending_skills'] = form.skills.data or ''
            session['pending_id'] = pending.id

            flash('Verification code sent to your email.', 'success')

            return redirect(
                url_for('auth.verify', pending_id=pending.id)
            )

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
            temp_filename = session.pop(
                'temp_profile_image',
                None
            )

            if temp_filename:
                temp_path = os.path.join(
                    current_app.config['TEMP_UPLOAD_FOLDER'],
                    temp_filename
                )

                if os.path.exists(temp_path):
                    ext = temp_filename.rsplit('.', 1)[1]
                    final_filename = f"user_{user.id}.{ext}"

                    final_path = os.path.join(
                        current_app.config['UPLOAD_FOLDER'],
                        final_filename
                    )

                    os.rename(temp_path, final_path)
                    user.profile_image = final_filename
                    db.session.commit()

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

            flash(
                'Email verified! Welcome to Aaj Ka Freelancer.',
                'success'
            )

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