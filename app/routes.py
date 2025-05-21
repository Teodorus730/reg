from flask import redirect, url_for
from flask_login import LoginManager, login_required, current_user
from models import Users
from auth.routes import auth
from client.routes import client
from admin.routes import admin
from moder.routes import moder


from app import app

login_manager = LoginManager(app)
login_manager.login_view = "auth.login"

app.register_blueprint(auth, url_prefix="/auth")
app.register_blueprint(client, url_prefix="/client")
app.register_blueprint(admin, url_prefix="/admin")
app.register_blueprint(moder, url_prefix="/moder")


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


@app.route("/")
def releases():
    return redirect(url_for("auth.login"))
