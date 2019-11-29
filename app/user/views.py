import os

from flask import request, render_template, flash, redirect, url_for, current_app
from flask_babel import refresh, gettext as _
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from app import db
from app.models import User, Publication, Message
from . import user, EditProfileForm, PreferenceForm
from ..frontend.forms import NewPublicationForm
from .forms import MessageForm


# User Profile
@user.route('/<username>')
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.latest_posts(page=page)
    return render_template('user/profile.html', user=user, posts=posts)


@user.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        file = form.avatar.data
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(
                current_app.instance_path, 'avatars', filename
            ))
        locale = form.locale.data
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.description = form.description.data
        current_user.locale = locale
        db.session.add(current_user)
        db.session.commit()
        if current_user.locale != locale:
            refresh()
        flash(_(u'Your profile has been updated.'))
        return redirect(url_for('user.profile', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.description.data = current_user.description
    form.locale.data = current_user.locale
    return render_template('user/edit_profile.html', form=form)


@user.route('/follow', methods=['POST'])
@login_required
def follow():
    u = User.query.filter_by(username=request.form['username']).first()
    if u and current_user != u and not current_user.is_following(u):
        current_user.follows(u)
        db.session.commit()
        status = _('Following')
        return {'status': status}
    return {}


@user.route('/unfollow', methods=['POST'])
@login_required
def unfollow():
    u = User.query.filter_by(username=request.form['username']).first()
    if u and current_user != u and current_user.is_following(u):
        current_user.un_follows(u)
        db.session.commit()
        status = _('Follow')
        return {'status': status}
    return {}


@user.route('/<username>/following')
def following(username):
    u = User.query.filter_by(username=username).first_or_404()
    users = u.following_desc_by_time()
    return render_template('user/following.html', username=username, users=users)


@user.route('/<username>/followers')
def followers(username):
    u = User.query.filter_by(username=username).first_or_404()
    users = u.followers_desc_by_time()
    return render_template('user/followers.html', username=username, users=users)


@user.route('/followed')
@login_required
def followed():
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts(page)
    return render_template('user/followed_posts.html', posts=posts)


@user.route('/my/hearts')
@login_required
def hearts():
    page = request.args.get('page', 1, type=int)
    posts = current_user.hearts_desc_by_time(page)
    return render_template('user/hearts.html', posts=posts)


@user.route('/my/bookmarks')
@login_required
def bookmarks():
    page = request.args.get('page', 1, type=int)
    posts = current_user.bookmarks_desc_by_time(page)
    return render_template('user/bookmarks.html', posts=posts)


@user.route('/my/publications', methods=['GET', 'POST'])
@login_required
def publications():
    form = NewPublicationForm()
    if form.validate_on_submit():
        name = form.name.data
        if Publication.exist(name):
            flash(_('Already exist.'))
        else:
            description = form.description.data
            creator = current_user._get_current_object()
            pub = Publication(name=name, description=description, creator=creator)
            db.session.add(pub)
            db.session.commit()
            # current_user.followed_publications.append(pub)
            user = User.query.get(current_user.id)
            user.follow_publication(pub)
            db.session.commit()
            flash(_('You have been successfully created a publication.'))
        return redirect(url_for('.publications'))
    page = request.args.get('page', 1, type=int)
    pubs = current_user.followed_pubs_desc_by_time(page)
    return render_template('user/publications.html', publications=pubs, form=form)


@user.route('/my/interests')
@login_required
def interests():
    return redirect(url_for('.publications'))


@user.route('/my/messages')
@login_required
def messages():
    sent_messages = current_user.messages_sent_desc_by_time()
    received_messages = current_user.messages_received_asc_by_time()
    return render_template('user/messages.html', sent_messages=sent_messages, received_messages=received_messages)


@user.route('/send_message/<recipient>', methods=['GET', 'POST'])
@login_required
def send_message(recipient):
    user = User.query.filter_by(username=recipient).first_or_404()
    form = MessageForm()
    if form.validate_on_submit():
        msg = Message(sender=current_user, recipient=user,
                      content=form.message.data)
        db.session.add(msg)
        db.session.commit()
        flash(_('Your message has been sent.'))
        return redirect(url_for('frontend.messages', username=current_user.username))
    return render_template('user/send_message.html', form=form, recipient=user.name)


@user.route('/preference', methods=['GET', 'POST'])
@login_required
def preference():
    form = PreferenceForm()
    return render_template('user/preference.html', form=form)