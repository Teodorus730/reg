import os
import uuid
from flask import Blueprint, render_template, redirect, request, url_for, flash, abort, send_from_directory
from flask_login import login_required, current_user
from werkzeug.utils import safe_join
from models import db, Release, Track
from client.forms import ReleaseForm

client = Blueprint("client", __name__)
UPLOAD_FOLDER = "files"  # Это относительная папка в корне проекта


@client.route("/")
@login_required
def dashboard():
    return render_template("dashboard.html", user=current_user)


@client.route('/uploads/<path:filename>')
@login_required
def uploaded_file(filename):
    if not filename:
        abort(400, "Файл не указан")

    files_dir = os.path.join(os.getcwd(), UPLOAD_FOLDER)  # абсолютный путь к "files"
    full_path = safe_join(files_dir, filename)

    if not full_path or not os.path.isfile(full_path):
        abort(404, f"Файл не найден: {filename}")

    directory, file = os.path.split(full_path)
    return send_from_directory(directory, file)


@client.route("/releases")
@login_required
def releases():
    releases = Release.query.filter_by(user_id=current_user.id).all()
    return render_template("releases.html", releases=releases)


@client.route("/create_release", methods=["GET", "POST"])
@login_required
def create_release():
    form = ReleaseForm()

    if request.method == "POST" and form.validate_on_submit():
        # Сохраняем обложку
        cover_rel_path = None
        if form.cover.data:
            ext = os.path.splitext(form.cover.data.filename)[1]
            unique_cover_filename = f"{uuid.uuid4().hex}{ext}"
            cover_rel_path = f"covers/{unique_cover_filename}"
            cover_full_path = os.path.join(UPLOAD_FOLDER, cover_rel_path)
            os.makedirs(os.path.dirname(cover_full_path), exist_ok=True)
            form.cover.data.save(cover_full_path)

        release = Release(
            title=form.title.data,
            version=form.version.data,
            main_artists=form.main_artists.data,
            featured_artists=form.featured_artists.data,
            copyright=form.copyright.data,
            genre=form.genre.data,
            release_type=form.release_type.data,
            release_date=form.release_date.data,
            upc=form.upc.data,
            cover_path=cover_rel_path,  # относительный путь
            user_id=current_user.id
        )
        db.session.add(release)
        db.session.commit()

        for track_form in form.tracks.entries:
            audio_rel_path = None
            pdf_rel_path = None

            if track_form.audio_file.data:
                audio_ext = os.path.splitext(track_form.audio_file.data.filename)[1]
                unique_audio_filename = f"{uuid.uuid4().hex}{audio_ext}"
                audio_rel_path = f"audio/{unique_audio_filename}"
                audio_full_path = os.path.join(UPLOAD_FOLDER, audio_rel_path)
                os.makedirs(os.path.dirname(audio_full_path), exist_ok=True)
                track_form.audio_file.data.save(audio_full_path)

            if track_form.pdf_file.data:
                pdf_ext = os.path.splitext(track_form.pdf_file.data.filename)[1]
                unique_pdf_filename = f"{uuid.uuid4().hex}{pdf_ext}"
                pdf_rel_path = f"pdfs/{unique_pdf_filename}"
                pdf_full_path = os.path.join(UPLOAD_FOLDER, pdf_rel_path)
                os.makedirs(os.path.dirname(pdf_full_path), exist_ok=True)
                track_form.pdf_file.data.save(pdf_full_path)

            track = Track(
                title=track_form.title.data,
                version=track_form.version.data,
                main_artists=track_form.main_artists.data,
                featured_artists=track_form.featured_artists.data,
                author=track_form.author.data,
                composer=track_form.composer.data,
                tiktok_start=int(track_form.tiktok_start.data) if track_form.tiktok_start.data else None,
                isrc=track_form.isrc.data,
                explicit=track_form.explicit.data == "True",
                audio_path=audio_rel_path,
                pdf_path=pdf_rel_path,
                release_id=release.id
            )
            db.session.add(track)

        db.session.commit()
        flash("Релиз успешно создан")
        return redirect(url_for("client.dashboard"))

    return render_template("create_release.html", form=form)
