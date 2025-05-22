from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length


class CreateUserForm(FlaskForm):
    username = StringField("Новое имя пользователя", validators=[DataRequired(), Length(min=3, max=64)])
    password = StringField("Пароль", validators=[DataRequired()])
    user_type = SelectField(
        "Тип аккаунта",
        choices=[("admin", "Админ"), ("moder", "Модератор"), ("artist", "Артист"), ("sub", "Саб аккаунт")],
        validators=[DataRequired()]
    )
    submit = SubmitField("Создать пользователя")
    
