# auth/routes.py
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user
from models.user import db, User, OAuth
from auth.forms import SignupForm, LoginForm, ResetPasswordRequestForm, ResetPasswordForm
from auth.utils import send_email, generate_token, verify_token
import hashlib
from openstack.provision import create_openstack_resources

auth = Blueprint('auth', __name__)

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash("Email already registered.", "danger")
            return render_template('signup.html', form=form)

        user = User(email=form.email.data, name=form.email.data.split('@')[0])
        user.password = generate_password_hash(form.password.data)
        db.session.add(user)
        db.session.flush()

        try:
            create_openstack_resources(user)
            token = generate_token({'email': user.email})
            confirm_url = url_for('auth.confirm_email', token=token, _external=True)
            send_email(user.email, "Confirm Your Email", "activate.html", confirm_url=confirm_url)
            db.session.commit()
            flash("A confirmation link has been sent to your email.", "info")
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash(f"Setup failed: {str(e)}", "danger")
            return redirect(url_for('auth.signup'))

    return render_template('signup.html', form=form)

@auth.route('/confirm/<token>')
def confirm_email(token):
    data = verify_token(token)
    if not 
        flash("Invalid or expired link.", "danger")
        return redirect(url_for('auth.signup'))
    user = User.query.filter_by(email=data['email']).first()
    if user.confirmed:
        flash("Already confirmed.", "info")
    else:
        user.confirmed = True
        db.session.commit()
        flash("Account confirmed!", "success")
    return redirect(url_for('auth.login'))

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            if not user.confirmed:
                flash("Please confirm your email.", "warning")
                return redirect(url_for('auth.login'))
            login_user(user)
            return redirect(url_for('dashboard.dashboard'))
        else:
            flash("Invalid credentials.", "danger")
    return render_template('login.html', form=form)

@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))