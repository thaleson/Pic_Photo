from flask import redirect, render_template, url_for, request, flash, make_response, send_file
from PicPhoto import app, database, bcrypt
from flask_login import login_required, logout_user, login_user, current_user
from PicPhoto.forms import FormLogin, FormRegister, FormPhoto
from PicPhoto.models import User, Photo
import os
from werkzeug.utils import secure_filename
import io

@app.after_request
def add_permissions_policy_header(response):
    response.headers['Permissions-Policy'] = 'interest-cohort=()'
    return response

@app.route("/", methods=["GET", "POST"])
def homepage():
    formlogin = FormLogin()

    if formlogin.validate_on_submit():
        user = User.query.filter_by(email=formlogin.email.data).first()
        if user and bcrypt.check_password_hash(user.password, formlogin.senha.data):
            login_user(user, remember=True)
            return redirect(url_for("perfil", id_user=user.id))
    return render_template("homepage.html", form=formlogin)

@app.route("/criar-conta", methods=["GET", "POST"])
def createacount(): 
    formregister = FormRegister()
    if formregister.validate_on_submit():
        password = bcrypt.generate_password_hash(
            formregister.senha.data).decode('utf-8')
        user = User(username=formregister.username.data,
                    password=password,
                    email=formregister.email.data)

        database.session.add(user)
        database.session.commit()
        login_user(user, remember=True)
        return redirect(url_for("perfil", id_user=user.id))

    return render_template("criar-conta.html", form=formregister)

@app.route("/perfil/<int:id_user>", methods=["GET", "POST"])
@login_required
def perfil(id_user):
    if int(id_user) == int(current_user.id):
        form_photos = FormPhoto()

        if form_photos.validate_on_submit():
            file = form_photos.foto.data
            safe_name = secure_filename(file.filename)
            file_data = file.read()

            photo = Photo(image_data=file_data, image_name=safe_name, id_user=current_user.id)
            database.session.add(photo)
            database.session.commit()

            flash("Photo uploaded successfully!", "success")
            return redirect(url_for("perfil", id_user=current_user.id))

        return render_template("perfil.html", usuario=current_user, form=form_photos)
    else:
        usuario = User.query.get(int(id_user))
        if usuario is None:
            return redirect(url_for("homepage"))  # Redirect if user not found
    return render_template("perfil.html", usuario=usuario, form=None)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("homepage"))

@app.route("/feed")
@login_required
def feed():
    photos = Photo.query.order_by(Photo.creation_date).all()
    return render_template("feed.html", photos=photos)

@app.route("/photo/<int:photo_id>")
def serve_photo(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    return send_file(io.BytesIO(photo.image_data), mimetype='image/jpeg', attachment_filename=photo.image_name)
