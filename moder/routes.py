from flask import Blueprint, render_template, request, redirect, url_for, abort, flash
from flask_login import login_required, current_user
from models import db, Release, Track


moder = Blueprint('moder', __name__)


@moder.route('/all_releases')
@login_required
def all_releases():
    if not (current_user.is_moder):
        flash("Access denied")
        return redirect(url_for("client.dashboard"))
    
    status_filter = request.args.get("status")
    query = Release.query

    if status_filter is not None and status_filter.isdigit():
        query = query.filter_by(status=int(status_filter))

    releases = query.order_by(Release.id.desc()).all()
    return render_template("all_releases.html", releases=releases, status_filter=status_filter)


@moder.route('/release/<int:release_id>', methods=["GET", "POST"])
@login_required
def release_detail(release_id):
    if not current_user.is_moder:
        flash("Access denied")
        return redirect(url_for("client.dashboard"))

    release = Release.query.get_or_404(release_id)

    if request.method == "POST":
        action = request.form.get("action")

        if action == "update_status":
            new_status = request.form.get("status")
            if new_status and new_status.isdigit() and int(new_status) in (0, 1, 2, 3):
                release.status = int(new_status)
                db.session.commit()
                flash("Статус обновлён", "success")
            else:
                flash("Недопустимый статус", "error")

        elif action == "update_upc":
            release.upc = request.form.get("upc") or None
            db.session.commit()
            flash("UPC обновлён", "success")

        elif action == "update_answer":
            release.answer = request.form.get("answer") or None
            db.session.commit()
            flash("Ответ обновлён", "success")

    return render_template("release_detail.html", release=release)


@moder.route('/track/<int:track_id>', methods=["GET", "POST"])
@login_required
def track_detail(track_id):
    if not current_user.is_moder:
        flash("Access denied")
        return redirect(url_for("client.dashboard"))

    track = Track.query.get_or_404(track_id)

    if request.method == "POST":
        track.isrc = request.form.get("isrc")
        db.session.commit()
        flash("ISRC обновлён", "success")

    return render_template("track_detail.html", track=track)

