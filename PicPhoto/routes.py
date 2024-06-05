from flask import redirect, render_template, url_for, request, flash
from PicPhoto import app, database, bcrypt
from flask_login import login_required, logout_user, login_user, current_user
from PicPhoto.forms import FormLogin, FormRegister, FormPhoto
from PicPhoto.models import User, Photo
from werkzeug.utils import secure_filename
import boto3
import os

# Configuração do S3
s3 = boto3.client(
    's3',
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
    region_name=os.environ.get('AWS_REGION')
)
S3_BUCKET = os.environ.get('S3_BUCKET_NAME')

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
            # Substitua o armazenamento local por upload para S3
            try:
                s3.upload_fileobj(
                    file,
                    S3_BUCKET,
                    safe_name,
                    ExtraArgs={"ACL": "public-read"}
                )
                file_url = f"https://{S3_BUCKET}.s3.amazonaws.com/{safe_name}"
                
                photo = Photo(image=file_url, id_user=current_user.id)
                database.session.add(photo)
                database.session.commit()

                flash("Photo uploaded successfully!", "success")
            except Exception as e:
                flash(f"An error occurred: {str(e)}", "danger")
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
