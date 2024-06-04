from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError

from PicPhoto.models import User


class FormLogin(FlaskForm):
    email = StringField("E-mail", validators=[DataRequired(), Email()])
    senha = PasswordField("Senha", validators=[DataRequired()])
    botao_confirmaçao = SubmitField("Fazer login")


    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if not user:

            raise ValidationError(
                "Usuario inexistente,crie uma conta para continuar")


class FormRegister(FlaskForm):
    email = StringField("E-mail", validators=[DataRequired(), Email()])
    username = StringField("Nome de Usuário", validators=[DataRequired()])
    senha = PasswordField("Senha", validators=[DataRequired(), Length(6, 20)])
    confirmação_senha= PasswordField("Confirmação de senha", validators=[
                                      DataRequired(), EqualTo("senha")])
    botao_confirmaçao = SubmitField("Criar conta")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("Este e-mail já está em uso")


class FormPhoto(FlaskForm):
    foto = FileField("foto", validators=[DataRequired()])
    botao_confirmaçao = SubmitField("Enviar")
