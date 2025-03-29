from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Конфигурация базы данных
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'instance', 'users.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# Модели базы данных
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)


class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)


# Создание таблиц
with app.app_context():
    db.create_all()

    # Создание администратора, если его нет
    admin_email = 'admin@example.com'
    admin_password = 'admin123'
    if not User.query.filter_by(email=admin_email).first():
        admin = User(username='Администратор', email=admin_email, password=admin_password)
        db.session.add(admin)
        db.session.commit()


# Проверка пользователя при входе
def check_user(email, password):
    return User.query.filter_by(email=email, password=password).first()


# Проверка существования пользователя
def user_exists(email):
    return User.query.filter_by(email=email).first() is not None


# Главная страница
@app.route('/')
def index():
    return render_template('index.html', user=session.get('user'))


# Карточки услуг
@app.route('/services/apartment')
def apartment():
    return render_template('apartment.html')


@app.route('/services/office')
def office():
    return render_template('office.html')


@app.route('/services/electric')
def electric():
    return render_template('electric.html')


# Форма контактов
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    subject = request.args.get('subject', '')

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')

        if name and email and subject and message:
            new_message = Message(name=name, email=email, subject=subject, message=message)
            db.session.add(new_message)
            db.session.commit()
            flash('✅ Ваше сообщение отправлено!', 'success')
        else:
            flash('❌ Пожалуйста, заполните все поля.', 'danger')

        return redirect(url_for('contact'))

    return render_template('contact.html', subject=subject)


# Регистрация
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        if not (username and email and password):
            flash('❌ Все поля обязательны для заполнения.', 'danger')
        elif user_exists(email):
            flash('❌ Пользователь с таким email уже зарегистрирован.', 'danger')
        else:
            new_user = User(username=username, email=email, password=password)
            db.session.add(new_user)
            db.session.commit()
            flash('✅ Регистрация успешна! Войдите в аккаунт.', 'success')
            return redirect(url_for('login'))

    return render_template('register.html')


# Вход пользователя и администратора
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = check_user(email, password)
        if user:
            session['user'] = user.username
            session['email'] = user.email
            flash(f'✅ Добро пожаловать, {user.username}!', 'success')
            if user.email == 'admin@example.com':
                return redirect(url_for('admin_panel'))
            return redirect(url_for('index'))
        else:
            flash('❌ Неверный email или пароль.', 'danger')

    return render_template('login.html')


# Выход пользователя
@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('email', None)
    flash('Вы вышли из системы.', 'info')
    return redirect(url_for('index'))


# Выход администратора
@app.route('/admin/logout')
def admin_logout():
    return redirect(url_for('logout'))


# Панель администратора
@app.route('/admin/panel')
def admin_panel():
    if session.get('email') != 'admin@example.com':
        flash('❌ Доступ запрещён. Только для администратора.', 'danger')
        return redirect(url_for('index'))

    users = User.query.all()
    messages = Message.query.all()
    services = Service.query.all()

    return render_template('admin_panel.html', users=users, messages=messages, services=services)


# Удаление сообщения (только для администратора)
@app.route('/admin/delete_message/<int:message_id>')
def delete_message(message_id):
    if session.get('email') != 'admin@example.com':
        flash('❌ Доступ запрещён.', 'danger')
        return redirect(url_for('index'))

    message = Message.query.get(message_id)
    if message:
        db.session.delete(message)
        db.session.commit()
        flash('✅ Сообщение удалено.', 'success')

    return redirect(url_for('admin_panel'))


# Удаление пользователя (только для администратора)
@app.route('/admin/delete_user/<int:user_id>')
def delete_user(user_id):
    if session.get('email') != 'admin@example.com':
        flash('❌ Доступ запрещён.', 'danger')
        return redirect(url_for('index'))

    user = User.query.get(user_id)
    if user and user.email != 'admin@example.com':
        db.session.delete(user)
        db.session.commit()
        flash('✅ Пользователь удалён.', 'success')

    return redirect(url_for('admin_panel'))


# Добавление услуги (только для администратора)
@app.route('/admin/add_service', methods=['POST'])
def add_service():
    if session.get('email') != 'admin@example.com':
        flash('❌ Доступ запрещён.', 'danger')
        return redirect(url_for('index'))

    title = request.form.get('title')
    description = request.form.get('description')

    if title and description:
        new_service = Service(title=title, description=description)
        db.session.add(new_service)
        db.session.commit()
        flash('✅ Услуга добавлена!', 'success')

    return redirect(url_for('admin_panel'))


# Удаление услуги (только для администратора)
@app.route('/admin/delete_service/<int:service_id>')
def delete_service(service_id):
    if session.get('email') != 'admin@example.com':
        flash('❌ Доступ запрещён.', 'danger')
        return redirect(url_for('index'))

    service = Service.query.get(service_id)
    if service:
        db.session.delete(service)
        db.session.commit()
        flash('✅ Услуга удалена!', 'success')

    return redirect(url_for('admin_panel'))


if __name__ == '__main__':
    app.run(debug=True)
