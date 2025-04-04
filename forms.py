from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length

# Форма для контактов
class ContactForm(FlaskForm):
    name = StringField("Имя", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    message = StringField("Сообщение", validators=[DataRequired(), Length(min=10)])
    submit = SubmitField("Отправить")

# Форма регистрации
class RegisterForm(FlaskForm):
    username = StringField("Имя пользователя", validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Пароль", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField("Подтвердите пароль", validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField("Зарегистрироваться")

# Форма входа
class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Пароль", validators=[DataRequired()])
    submit = SubmitField("Войти")
