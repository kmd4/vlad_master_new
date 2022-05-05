from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField
from wtforms.fields import EmailField
from wtforms.validators import DataRequired
from werkzeug.security import generate_password_hash, check_password_hash
from data.users import User


class RegisterForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    name = StringField('Имя пользователя', validators=[DataRequired()])
    submit_reg = SubmitField('Registation')
    submit_log = SubmitField('have account')

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired(message="Email required")])
    password = PasswordField('Пароль', validators=[DataRequired(message="Password required")])
    submit = SubmitField('Войти')