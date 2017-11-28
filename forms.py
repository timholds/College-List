from flask_wtf import Form
from wtforms import BooleanField, StringField, PasswordField, SubmitField, validators
from wtforms.validators import Email, DataRequired
from werkzeug.security import generate_password_hash

class SignupForm(Form):
    email = StringField('email',
                validators=[DataRequired(),Email()])
    password = PasswordField(
                'password',
                validators=[DataRequired()])
    submit = SubmitField("Sign In")

"""
class RegistrationForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email Address', [validators.Length(min=4, max=35)])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    hashed_password = generate_password_hash(password, method='sha256')
    confirm = PasswordField('Repeat Password')
    accept_tos = BooleanField('I accept the TOS', [validators.DataRequired()])
"""
