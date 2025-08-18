# dashboard/routes.py
from flask import Blueprint, render_template
from flask_login import login_required, current_user

dashboard = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard.route('/')
@login_required
def dashboard():
    return render_template('sidebar3.html', user=current_user)

@dashboard.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@dashboard.route('/settings')
@login_required
def settings():
    return render_template('settings.html', user=current_user)