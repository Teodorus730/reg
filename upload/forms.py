from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, RadioField, DateField, FileField, TextAreaField, SubmitField, FieldList, FormField
from wtforms.validators import DataRequired


class TrackForm(FlaskForm):
    track_title = StringField("Название трека", validators=[DataRequired()])
    version = StringField("Версия")
    artists = StringField("Артисты", validators=[DataRequired()])
    composer = StringField("Композитор (ФИО)", validators=[DataRequired()])
    authors = StringField("Авторы (ФИО)", validators=[DataRequired()])
    explicit = RadioField("Присутствие ненормативной лексики", choices=[("no", "Нет"), ("yes", "Да")])
    wav_file = FileField("Wav файл", validators=[DataRequired()])
    lyrics = TextAreaField("Текст трека")


class ReleaseForm(FlaskForm):
    title = StringField("Название релиза", validators=[DataRequired()])
    version = StringField("Версия")
    artists = StringField("Артисты", validators=[DataRequired()])
    release_type = RadioField("Тип релиза", choices=[("single", "Single"), ("ep", "EP"), ("album", "Album")])
    genre = SelectField("Жанр", choices=[("pop", "Pop"), ("rock", "Rock"), ("hiphop", "Hip-Hop")])
    release_date = DateField("Дата релиза", format="%Y-%m-%d")
    preorder_date = DateField("Дата предзаказа", format="%Y-%m-%d")
    label = StringField("Название лейбла", validators=[DataRequired()])
    
    tracks = FieldList(FormField(TrackForm), min_entries=0)
