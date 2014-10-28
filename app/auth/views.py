from flask import render_template, redirect, \
    url_for, abort, session, flash, request, current_app
from flask.ext.login import login_user, current_user, \
    logout_user, login_required
from datetime import datetime
from .forms import LoginForm, RegistrationForm
from . import auth
from ..models import User
from ..email import send_email

@auth.before_app_request
def before_request():
    #Checks if the user is allowed to login
    if current_user.is_authenticated():
        #Checks if the logged in user is confirmed
        if not current_user.confirmed \
                and request.endpoint[:5] != 'auth.':
            return redirect(url_for('auth.unconfirmed'))

@auth.before_app_request
def before_app_request():
    #This fuunction is requested before every request
    #Session expires after 50 minutes
    if current_user.is_authenticated():
        diff = (datetime.utcnow() - session['login_time']).seconds / 60
        if diff >= 50:
            #After 60 minutes token becomes invalidate itself
            if diff < 60:
                current_user.invalidateToken()
            logout_user()
            session.clear()
            flash('Session Expired: Please Login Again')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        #Checks whether the user is present in local database or not
        user = User.query.filter_by(email=form.email.data).first()
        password = form.password.data
        if user is not None:
            isAuthenticated = user.authenticateUser(password)
            if isAuthenticated:
                login_user(user)
                return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid username or password.')
    return render_template('auth/login.html', form=LoginForm())

@auth.route('/logout')
@login_required
def logout():
    if current_user.invalidateToken():
        logout_user()
        session.clear()
        flash('You have been logged out.')
    else:
        flash('Oops! Something went wrong')
    return redirect(url_for('main.index'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if not current_user.is_authenticated():
        form = RegistrationForm()
        if form.validate_on_submit():
            user = User(username=form.username.data, first_name=form.first_name.data, last_name=form.last_name.data,
                    email=form.email.data)
            #Creates a project for the user
            if user.createProject():
                #Creates the user if project is created
                if user.createUser(form.password.data):
                    #Gives the user role of __member__ if user is created successfully
                    if user.addMemberRole():
                        token = user.generate_confirmation_token()
                        send_email(user.email, 'Confirm Your Account',
                               'auth/email/confirm', user=user, token=token)
                        flash('Confirmation email has been sent.')
                        return redirect(request.args.get('next') or url_for('main.index'))
            flash('Oops! Something went wrong. Try again')
        return render_template('auth/register.html', form=form)
    return redirect(url_for('main.index'))

@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('You have confirmed your account. Thanks!')
    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('main.index'))

@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account',
           'auth/email/confirm', user=current_user, token=token)
    flash('A new confirmation email has been sent.')
    return redirect(request.args.get('next') or url_for('main.index'))

@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous() or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')