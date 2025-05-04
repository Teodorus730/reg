from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


db = SQLAlchemy()

    
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    releases = db.relationship('Release', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Release(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    version = db.Column(db.String(64))
    main_artists = db.Column(db.Text)  # можно сериализовать JSON
    featured_artists = db.Column(db.Text)
    copyright = db.Column(db.String(128))
    genre = db.Column(db.String(64))
    release_type = db.Column(db.String(64))
    release_date = db.Column(db.Date)
    upc = db.Column(db.String(64))
    cover_path = db.Column(db.String(256))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    tracks = db.relationship('Track', backref='release', lazy=True)

class Track(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    version = db.Column(db.String(64))
    main_artists = db.Column(db.Text)
    featured_artists = db.Column(db.Text)
    author = db.Column(db.String(128))
    composer = db.Column(db.String(128))
    tiktok_start = db.Column(db.Integer)
    isrc = db.Column(db.String(64))
    explicit = db.Column(db.Boolean, default=False)
    audio_path = db.Column(db.String(256))
    pdf_path = db.Column(db.String(256))

    release_id = db.Column(db.Integer, db.ForeignKey('release.id'), nullable=False)

