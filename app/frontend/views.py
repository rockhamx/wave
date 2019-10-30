from flask import render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from . import frontend
from app import db
from app.models import User
from .forms import EditProfileForm


@frontend.route('/')
def index():
    return render_template('index.html')


@frontend.route('/user/<username>')
def user(username):
    u = User.query.filter_by(username=username).first_or_404()
    return render_template('user/profile.html', user=u)


@frontend.route('/user/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.motto = form.motto.data
        db.session.add(current_user)
        db.session.commit()
        flash('您的个人信息已更新。')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.motto.data = current_user.motto
    return render_template('user/edit_profile.html', form=form)