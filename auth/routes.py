from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import db, Users
from auth.forms import LoginForm, CreateUserForm

auth = Blueprint("auth", __name__)

@auth.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for("dashboard"))
        flash("Invalid credentials")
    return render_template("login.html", form=form)

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))

@auth.route("/create_user", methods=["GET", "POST"])
@login_required
def create_user():
    if not current_user.is_admin:
        flash("Access denied")
        return redirect(url_for("dashboard"))

    form = CreateUserForm()
    if form.validate_on_submit():
        if Users.query.filter_by(username=form.username.data).first():
            flash("User already exists")
        else:
            new_user = Users(username=form.username.data, is_admin=form.is_admin.data)
            new_user.set_password(form.password.data)
            db.session.add(new_user)
            db.session.commit()
            flash("User created")
            return redirect(url_for("dashboard"))
    return render_template("create_user.html", form=form)
