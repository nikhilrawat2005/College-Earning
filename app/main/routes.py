from flask import render_template, redirect, url_for, flash, request, Blueprint
from flask_login import login_required, current_user

from app.models import User
from app.forms import EditProfileForm
from app.user_service import UserService

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def landing():
    total_users = UserService.get_user_count()
    total_workers = UserService.get_worker_count()
    return render_template(
        'landing.html',
        total_users=total_users,
        total_workers=total_workers
    )


@main_bp.route('/dashboard')
@login_required
def dashboard():
    query = request.args.get('q', '')
    users = UserService.search_users(query)
    total_users = UserService.get_user_count()
    total_workers = UserService.get_worker_count()
    return render_template('dashboard.html', users=users, total_users=total_users, total_workers=total_workers, query=query)


@main_bp.route('/profile/<username>')
@login_required
def profile(username):
    user = UserService.get_user_by_username(username)
    if not user:
        flash('User not found.', 'warning')
        return redirect(url_for('main.dashboard'))
    return render_template('profile.html', profile_user=user)


@main_bp.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(obj=current_user)
    if form.validate_on_submit():
        UserService.update_user_profile(current_user, {
            'full_name': form.full_name.data,
            'college_name': form.college_name.data,
            'year': form.year.data,
            'class_name': form.class_name.data,
            'section': form.section.data,
            'phone_number': form.phone_number.data,
            'short_bio': form.short_bio.data,
            'is_worker': form.is_worker.data,
            'skills': form.skills.data if form.is_worker.data else None
        })
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('main.profile', username=current_user.username))
    return render_template('edit_profile.html', form=form)