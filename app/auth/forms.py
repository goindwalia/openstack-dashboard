from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, \
    BooleanField, SubmitField
from wtforms.validators import Required, Length, \
    Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User

class LoginForm(Form):
    email = StringField('Email', validators=[Required(), Length(1,64), Email()])
    password = PasswordField('Password', validators=[Required()])
    submit = SubmitField('Sign In')

class RegistrationForm(Form):
    first_name = StringField('First Name', validators=[Required(), Length(1,64)])
    last_name = StringField('Last Name', validators=[Required(), Length(1,64)])
    username = StringField('Username', validators=[Required(), Length(1,64)])
    password = PasswordField('Password', validators=[Required(), Length(6,64),
                EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField('Confirm Password', validators=[Required()])
    email = StringField('Email', validators=[Required(), Email(), Length(1,64)])
    submit = SubmitField('Register')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')
