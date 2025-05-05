from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import db, Users
from admin.forms import CreateUserForm

admin = Blueprint("admin", __name__)

@admin.route("/users", methods=["GET", "POST"])
@login_required
def users():
    if not current_user.is_admin:
        flash("Access denied")
        return redirect(url_for("client.dashboard"))

    if request.method == "POST":
        action = request.form.get("action")
        user_id = request.form.get("user_id")
        user = Users.query.get(user_id)
        if not user:
            flash("User not found")
            return redirect(url_for("admin.users"))

        if action == "delete":
            if user.id == current_user.id:
                flash("You cannot delete yourself.")
                return redirect(url_for("admin.users"))

            db.session.delete(user)
            db.session.commit()
            flash(f"User {user.username} deleted.")

        elif action == "update":
            new_role = request.form.get("user_type")
            if new_role not in ("admin", "moder", "artist", "sub"):
                flash("Invalid role.")
            else:
                user.user_type = new_role
                db.session.commit()
                flash(f"Role updated for {user.username}.")

    users = Users.query.all()
    return render_template("users.html", users=users)



@admin.route("/create_user", methods=["GET", "POST"])
@login_required
def create_user():
    if not current_user.is_admin:
        flash("Access denied")
        return redirect(url_for("client.dashboard"))

    form = CreateUserForm()
    if form.validate_on_submit():
        if Users.query.filter_by(username=form.username.data).first():
            flash("User already exists")
        else:
            new_user = Users(
                    username=form.username.data,
                    user_type=form.user_type.data,
                    creator_id=current_user.id,
                )
            new_user.set_password(form.password.data)
            db.session.add(new_user)
            db.session.commit()
            flash("User created")
            return redirect(url_for("admin.users"))
    return render_template("create_user.html", form=form)
