from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=64)])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

class CreateUserForm(FlaskForm):
    username = StringField("New Username", validators=[DataRequired(), Length(min=3, max=64)])
    password = PasswordField("Password", validators=[DataRequired()])
    is_admin = BooleanField("Is Admin")
    submit = SubmitField("Create User")
