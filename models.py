from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


db = SQLAlchemy()


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    user_type = db.Column(db.String(20), nullable=False)  # 'admin', 'moder', 'artist', 'sub'
    
    releases = db.relationship('Release', backref='user', lazy=True)
    
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    sub_accounts = db.relationship('Users', backref=db.backref('creator', remote_side=[id]), lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.user_type == "admin"

    @property
    def is_moder(self):
        return self.user_type == "moder"

    @property
    def is_artist(self):
        return self.user_type == "artist"

    @property
    def is_sub(self):
        return self.user_type == "sub"


class Release(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    version = db.Column(db.String(64))
    main_artists = db.Column(db.Text)
    featured_artists = db.Column(db.Text)
    copyright = db.Column(db.String(128))
    genre = db.Column(db.String(128))
    release_type = db.Column(db.String(64))
    release_date = db.Column(db.Date)
    upc = db.Column(db.String(64))
    cover_path = db.Column(db.String(256))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    comment = db.Column(db.String(512))
    answer = db.Column(db.String(256))
    
    promo1 = db.Column(db.String(2048))
    promo2 = db.Column(db.String(2048))
    promo3 = db.Column(db.String(2048))
    
    video = db.Column(db.String(256))
    
    edit = db.Column(db.String(512))
    
    prodby = db.Column(db.String(256))

    tracks = db.relationship('Track', backref='release', lazy=True)
    
    status = db.Column(db.Integer, nullable=False)

class Track(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    version = db.Column(db.String(64))
    main_artists = db.Column(db.Text)
    featured_artists = db.Column(db.Text)
    author = db.Column(db.String(128))
    composer = db.Column(db.String(128))
    tiktok_start = db.Column(db.String(128))
    isrc = db.Column(db.String(64))
    explicit = db.Column(db.Boolean, default=False)
    audio_path = db.Column(db.String(256))
    pdf_path = db.Column(db.String(256))

    release_id = db.Column(db.Integer, db.ForeignKey('release.id'), nullable=False)

