import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from flask_login import current_user, login_user, logout_user
from flaskr import db
from flaskr.models import User
from flaskr.forms import LoginForm, RegistrationForm
from werkzeug.urls import url_parse
from datetime import datetime

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET','POST'))
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You are now registered.')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)

@bp.route('/login', methods=('GET','POST'))
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        error = None
        user = User.query.filter_by(username=username).first()
        if user is None:
            error = 'Incorrect username.'
        elif not user.check_password(password):
            error = 'Incorrect password.'
        if error is None:
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('index')
            return redirect(next_page)
        flash(error)
    return render_template('auth/login.html', form=form)

@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
