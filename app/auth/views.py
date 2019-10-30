from flask import render_template, redirect, request, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user

from app.email import send_email
from . import auth, RegistrationForm, LoginForm, ChangePasswordForm, PasswordResetRequestForm, PasswordResetForm, \
    ChangeEmailForm
from ..models import User
from .. import db, email


@auth.route('/getting-on-board', methods=('GET', 'POST'))
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        u = User(email=form.email.data.lower(),
                 username=form.username.data,
                 password=form.password.data)
        db.session.add(u)
        db.session.commit()
        login_user(u)
        token = u.generate_confirmation_token()
        email.send_email(form.email.data, 'Confirm your registration', 'auth/email/confirm',
                         user=u, token=token)
        flash('A confirmation email has been send to you by email.')
        return redirect(url_for('auth.unconfirmed'))
    return render_template('auth/getting-on-board.html', form=form)


@auth.route('/login', methods=('GET', 'POST'))
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember.data)
            next_url = request.args.get('next')
            if next_url is None or not next_url.startswith('/'):
                next_url = url_for('frontend.user', username=current_user.username)
            return redirect(next_url)
        flash('Invalid username or password.')
    return render_template('/auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logout. See you around!')
    return redirect(url_for('frontend.index'))


@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed \
            and request.endpoint \
            and request.blueprint != 'auth' \
            and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('frontend.index'))
    if current_user.confirm(token):
        flash('你已经验证了你的邮箱，谢谢！')
        # flash('You have confirmed your account.Thanks!')
    else:
        flash('这个验证链接不可用或者已过期，点击此处重新获得一封验证邮件。')
        # flash('The confirmation link is invalid or expired.')
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
    email.send_email(current_user.email, 'Confirm your registration', 'auth/email/confirm',
                     user=current_user, token=token)
    flash('A confirmation email has been send to you by email.')
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
            flash('您的密码已更新，请用新的密码登录。')
            return redirect(url_for('frontend.index'))
        else:
            flash('非常抱歉，您输入的密码不正确。')
    return render_template("auth/change_password.html", form=form)


@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    if not current_user.is_anonymous:
        return redirect(url_for('frontend.index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user:
            token = user.generate_reset_token()
            send_email(user.email, 'Reset Your Password',
                       'auth/email/reset_password',
                       user=user, token=token)
        flash('An email with instructions to reset your password has been '
              'sent to you.')
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
            flash('Your password has been updated.')
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
            send_email(new_email, '确认您的电子邮箱',
                       'auth/email/change_email',
                       user=current_user, token=token)
            flash('一封包含验证链接的电子邮件已经发送到您的邮箱，请检查您的收件箱或垃圾邮件箱，'
                  '该链接只在十分钟之内有效，请尽快验证。')
            return redirect(url_for('frontend.index'))
        else:
            flash('无效的电子邮箱或密码。')
    return render_template("auth/change_email.html", form=form)


@auth.route('/change_email/<token>')
@login_required
def change_email(token):
    if current_user.change_email(token):
        db.session.commit()
        flash('您的电子邮箱已更新。')
    else:
        flash('验证链接无效或已过期。')
    return redirect(url_for('frontend.index'))

