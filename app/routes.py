from flask import render_template
from flask_login import LoginManager, login_required, current_user
from models import Users
from auth.routes import auth
from upload.routes import upload

from app import app

login_manager = LoginManager(app)
login_manager.login_view = "auth.login"

app.register_blueprint(auth, url_prefix="/auth")
app.register_blueprint(upload, url_prefix="/upload")


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

@app.route("/")
@login_required
def dashboard():
    return render_template("dashboard.html", user=current_user)