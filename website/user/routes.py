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
        user = User.find_one({'username': login_form.username.data})
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
        user = User.find_one({'username': register_form.username.data})
        if user:
            flash('Username already exists.', 'error')
            return redirect(url_for('user_bp.register'))
        user = User(
            username=register_form.username.data,
            email=register_form.email.data,
            plaintext_password=register_form.password.data)
        user.save()
        flash('Account created successfully.')
    return render_template('register.html', form=register_form)


@user_bp.route('/<username>/profile', methods=['GET', 'POST'])
def profile(username: str):
    user = User.find_one({'username': username})
    if user is None:
        abort(404, description="User not found")
    problems = dict(map(lambda p: (p.id, False), Problem.find_all()))
    for solved_problem_id in user.get_solved_problem_ids():
        problems[solved_problem_id] = True
    problems = list(problems.items())
    problems_grid = [problems[i:i + 12] for i in range(0, len(problems), 12)]
    print(problems)
    return render_template('profile.html', user=user, problems_grid=problems_grid)

# ! debug


@user_bp.route('/admin_debug')
def admin_debug():
    logout_user()
    login_user(User.find_one({'username': 'admin'}))
    return redirect(url_for('home_bp.home'))


@user_bp.route('/user_debug')
def user_debug():
    logout_user()
    login_user(User.find_one({'username': 'user'}))
    return redirect(url_for('home_bp.home'))
