from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from flask_babel import refresh, gettext as _, get_locale

from app.email import send_email
from . import auth, RegistrationForm, LoginForm, ChangePasswordForm, PasswordResetRequestForm, PasswordResetForm, \
    ChangeEmailForm
from ..models import User
from .. import db, email


@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed \
            and request.endpoint \
            and request.blueprint != 'auth' \
            and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))


@auth.route('/getting-on-board', methods=('GET', 'POST'))
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        u = User(email=form.email.data.lower(),
                 username=form.username.data.lower(),
                 password=form.password.data,
                 locale=str(get_locale()))
        db.session.add(u)
        db.session.commit()
        login_user(u)
        token = u.generate_confirmation_token()
        email.send_email((u.username, form.email.data), _(u'Confirm your registration'), 'auth/email/confirm',
                         user=u, token=token)
        flash(_(u'A confirmation email has been send to you by email.'))
        return redirect(url_for('auth.unconfirmed'))
    return render_template('auth/getting-on-board.html', form=form)


@auth.route('/login', methods=('GET', 'POST'))
def login():
    if current_user.is_authenticated:
        return redirect(url_for('user.profile', username=current_user.username))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember.data)
            next_url = request.args.get('next')
            refresh()    # refresh locale & timezone
            if next_url is None or not next_url.startswith('/'):
                next_url = url_for('user.profile', username=current_user.username)
            flash(_(u'Welcome back, %(name)s!', name=current_user.name), 'success')
            return redirect(next_url)
        flash(_(u'Invalid username or password.'), 'warning')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash(_(u'You have been logout. See you around!'))
    return redirect(url_for('frontend.index'))


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        flash(_(u'You\'ve already confirmed your account.'))
        return redirect(url_for('frontend.index'))
    if current_user.confirm(token):
        flash(_(u'You have confirmed your account.Thanks!'))
        return redirect(url_for('auth.unconfirmed'))
    else:
        flash(_(u'The confirmation link is invalid or expired.'))
        return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
@login_required
def unconfirmed():
    if current_user.confirmed:
        return redirect(url_for('frontend.index'))
    return render_template('auth/unconfirmed.html', user=current_user)


@auth.route('/resent_confirmation_email')
@login_required
def resent_confirmation_email():
    if current_user.confirmed:
        return redirect(url_for('frontend.index'))
    token = current_user.generate_confirmation_token()
    email.send_email(current_user.email, _(u'Confirm your registration'), 'auth/email/confirm',
                     user=current_user, token=token)
    flash(_(u'A confirmation email has been send to you by email.'))
    return redirect(url_for('auth.unconfirmed'))


@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            db.session.commit()
            flash(_(u'Your password has been updated.'))  # 您的密码已更新，请用新的密码登录。
            return redirect(url_for('frontend.index'))
        else:
            flash(_(u'Invalid password.'), 'warning')  #
    return render_template("auth/change_password.html", form=form)


@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    if not current_user.is_anonymous:
        return redirect(url_for('user.profile', username=current_user.username))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user:
            token = user.generate_reset_token()
            send_email(user.email, _(u'Reset Your Password'),
                       'auth/email/reset_password',
                       user=user, token=token)
        flash(_(u'An email with instructions to reset your password has been '
              'sent to you.'))
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if not current_user.is_anonymous:
        return redirect(url_for('frontend.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        if User.reset_password(token, form.password.data):
            db.session.commit()
            flash(_(u'Your password has been updated.'))
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('frontend.index'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/change_email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data.lower()
            token = current_user.generate_email_change_token(new_email)
            send_email(new_email, _(u'Confirm your email address'),
                       'auth/email/change_email',
                       user=current_user, token=token)
            flash(_(u'An email with instructions to confirm your new email '
                  'address has been sent to you.'))
            return redirect(url_for('frontend.index'))
        else:
            flash(_(u'Invalid email or password.'))
    return render_template("auth/change_email.html", form=form)


@auth.route('/change_email/<token>')
@login_required
def change_email(token):
    if current_user.change_email(token):
        db.session.commit()
        flash(_(u'Your email address has been updated.'))  # 您的电子邮箱已更新。
    else:
        flash(_(u'Invalid request.'))  # 验证链接无效或已过期。
    return redirect(url_for('frontend.index'))

