import os
import uuid
from flask import Blueprint, render_template, redirect, request, url_for, flash, abort, send_from_directory
from flask_login import login_required, current_user
from werkzeug.utils import safe_join
from models import db, Release, Track, Users
from client.forms import ReleaseForm, CreateSubForm, TrackForm, PromoForm, VideoForm, ProdbyForm, EditForm

from utils import delete_file, validate_audio, validate_image, validate_pdf

client = Blueprint("client", __name__)
UPLOAD_FOLDER = "files"
MAX_SUB = 3


@client.route("/")
@login_required
def dashboard():
    if (current_user.is_artist or current_user.is_sub):
        return redirect(url_for("client.releases"))
    elif (current_user.is_moder):
        return redirect(url_for("moder.all_releases"))
    elif (current_user.is_admin):
        return redirect(url_for("admin.all_users"))


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
    if not (current_user.is_artist or current_user.is_sub):
        flash("Access denied")
        return redirect(url_for("client.dashboard"))

    sub_accounts = Users.query.filter_by(creator_id=current_user.id).all()
    usernames = list(map(lambda x: x.username, sub_accounts))
    user_ids = [current_user.id] + [u.id for u in sub_accounts]

    # Получаем фильтры из запроса
    status = request.args.get("status")
    username = request.args.get("username")
    title = request.args.get("title", "").strip()

    # Запрос релизов, привязанных к нужным пользователям
    query = Release.query.join(Users).filter(Release.user_id.in_(user_ids))

    # Фильтрация по статусу
    if status and status.isdigit():
        query = query.filter(Release.status == int(status))

    # Фильтрация по username владельца релиза
    if username:
        query = query.filter(Users.username.ilike(f"%{username}%"))

    # Фильтрация по названию релиза
    if title:
        query = query.filter(Release.title.ilike(f"%{title}%"))

    # Сортировка по дате релиза
    releases = query.order_by(Release.release_date.desc()).all()

    return render_template(
        "releases.html",
        releases=releases,
        status_filter=status or "",
        username_filter=username or "",
        title_filter=title,
        usernames=usernames,
        main_username=current_user.username
    )



@client.route("/create_release", methods=["GET", "POST"])
@login_required
def create_release():
    if not (current_user.is_artist or current_user.is_sub):
        flash("Access denied")
        return redirect(url_for("client.dashboard"))

    form = ReleaseForm()
    
    if request.method == "POST" and form.validate_on_submit():
        cover_rel_path = None

        cover_error = validate_image(form.cover.data)
        if cover_error:
            flash(cover_error)
            return render_template("create_release.html", form=form)

        ext = os.path.splitext(form.cover.data.filename)[1]
        unique_cover_filename = f"{uuid.uuid4().hex}{ext}"
        cover_rel_path = f"covers/{unique_cover_filename}"
        cover_full_path = os.path.join(UPLOAD_FOLDER, cover_rel_path)
        os.makedirs(os.path.dirname(cover_full_path), exist_ok=True)
        form.cover.data.stream.seek(0)
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
            cover_path=cover_rel_path,
            user_id=current_user.id,
            comment=form.comment.data,
            status=1
        )
        db.session.add(release)
        db.session.commit()

        track_index = 0
        while f"tracks-{track_index}-title" in request.form:
            # Инициализация формы
            track_form = TrackForm(formdata=None)
            track_form.title.data = request.form.get(f"tracks-{track_index}-title")
            track_form.version.data = request.form.get(f"tracks-{track_index}-version")
            track_form.main_artists.data = request.form.get(f"tracks-{track_index}-main_artists")
            track_form.featured_artists.data = request.form.get(f"tracks-{track_index}-featured_artists")
            track_form.author.data = request.form.get(f"tracks-{track_index}-author")
            track_form.composer.data = request.form.get(f"tracks-{track_index}-composer")
            track_form.tiktok_start.data = request.form.get(f"tracks-{track_index}-tiktok_start")
            track_form.isrc.data = request.form.get(f"tracks-{track_index}-isrc")
            track_form.explicit.data = request.form.get(f"tracks-{track_index}-explicit")

            audio_file = request.files.get(f"tracks-{track_index}-audio_file")
            pdf_file = request.files.get(f"tracks-{track_index}-pdf_file")

            audio_error = validate_audio(audio_file)
            if audio_error:
                flash(f"Трек {track_index + 1}: {audio_error}")
                return render_template("create_release.html", form=form)

            pdf_error = validate_pdf(pdf_file)
            if pdf_error:
                flash(f"Трек {track_index + 1}: {pdf_error}")
                return render_template("create_release.html", form=form)

            audio_rel_path = None
            pdf_rel_path = None

            if audio_file:
                audio_ext = os.path.splitext(audio_file.filename)[1]
                unique_audio_filename = f"{uuid.uuid4().hex}{audio_ext}"
                audio_rel_path = f"audio/{unique_audio_filename}"
                audio_full_path = os.path.join(UPLOAD_FOLDER, audio_rel_path)
                os.makedirs(os.path.dirname(audio_full_path), exist_ok=True)
                audio_file.save(audio_full_path)

            if pdf_file:
                pdf_ext = os.path.splitext(pdf_file.filename)[1]
                unique_pdf_filename = f"{uuid.uuid4().hex}{pdf_ext}"
                pdf_rel_path = f"pdfs/{unique_pdf_filename}"
                pdf_full_path = os.path.join(UPLOAD_FOLDER, pdf_rel_path)
                os.makedirs(os.path.dirname(pdf_full_path), exist_ok=True)
                pdf_file.save(pdf_full_path)

            track = Track(
                title=track_form.title.data,
                version=track_form.version.data,
                main_artists=track_form.main_artists.data,
                featured_artists=track_form.featured_artists.data,
                author=track_form.author.data,
                composer=track_form.composer.data,
                tiktok_start=track_form.tiktok_start.data if track_form.tiktok_start.data else None,
                isrc=track_form.isrc.data,
                explicit=track_form.explicit.data == "True",
                audio_path=audio_rel_path,
                pdf_path=pdf_rel_path,
                release_id=release.id
            )
            db.session.add(track)
            track_index += 1

        db.session.commit()
        flash("Релиз успешно создан")
        return redirect(url_for("client.dashboard"))

    return render_template("create_release.html", form=form)



@client.route('/delete_release/<int:release_id>', methods=['POST'])
@login_required
def delete_release(release_id):
    release = Release.query.get_or_404(release_id)
    
    if not (current_user.is_admin or current_user.id == release.user_id):
        flash("У вас нет прав на удаление этого релиза.")
        return redirect(url_for('client.release_detail', release_id=release_id))

    # files
    cover_full_path = os.path.join(UPLOAD_FOLDER, release.cover_path)
    delete_file(cover_full_path)
    
    for track in release.tracks:
        if track.pdf_path:
            pdf_full_path = os.path.join(UPLOAD_FOLDER, track.pdf_path)
            delete_file(pdf_full_path)
        
        if track.audio_path:
            audio_full_path = os.path.join(UPLOAD_FOLDER, track.audio_path)
            delete_file(audio_full_path)

    # db
    for track in release.tracks:
        db.session.delete(track)

    db.session.delete(release)
    db.session.commit()
    
    flash("Релиз и все его треки удалены.")
    return redirect(url_for('client.releases'))


@client.route("/release/<int:release_id>", methods=["GET", "POST"])
@login_required
def release(release_id):
    release = Release.query.filter_by(id=release_id, user_id=current_user.id).first_or_404()
    
    if not (current_user.is_artist or current_user.is_sub):
        flash("Access denied")
        return redirect(url_for("client.dashboard"))
    
    if release.status in [2, 3, 4]:
        promo_form = PromoForm()
        video_form = VideoForm()
        prodby_form = ProdbyForm()
        edit_form = EditForm()

        
        if request.method == "POST" and promo_form.validate_on_submit():
            release.promo1 = promo_form.promo1.data
            release.promo2 = promo_form.promo2.data
            release.promo3 = promo_form.promo3.data
            
            release.status = 4
            
            db.session.commit()
            flash("Запрос на промо добавлен")
            
        if request.method == "POST" and video_form.validate_on_submit():
            release.video = video_form.video.data
            
            release.status = 4
            
            db.session.commit()
            flash("Запрос на видеошот добавлен")
            
        if request.method == "POST" and edit_form.validate_on_submit():
            release.edit = edit_form.edit.data
            
            release.status = 4
            
            db.session.commit()
            flash("Запрос на изменение добавлен")
            
        if request.method == "POST" and prodby_form.validate_on_submit():
            release.prodby = prodby_form.prodby.data
            
            release.status = 4
            
            db.session.commit()
            flash("Запрос на prodby добавлен")
            
        
        return render_template("release.html", 
                               release=release, 
                               promo_form=promo_form, 
                               video_form=video_form,
                               prodby_form=prodby_form,
                               edit_form=edit_form)
    
    return render_template("release.html", release=release)


@client.route("/release/<int:release_id>/edit", methods=["GET", "POST"])
@login_required
def edit_release(release_id):
    release = Release.query.filter_by(id=release_id, user_id=current_user.id).first_or_404()

    if not (current_user.is_artist or current_user.is_sub):
        flash("Access denied")
        return redirect(url_for("client.dashboard"))

    if release.status not in [0, 1]:
        flash("Access denied")
        return redirect(url_for("client.dashboard"))

    form = ReleaseForm()

    if request.method == "POST" and form.validate_on_submit():
        release.title = form.title.data
        release.version = form.version.data
        release.main_artists = form.main_artists.data
        release.featured_artists = form.featured_artists.data
        release.copyright = form.copyright.data
        release.genre = form.genre.data
        release.release_type = form.release_type.data
        release.release_date = form.release_date.data
        release.upc = form.upc.data
        release.comment = form.comment.data

        if form.cover.data:
            cover_error = validate_image(form.cover.data)
            if cover_error:
                flash(cover_error)
                return render_template("edit_release.html", form=form, release=release)

            ext = os.path.splitext(form.cover.data.filename)[1]
            unique_cover_filename = f"{uuid.uuid4().hex}{ext}"
            cover_rel_path = f"covers/{unique_cover_filename}"
            cover_full_path = os.path.join(UPLOAD_FOLDER, cover_rel_path)
            os.makedirs(os.path.dirname(cover_full_path), exist_ok=True)
            form.cover.data.stream.seek(0)
            form.cover.data.save(cover_full_path)
            release.cover_path = cover_rel_path

        Track.query.filter_by(release_id=release.id).delete()

        track_index = 0
        while f"tracks-{track_index}-title" in request.form:
            track_form = TrackForm(formdata=None)
            track_form.title.data = request.form.get(f"tracks-{track_index}-title")
            track_form.version.data = request.form.get(f"tracks-{track_index}-version")
            track_form.main_artists.data = request.form.get(f"tracks-{track_index}-main_artists")
            track_form.featured_artists.data = request.form.get(f"tracks-{track_index}-featured_artists")
            track_form.author.data = request.form.get(f"tracks-{track_index}-author")
            track_form.composer.data = request.form.get(f"tracks-{track_index}-composer")
            track_form.tiktok_start.data = request.form.get(f"tracks-{track_index}-tiktok_start")
            track_form.isrc.data = request.form.get(f"tracks-{track_index}-isrc")
            track_form.explicit.data = request.form.get(f"tracks-{track_index}-explicit")

            audio_file = request.files.get(f"tracks-{track_index}-audio_file")
            pdf_file = request.files.get(f"tracks-{track_index}-pdf_file")

            audio_error = validate_audio(audio_file)
            if audio_error:
                flash(f"Трек {track_index + 1}: {audio_error}")
                return render_template("edit_release.html", form=form, release=release)

            pdf_error = validate_pdf(pdf_file)
            if pdf_error:
                flash(f"Трек {track_index + 1}: {pdf_error}")
                return render_template("edit_release.html", form=form, release=release)

            audio_rel_path = None
            pdf_rel_path = None

            if audio_file:
                audio_ext = os.path.splitext(audio_file.filename)[1]
                unique_audio_filename = f"{uuid.uuid4().hex}{audio_ext}"
                audio_rel_path = f"audio/{unique_audio_filename}"
                audio_full_path = os.path.join(UPLOAD_FOLDER, audio_rel_path)
                os.makedirs(os.path.dirname(audio_full_path), exist_ok=True)
                audio_file.save(audio_full_path)

            if pdf_file:
                pdf_ext = os.path.splitext(pdf_file.filename)[1]
                unique_pdf_filename = f"{uuid.uuid4().hex}{pdf_ext}"
                pdf_rel_path = f"pdfs/{unique_pdf_filename}"
                pdf_full_path = os.path.join(UPLOAD_FOLDER, pdf_rel_path)
                os.makedirs(os.path.dirname(pdf_full_path), exist_ok=True)
                pdf_file.save(pdf_full_path)

            track = Track(
                title=track_form.title.data,
                version=track_form.version.data,
                main_artists=track_form.main_artists.data,
                featured_artists=track_form.featured_artists.data,
                author=track_form.author.data,
                composer=track_form.composer.data,
                tiktok_start=track_form.tiktok_start.data if track_form.tiktok_start.data else None,
                isrc=track_form.isrc.data,
                explicit=track_form.explicit.data == "True",
                audio_path=audio_rel_path,
                pdf_path=pdf_rel_path,
                release_id=release.id
            )
            db.session.add(track)
            track_index += 1

        db.session.commit()
        flash("Релиз обновлён")
        return redirect(url_for("client.releases"))

    elif request.method == "GET":
        form.title.data = release.title
        form.version.data = release.version
        form.main_artists.data = release.main_artists
        form.featured_artists.data = release.featured_artists
        form.copyright.data = release.copyright
        form.genre.data = release.genre
        form.release_type.data = release.release_type
        form.release_date.data = release.release_date
        form.upc.data = release.upc
        form.comment.data = release.comment

    return render_template("edit_release.html", form=form, release=release)




@client.route('/delete_sub/<int:user_id>', methods=['POST'])
@login_required
def delete_sub(user_id):
    user = Users.query.get_or_404(user_id)

    if not current_user.is_artist:
        flash("Недоступно")
        return redirect(url_for('client.subs'))
    
    if not (user.is_sub and user.creator_id == current_user.id):
        flash("Пользователь недоступен")
        return redirect(url_for('client.subs'))

    for release in user.releases:
        
        cover_full_path = os.path.join(UPLOAD_FOLDER, release.cover_path)
        delete_file(cover_full_path)
        
        for track in release.tracks:
            if track.pdf_path:
                pdf_full_path = os.path.join(UPLOAD_FOLDER, track.pdf_path)
                delete_file(pdf_full_path)
            
            if track.audio_path:
                audio_full_path = os.path.join(UPLOAD_FOLDER, track.audio_path)
                delete_file(audio_full_path)
        
            db.session.delete(track)
            
        db.session.delete(release)

    db.session.delete(user)
    db.session.commit()
    
    flash("Пользователь и все связанные данные удалены.")
    return redirect(url_for('client.subs'))



@client.route("/subs", methods=["GET", "POST"])
@login_required
def subs():
    if not current_user.is_artist:
        flash("У вас нет доступа к этой странице")
        return redirect(url_for("client.dashboard"))

    users = Users.query.filter_by(creator_id=current_user.id).all()
    return render_template("subs.html", users=users)



@client.route("/create_subaccount", methods=["GET", "POST"])
@login_required
def create_sub():
    if not current_user.is_artist:
        flash("У вас нет доступа к этой страниц")
        return redirect(url_for("client.dashboard"))
    
    users = Users.query.filter_by(creator_id=current_user.id).all()
    if len(users) >= MAX_SUB:
        flash(f"Нельзя создать больше {MAX_SUB} сабаккаунтов")
        return redirect(url_for("client.dashboard"))

    form = CreateSubForm()
    if form.validate_on_submit():
        if Users.query.filter_by(username=form.username.data).first():
            flash("Пользователь уже существует.")
        else:
            new_user = Users(
                username=form.username.data,
                user_type="sub",
                creator_id=current_user.id,
            )
            new_user.set_password(form.password.data)
            db.session.add(new_user)
            db.session.commit()
            flash("Саб аккаунт создан.")
            return redirect(url_for("client.subs"))
    return render_template("create_sub.html", form=form)

