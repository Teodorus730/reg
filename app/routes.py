from flask import render_template
from flask_login import LoginManager, login_required, current_user
from models import Users
from auth.routes import auth
from client.routes import client

from app import app

login_manager = LoginManager(app)
login_manager.login_view = "auth.login"

app.register_blueprint(auth, url_prefix="/auth")
app.register_blueprint(client, url_prefix="/client")


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))
