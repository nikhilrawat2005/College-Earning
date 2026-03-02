from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
import re

from app.models import User
from app.user_service import UserService
from app.extensions import db, csrf
from app.services.skill_service import SkillService
from app.forms import EditProfileForm
from app.data.services_data import ALL_SKILLS

main_bp = Blueprint('main', __name__)


# =====================================================
# LANDING PAGE
# =====================================================
@main_bp.route('/')
def landing():
    total_users = UserService.get_user_count()
    total_workers = UserService.get_worker_count()

    return render_template(
        'landing.html',
        total_users=total_users,
        total_workers=total_workers
    )


# =====================================================
# DASHBOARD
# =====================================================
@main_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dual_dashboard.html')


# =====================================================
# SERVICES CONTENT (AJAX LOAD)
# =====================================================
@main_bp.route('/dashboard/services')
@login_required
def dashboard_services():
    # List of pastel CSS classes defined in style.css
    pastel_classes = [
        'category-pastel-1', 'category-pastel-2', 'category-pastel-3',
        'category-pastel-4', 'category-pastel-5', 'category-pastel-6',
        'category-pastel-7'
    ]
    return render_template(
        'services_content.html',
        skill_service=SkillService,
        pastel_classes=pastel_classes
    )


# =====================================================
# TUTORIALS CONTENT (AJAX LOAD)
# =====================================================
@main_bp.route('/dashboard/tutorials')
@login_required
def dashboard_tutorials():
    return render_template('tutorials_content.html')


# =====================================================
# PEOPLE DIRECTORY
# =====================================================
@main_bp.route('/people')
@login_required
def people():

    query = request.args.get('q', '')

    users_query = User.query.filter(User.is_verified == True)

    if query:
        users_query = users_query.filter(
            User.full_name.ilike(f"%{query}%") |
            User.college_name.ilike(f"%{query}%")
        )

    users = users_query.all()

    total_users = UserService.get_user_count()
    total_workers = UserService.get_worker_count()

    return render_template(
        'people.html',
        users=users,
        total_users=total_users,
        total_workers=total_workers,
        query=query
    )


# =====================================================
# USER PROFILE
# =====================================================
@main_bp.route('/profile/<username>')
@login_required
def profile(username):

    profile_user = User.query.filter_by(
        username=username,
        is_verified=True
    ).first_or_404()

    return render_template(
        'profile.html',
        profile_user=profile_user
    )


# =====================================================
# EDIT PROFILE (GET + POST)
# =====================================================
@main_bp.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(obj=current_user)

    if form.validate_on_submit():
        # Update user fields
        current_user.full_name = form.full_name.data
        current_user.college_name = form.college_name.data
        current_user.year = form.year.data
        current_user.class_name = form.class_name.data
        current_user.section = form.section.data
        current_user.phone_number = form.phone_number.data
        current_user.short_bio = form.short_bio.data
        current_user.is_worker = form.is_worker.data
        # Skills are handled via hidden field; form.skills.data already updated by JS
        current_user.skills = form.skills.data

        # Profile image is uploaded separately via /upload-profile-image, so we don't handle here
        db.session.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('main.profile', username=current_user.username))

    return render_template(
        'edit_profile.html',
        form=form,
        skills_list=ALL_SKILLS
    )


# =====================================================
# CROP IMAGE UPLOAD (AJAX)
# =====================================================
@main_bp.route('/upload-profile-image', methods=['POST'])
@login_required
def upload_profile_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Validate file type (allow only images)
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
        return jsonify({'error': 'Invalid file type'}), 400

    # Delete old image if exists
    UserService.delete_old_profile_image(current_user)

    # Save new image
    filename = f"user_{current_user.id}_{secure_filename(file.filename)}"
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    # Update user's profile_image field
    current_user.profile_image = filename
    db.session.commit()

    return jsonify({'filename': filename})


# =====================================================
# SERVICE USERS PAGE (NEW)
# =====================================================
@main_bp.route('/services/<path:skill_name>')
@login_required
def service_users(skill_name):
    """Show all verified workers offering a specific skill."""
    # Convert slug back to skill name (e.g., "video-editing" -> "Video Editing")
    # Build a mapping from slug to actual skill name using ALL_SKILLS
    slug_map = {skill.lower().replace(' ', '-'): skill for skill in ALL_SKILLS}
    # Also handle slashes or other punctuation if needed
    actual_skill = slug_map.get(skill_name)

    if not actual_skill:
        abort(404, description="Skill not found")

    # Query verified workers with this skill
    users = User.query.filter(
        User.is_verified == True,
        User.is_worker == True,
        User.skills.ilike(f'%{actual_skill}%')
    ).all()

    return render_template('service_users.html', skill=actual_skill, users=users)