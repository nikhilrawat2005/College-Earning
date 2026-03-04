from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app, abort
from flask_login import login_required, current_user
import os

from app.models import User, HireRequest
from app.user_service import UserService
from app.extensions import db
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
# EDIT PROFILE (GET + POST) – with image handling
# =====================================================
@main_bp.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(obj=current_user)
    if form.validate_on_submit():
        current_user.full_name = form.full_name.data
        current_user.college_name = form.college_name.data
        current_user.year = form.year.data
        current_user.class_name = form.class_name.data
        current_user.section = form.section.data
        current_user.phone_number = form.phone_number.data
        current_user.short_bio = form.short_bio.data
        current_user.is_worker = form.is_worker.data
        current_user.skills = form.skills.data

        if form.profile_image.data:
            old_image = current_user.profile_image
            try:
                filename = UserService.save_profile_image(form.profile_image.data, current_user.id)
                if filename:
                    current_user.profile_image = filename
                    db.session.commit()
                    if old_image and old_image != 'default_profile.png':
                        old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], old_image)
                        if os.path.exists(old_path):
                            os.remove(old_path)
                else:
                    flash('Failed to upload image.', 'danger')
            except ValueError as e:
                flash(str(e), 'danger')
            except Exception as e:
                current_app.logger.error(f"Image upload error: {e}")
                flash('An error occurred while uploading the image.', 'danger')
        else:
            db.session.commit()

        flash('Profile updated successfully.', 'success')
        return redirect(url_for('main.profile', username=current_user.username))

    return render_template(
        'edit_profile.html',
        form=form,
        skills_list=ALL_SKILLS
    )


# =====================================================
# (Deprecated) Old AJAX upload endpoint – now returns 410
# =====================================================
@main_bp.route('/upload-profile-image', methods=['POST'])
@login_required
def upload_profile_image():
    return jsonify({'error': 'This endpoint is deprecated. Use edit profile form.'}), 410


# =====================================================
# SKILL WORKERS PAGE (Skill Detail)
# =====================================================
@main_bp.route('/services/<path:skill_name>')
@login_required
def skill_workers(skill_name):
    slug_map = {skill.lower().replace(' ', '-'): skill for skill in ALL_SKILLS}
    actual_skill = slug_map.get(skill_name)
    if not actual_skill:
        abort(404, description="Skill not found")
    description = SkillService.get_description(actual_skill)
    counts = SkillService.get_skill_counts()
    worker_count = counts.get(actual_skill, 0)
    users = User.query.filter(
        User.is_verified == True,
        User.is_worker == True,
        User.skills.ilike(f'%{actual_skill}%')
    ).all()
    return render_template(
        'service_detail.html',
        skill=actual_skill,
        description=description,
        worker_count=worker_count,
        users=users
    )


# =====================================================
# HIRE REQUESTS PAGE (for workers)
# =====================================================
@main_bp.route('/requests')
@login_required
def requests():
    if not current_user.is_worker:
        flash('Only workers can view requests.', 'warning')
        return redirect(url_for('main.dashboard'))
    pending_requests = HireRequest.query.filter_by(
        worker_id=current_user.id,
        status='pending',
        active=True
    ).order_by(HireRequest.created_at.desc()).all()
    return render_template('requests.html', requests=pending_requests)