from flask import Blueprint, redirect, url_for, render_template, flash, request, abort
from flask_login import login_user, logout_user, login_required, current_user

from website.user.forms import LoginForm, RegisterForm
from website.models import User, Problem
from website.utils import is_safe_url

user_bp = Blueprint('user_bp', __name__,
                    template_folder='templates', static_folder='static')


@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    if login_form.is_submitted():
        if not login_form.validate():
            flash('Invalid form.', 'error')
            return redirect(url_for('user_bp.login'))
        user = User.find_one({'id': login_form.id.data})
        print(user)
        if not user:
            flash('Usernmame does not exist.', 'error')
            return redirect(url_for('user_bp.login'))
        if not user.check_password(login_form.password.data):
            flash('Invalid username or password', 'error')
            return redirect(url_for('user_bp.login'))
        login_user(user)
        flash(f'Logged in successfully as {user.username}.')
        next_page = request.args.get('next')
        if not is_safe_url(next_page):
            return abort(400)
        return redirect(next_page or url_for('home_bp.home'))
    return render_template('login.html', form=login_form)


@user_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.')
    return redirect(url_for('home_bp.home'))


@user_bp.route('/register', methods=['GET', 'POST'])
def register():
    register_form = RegisterForm()
    if register_form.is_submitted():
        if not register_form.validate():
            flash('Invalid form.', 'error')
            return redirect(url_for('user_bp.register'))
        user = User.find_one({'id': register_form.id.data})
        if user:
            flash('Username already exists.', 'error')
            return redirect(url_for('user_bp.register'))
        user = User(
            id=register_form.id.data,
            email=register_form.email.data)
        user.set_password_and_send_email()
        user.save()
        flash('Account created successfully. An email will be sent to you with your login password.')
    return render_template('register.html', form=register_form)

@user_bp.route('/<id>/profile')
def profile(id: str):
    user = User.find_one({'id': id})
    if user is None:
        abort(404, description="User not found")
    problems = dict(map(lambda p: (p.id, False), Problem.find_all()))
    for solved_problem_id in user.get_solved_problem_ids():
        problems[solved_problem_id] = True
    problems = list(problems.items())
    problems_grid = [problems[i:i + 12] for i in range(0, len(problems), 12)]
    print(problems)
    return render_template('profile.html', user=user, problems_grid=problems_grid)

@user_bp.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        new_username = request.form.get('username')
        if new_username:
            current_user.username = new_username
            flash('Username changed successfully.')
        
        new_full_name = request.form.get('full_name')
        if new_full_name:
            current_user.full_name = new_full_name
            flash('Full name changed successfully.')
        
        new_password = request.form.get('password')
        if new_password:
            current_user.set_password(new_password)
            flash('Password changed successfully.')
        current_user.save(replace=True)
        
    return render_template('settings.html',)

# ! debug


@user_bp.route('/admin_debug')
def admin_debug():
    logout_user()
    print(User.find_one({'id': 'admin'}))
    login_user(User.find_one({'id': 'admin'}))
    return redirect(url_for('home_bp.home'))


@user_bp.route('/user_debug')
def user_debug():
    logout_user()
    login_user(User.find_one({'id': 'user'}))
    return redirect(url_for('home_bp.home'))
