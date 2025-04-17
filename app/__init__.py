from config import Config
from models import db
from flask import Flask

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

with app.app_context():
    db.create_all()
    
from app import routes