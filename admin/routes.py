from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import db, Users
from admin.forms import CreateUserForm

admin = Blueprint("admin", __name__)


@admin.route('/all_users')
@login_required
def all_users():
    if not (current_user.is_admin):
        flash("Access denied")
        return redirect(url_for("client.dashboard"))
    
    type_filter = request.args.get("user_type")
    query = Users.query

    if type_filter is not None and type_filter in ["admin", "sub", "moder", "artist"]:
        query = query.filter_by(user_type=type_filter)

    users = query.order_by(Users.id.desc()).all()
    return render_template("all_users.html", users=users, type_filter=type_filter)



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


@admin.route('/users/<int:user_id>', methods=["GET", "POST"])
@login_required
def user_detail(user_id):
    if not current_user.is_admin:
        flash("Access denied")
        return redirect(url_for("client.dashboard"))

    user = Users.query.get_or_404(user_id)

    if request.method == "POST":
        action = request.form.get("action")

        if action == "update_type":
            new_type = request.form.get("user_type")
            if new_type and new_type in ["admin", "moder", "artist", "sub"]:
                user.user_type = new_type
                db.session.commit()
                flash("Тип обновлён", "success")
            else:
                flash("Недопустимый тип", "error")

        elif action == "update_password":
            new_password = request.form.get("password")
            if new_password:
                user.set_password(new_password)
                db.session.commit()
                flash("Пароль обновлён", "success")
            else:
                flash("Недопустимый пароль", "error")

        elif action == "update_username":
            new_username = request.form.get("username")
            if new_username:
                user.username = new_username
                db.session.commit()
                flash("Юзернейм обновлён", "success")
            else:
                flash("Недопустимый юзернейм", "error")

    return render_template("user_detail.html", user=user)
