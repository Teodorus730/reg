from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length

class LoginForm(FlaskForm):
    username = StringField("Имя пользователя", validators=[DataRequired(), Length(min=3, max=64)])
    password = PasswordField("Пароль", validators=[DataRequired()])
    submit = SubmitField("Войти")
    