from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError

from website.models import User

class LoginForm(FlaskForm):
    id = StringField('id', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class RegisterForm(FlaskForm):
    id = StringField('id', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])