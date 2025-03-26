import sqlite3
import os
from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Путь к базе данных users.db
db_path = os.path.join(app.instance_path, 'users.db')

# Проверяем, существует ли папка instance
if not os.path.exists(app.instance_path):
    os.makedirs(app.instance_path)

# Подключение к базе данных
connection = sqlite3.connect(db_path, check_same_thread=False)
sql = connection.cursor()

# Создание таблиц, если их нет
sql.execute('''CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)''')

sql.execute('''CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    subject TEXT NOT NULL,
    message TEXT NOT NULL
)''')

connection.commit()

# Создание администратора, если его нет
admin_email = 'admin@gmail.com'
admin_password = 'admin123'
sql.execute("SELECT * FROM users WHERE email = ?", (admin_email,))
if not sql.fetchone():
    sql.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                ('Администратор', admin_email, admin_password))
    connection.commit()


# Проверка пользователя при входе
def check_user(email, password):
    sql.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
    return sql.fetchone()


# Проверка, существует ли пользователь
def user_exists(email):
    sql.execute("SELECT id FROM users WHERE email = ?", (email,))
    return sql.fetchone() is not None


# Главная страница
@app.route('/')
def index():
    return render_template('index.html')


# Страницы с услугами
@app.route('/services/apartment')
def apartment():
    return render_template('apartment.html')


@app.route('/services/office')
def office():
    return render_template('office.html')


@app.route('/services/electric')
def electric():
    return render_template('electric.html')


# Контактная форма
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')

        if name and email and subject and message:
            sql.execute("INSERT INTO messages (name, email, subject, message) VALUES (?, ?, ?, ?);",
                        (name, email, subject, message))
            connection.commit()
            flash('✅ Ваше сообщение отправлено!', 'success')
        else:
            flash('❌ Пожалуйста, заполните все поля.', 'danger')

        return redirect(url_for('contact'))
    return render_template('contact.html')


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
            sql.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?);",
                        (username, email, password))
            connection.commit()
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
            session['user'] = user[1]  # Имя пользователя
            session['email'] = user[2]  # Email пользователя

            flash(f'✅ Добро пожаловать, {user[1]}!', 'success')

            # Если email совпадает с администратором, перенаправляем на админ-панель
            if user[2] == 'admin@example.com':
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


# Панель администратора (просмотр сообщений)
@app.route('/admin/panel')
def admin_panel():
    if session.get('email') != 'admin@example.com':
        flash('❌ Доступ запрещён. Только для администратора.', 'danger')
        return redirect(url_for('index'))

    sql.execute("SELECT * FROM messages;")
    messages = sql.fetchall()
    return render_template('admin_panel.html', messages=messages)


if __name__ == '__main__':
    app.run(debug=True)
