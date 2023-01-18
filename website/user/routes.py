from flask import Blueprint, redirect, url_for, render_template, flash, request, abort
from flask_login import login_user, logout_user, login_required, current_user

from website.models import User, Problem, UserGroup
from website.utils import is_safe_url

user_bp = Blueprint(
    'user_bp', __name__, template_folder='templates', static_folder='static'
)


@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.find_one({'email': email})

        if not user:
            flash('Email does not exist.', 'error')
            return redirect(url_for('user_bp.login'))
        if not user.check_password(password):
            flash('Invalid email or password', 'error')
            return redirect(url_for('user_bp.login'))

        login_user(user)
        flash(f'Logged in successfully as {user.username}.')

        next_page = request.args.get('next')
        if not is_safe_url(next_page):
            return abort(400)

        return redirect(next_page or url_for('home_bp.home'))
    return render_template('login.html')


@user_bp.route('/logout')
def logout():
    logout_user()
    flash('Logged out successfully.')
    return redirect(url_for('home_bp.home'))


@user_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.find_one({'email': email})

        if user:
            flash('Email already used. Login instead.', 'error')
            return redirect(url_for('user_bp.login'))

        user = User(email=email)
        user.set_password_and_send_email()
        user.save()
        flash(
            'Account created successfully. An email will be sent to you with your login password.'
        )
        return redirect(url_for('user_bp.login'))
    return render_template('register.html')


@user_bp.route('/profile/<id>')
def profile(id: str):
    user = User.find_one({'id': id})
    if user is None:
        abort(404, description="User not found")
    problems = Problem.find_all()
    solved_problems = user.get_solved_problem_ids()
    return render_template('profile.html', user=user, problems=problems, solved_problems=solved_problems)


@user_bp.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        new_username = request.form.get('username')
        if new_username and new_username != current_user.username:
            existing = User.find_all({'username': new_username})
            if existing:
                flash('Username already exists', 'error')
            else:
                current_user.username = new_username
                flash('Username changed successfully.')

        new_full_name = request.form.get('full_name')
        if new_full_name and new_full_name != current_user.full_name:
            current_user.full_name = new_full_name
            flash('Full name changed successfully.')

        new_hide_name = 'hide_name' in request.form
        if new_hide_name != current_user.hide_name:
            current_user.hide_name = new_hide_name
            flash('Hide name option changed successfully.')

        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        if new_password:
            if current_user.check_password(current_password):
                current_user.set_password(new_password)
                flash('Password changed successfully.')
            else:
                flash('Current password not correct.', 'error')
        
        selected_groups = request.form.getlist('group_select')
        if selected_groups:
            selected_group_ints = [int(g) for g in selected_groups]
            if set(selected_group_ints) != set(current_user.user_group_ids):
                current_user.user_group_ids = selected_group_ints
                flash('Groups changed successfully.')
            
        current_user.save(replace=True)
    groups = UserGroup.find_all()
    user_group_ids = [str(g.id) for g in current_user.fetch_groups()]
    return render_template('settings.html', groups=groups, user_group_ids=user_group_ids)


# ! debug


@user_bp.route('/admin_debug')
def admin_debug():
    logout_user()
    login_user(User.find_one({'id': 'admin'}))
    return redirect(url_for('home_bp.home'))


@user_bp.route('/user_debug')
def user_debug():
    logout_user()
    login_user(User.find_one({'id': 'user'}))
    return redirect(url_for('home_bp.home'))
