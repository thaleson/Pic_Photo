from flask import redirect, render_template, url_for, request, flash
from PicPhoto import app, database, bcrypt
from flask_login import login_required, logout_user, login_user, current_user
from PicPhoto.forms import FormLogin, FormRegister, FormPhoto
from PicPhoto.models import User, Photo
import os
from werkzeug.utils import secure_filename


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
            path = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                app.config["UPLOAD_FOLDER"])
            if not os.path.exists(path):
                os.makedirs(path)  # Create the directory if it doesn't exist

            file_path = os.path.join(path, safe_name)
            file.save(file_path)

            photo = Photo(image=safe_name, id_user=current_user.id)
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
    return render_template("feed.html",photos=photos)