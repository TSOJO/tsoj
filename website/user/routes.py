from flask import (Blueprint, abort, flash, redirect, render_template, request,
                   url_for, current_app)
from flask_login import current_user, login_required, login_user, logout_user

from website.models import Problem, User, UserGroup, Token
from website.utils import is_safe_url

user_bp = Blueprint(
    'user_bp', __name__, template_folder='templates', static_folder='static'
)


@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email').lower()
        password = request.form.get('password')
        user = User.find_one({'email': email})

        if not user:
            flash('Invalid email', 'error')
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
    return redirect(url_for('user_bp.login'))


@user_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email').lower()

        if current_app.config.get('TONBRIDGE') and not email.endswith('@tonbridge-school.org'):
            flash('Please use your school email to register.', 'error')
            return redirect(url_for('user_bp.register'))
        
        user = User.find_one({'email': email})

        if user:
            flash('Email is already registered, please login.', 'error')
            return redirect(url_for('user_bp.login'))
        
        full_name = request.form.get('full_name')
        user = User(email=email, full_name=full_name)
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
    solved_problem_ids = user.get_solved_problem_ids()
    self_user_groups = user.fetch_user_groups()
    developers = current_app.config['DEVELOPERS']
    return render_template(
        'profile.html', user=user, problems=problems, solved_problem_ids=solved_problem_ids, self_user_groups=self_user_groups, developers=developers
    )


@user_bp.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        if request.form.get('action') == 'email_update':
            current_password = request.form.get('current_password')
            new_email = request.form.get('email')
            print(new_email)
            print(current_password)
            if current_user.check_password(current_password):
                if new_email and new_email != current_user.email:
                    existing = User.find_all({'email': new_email})
                    if existing:
                        flash('That email is already being used for another account.', 'error')
                    else:
                        current_user.validate_new_email(new_email)
                        flash('An email has been sent to the new address with a verification link.')
            else:
                flash('Current password not correct.', 'error')
                    
        elif request.form.get('action') == 'profile_update':
            new_username = request.form.get('username')
            if new_username and new_username != current_user.username:
                existing = User.find_all({'username': new_username})
                if existing:
                    flash('Username already exists.', 'error')
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
                
            selected_groups = request.form.getlist('group_select')
            if selected_groups:
                selected_group_ints = [int(g) for g in selected_groups]
                if set(selected_group_ints) != set(current_user.user_group_ids):
                    current_user.user_group_ids = selected_group_ints
                    flash('Group changed successfully.')
        
        elif request.form.get('action') == 'password_update':
            current_password = request.form.get('current_password')
            confirm_password = request.form.get('confirm_password')
            new_password = request.form.get('new_password')
            if new_password:
                if current_user.check_password(current_password):
                    if new_password == confirm_password:
                        current_user.set_password(new_password)
                        flash('Password changed successfully.')
                    else:
                        flash('New passwords must match.', 'error')
                else:
                    flash('Current password not correct.', 'error')


        current_user.save(replace=True)
    groups = UserGroup.find_all()
    user_group_ids = [str(g.id) for g in current_user.fetch_user_groups()]
    return render_template(
        'settings.html', groups=groups, user_group_ids=user_group_ids
    )

@user_bp.route('/verify/<plaintext_token>')
def verify_new_email(plaintext_token):
    token_data = Token.get_token_data(plaintext_token, 'change_email')
    if token_data is None:
        flash('Invalid token. This may be because it has expired.', 'error')
        return redirect(url_for('home_bp.home'))
    
    
    user_id = token_data['user_id']
    user = User.find_one({'id': user_id})
    
    if user is None:
        flash('User not found.', 'error')
        return redirect(url_for('user_bp.forgot_password'))
    
    user.email = token_data['new_email']
    user.save(replace=True, wait=True)
    flash('Email changed successfully.')
    return redirect(url_for('home_bp.home'))

@user_bp.route('/reset-password/<plaintext_token>', methods=['GET', 'POST'])
def reset_password(plaintext_token: str):
    if request.method == 'POST':
        token_data = Token.get_token_data(plaintext_token, 'change_password')
        if token_data is None:
            flash('Invalid token. This may be because it has expired.', 'error')
            return redirect(url_for('user_bp.forgot_password'))
        
        user_id = token_data['user_id']
        user = User.find_one({'id': user_id})
        
        if user is None:
            flash('User not found.', 'error')
            return redirect(url_for('home_bp.home'))
        
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        if new_password == confirm_password:
            user.set_password(new_password)
            user.save(replace=True, wait=True)
            flash('Password changed successfully. Login with your new password.')
            return redirect(url_for('user_bp.login'))
        else:
            flash('Passwords must match.', 'error')
    return render_template('password_reset.html', plaintext_token=plaintext_token)

@user_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    # TODO Add Captcha
    if request.method == 'POST':
        email = request.form.get('email')
        # Pretend everything is fine even if email is not a valid user
        flash('Please check your email for a link to reset your password. The link will expire in 3 hours.')
        user = User.find_one({'email': email})
        if user:
            user.send_reset_password_email()
            user.save(replace=True)
        return redirect(url_for('user_bp.login'))
    return render_template('forgot_password.html')

@user_bp.route('/admin_debug')
def admin_debug():
    if not current_app.config.get('DEV'):
        abort(404)
    logout_user()
    login_user(User.find_one({'id': 'admin'}))
    return redirect(url_for('home_bp.home'))


@user_bp.route('/user_debug')
def user_debug():
    if not current_app.config.get('DEV'):
        abort(404)
    logout_user()
    login_user(User.find_one({'id': 'user'}))
    return redirect(url_for('home_bp.home'))
