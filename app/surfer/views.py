from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user
from . import surfer, RegistrationForm, LoginForm
from ..models import User
from .. import db


@surfer.route('/getting-on-board', methods=('GET', 'POST'))
def getting_on_board():
    form = RegistrationForm()
    if form.validate_on_submit():
        # flash('This email has been registerd.')
        # return redirect('/login')
        u = User(email=form.email.data,
                      username=form.username.data,
                      password=form.password.data)
        db.session.add(u)
        db.session.commit()
        return redirect('/login')
    return render_template('surfer/getting-on-board.html', form=form)


@surfer.route('/login', methods=('GET', 'POST'))
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember.data)
            next_url = request.args.get('next')
            if next_url is None or not next_url.startswith('/'):
                next_url = url_for('frontend.index')
            return render_template(str(next_url))
        flash('Invalid username or password.')
    return render_template('/surfer/login.html', form=form)