from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, DateField, FieldList, FormField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Optional, Length
from flask_wtf.file import FileField, FileAllowed

class TrackForm(FlaskForm):
    class Meta:
        csrf = False
        
    title = StringField("Название трека", validators=[DataRequired()])
    version = StringField("Версия", validators=[Optional()])
    main_artists = StringField("Основные артисты", validators=[DataRequired()])
    featured_artists = StringField("Дополнительные артисты")
    author = StringField("Автор", validators=[DataRequired()])
    composer = StringField("Композитор", validators=[DataRequired()])
    tiktok_start = StringField("Старт TikTok (сек)", validators=[DataRequired()])
    isrc = StringField("ISRC")
    explicit = SelectField("Ненормативная лексика", choices=[("False", "Нет"), ("True", "Да")], validators=[DataRequired()])
    audio_file = FileField("Загрузка аудиофайла", validators=[FileAllowed(["wav"], "Только WAV"), DataRequired()])
    pdf_file = FileField("Загрузка PDF-файла", validators=[Optional(), FileAllowed(["pdf"], "Только PDF")])

class ReleaseForm(FlaskForm):
    title = StringField("Название релиза", validators=[DataRequired()])
    version = StringField("Версия релиза", validators=[Optional()])
    main_artists = StringField("Основные артисты", validators=[DataRequired()])
    featured_artists = StringField("Дополнительные артисты", validators=[Optional()])
    copyright = StringField("Копирайт", validators=[DataRequired()])
    genre = SelectField("Жанр", choices=[("Country", "Country"), ("Rock", "Rock"), ("Pop", "Pop")], validators=[DataRequired()])
    release_type = SelectField("Тип релиза", choices=[("Album", "Album"), ("Single", "Single")], validators=[DataRequired()])
    release_date = DateField("Дата релиза", validators=[DataRequired()])
    upc = StringField("UPC", validators=[Optional()])
    cover = FileField("Обложка", validators=[Optional(), FileAllowed(["png", "jpg", "jpeg"], "Только изображения")])
    comment = TextAreaField("Комментарий для модерации", validators=[Optional(), Length(min=3, max=250)])

    tracks = FieldList(FormField(TrackForm), min_entries=0)
    submit = SubmitField("Сохранить")
    
    
class CreateSubForm(FlaskForm):
    username = StringField("Новое имя пользователя", validators=[DataRequired(), Length(min=3, max=64)])
    password = PasswordField("Пароль", validators=[DataRequired()])
    submit = SubmitField("Создать пользователя")
    

class PromoForm(FlaskForm):
    promo1 = TextAreaField("Что вы хотели выразить/высказать в композиции, о чем ваш релиз", validators=[DataRequired(), Length(min=3, max=250)])
    promo2 = TextAreaField("Маркетинговая информация: все использованные и задуманные способы продвижения", validators=[DataRequired(), Length(min=3, max=250)])
    promo3 = TextAreaField("Ваш посыл; в чем заключается творческая или нравственная идея вашей деятельности", validators=[DataRequired(), Length(min=3, max=250)])
    submit = SubmitField("Добавить промо")


class VideoForm(FlaskForm):
    video = StringField("Добавить видеошот", validators=[DataRequired()])
    submit = SubmitField("Добавить видеошот")
