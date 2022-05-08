from dotenv import load_dotenv

import time
from flask import Flask, render_template, redirect, url_for, flash
from flask_login import LoginManager, login_user, current_user, logout_user
from flask_socketio import SocketIO, join_room, leave_room, send

from data import db_session
from data.users import User
from data.messages import Messages
from forms.user import RegisterForm, LoginForm
from mail import send_email
from message_resources import *



app = Flask(__name__)
load_dotenv()
api = Api(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)
socketio = SocketIO(app, manage_session=False, cors_allowed_origins='*')

# Predefined rooms for chat
ROOMS = []
user_id = None



@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/', methods=['GET', 'POST'])
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        # s = check_password(form.password.data)
        # if s != True:
        #     return render_template('register.html', title='Регистрация',
        #                            form=form,
        #                            message=s)
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first() or\
            db_sess.query(User).filter(User.name == form.name.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        send_email(form.email.data)
        user = User(
            name=form.name.data,
            email=form.email.data)
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    global ROOMS, user_id
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user :#and user.check_password(form.password.data):
            login_user(user)
            user_id = user.id
            db_sess.commit()
            ROOMS = user.dialogs.split(':')
            print(ROOMS)
            return redirect(url_for('chat'))
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)

    return render_template('login.html', title='Авторизация', form=form)


def check_password(pas):
    if len(pas) < 8: return 'Пароль слишком короткий'
    if pas.isdigit() or pas.isalpha(): return 'Пароль слишком простой. Надежный пароль содержит латинские буквы и цифры'
    return True


@app.route("/logout", methods=['GET'])
def logout():

    # Logout user
    logout_user()
    flash('You have logged out successfully', 'success')
    return redirect(url_for('login'))


@app.route("/chat", methods=['GET', 'POST'])
def chat():
    if not current_user.is_authenticated:
        flash('Please login', 'danger')
        return redirect(url_for('login'))

    return render_template("chat.html", username=current_user.name, rooms=ROOMS)


@socketio.on('incoming-msg')
def on_message(data):
    """Broadcast messages"""
    print(f"Message: {data}")

    msg = data["msg"]
    username = data["username"]
    room = data["room"]
    # Set timestamp
    time_stamp = time.strftime('%b-%d %I:%M%p', time.localtime())
    send({"username": username, "msg": msg + '12', "time_stamp": time_stamp}, room=room, broadcast=True)
    message = Messages(content=msg,  room=room, user_id=user_id, created_date=time_stamp, username=username)
    db_sess = db_session.create_session()
    db_sess.add(message)
    db_sess.commit()



@socketio.on('join')
def on_join(data):
    """User joins a room"""
    print(data)
    room = data["room"]
    username = data['username']
    join_room(room)
    # Broadcast that new user has joined
    db_sess = db_session.create_session()
    messs = db_sess.query(Messages.content, Messages.user_id, Messages.room, Messages.created_date, Messages.username).all()
    mess_fil = list(filter(lambda x: (x[1] == user_id and (x[2] == room or x[2] == 'My_notes')) or (room != 'My_notes' and x[1] == int(room) and x[2] == user_id), messs))
    mess_fil = list(map(lambda x: {"username": x[4], 'msg': x[0], 'time_stamp': x[3]}, mess_fil))
    print(mess_fil)
    for i in range(len(mess_fil)):
         send(mess_fil[i], room=room, broadcast=True)
    #
    # send({"msg": " has joined the " + str(room) + " room."}, room=room)


@socketio.on('leave')
def on_leave(data):
    """User leaves a room"""

    username = data['username']
    room = data['room']
    leave_room(room)
    # send({"msg": username + " has left the room"}, room=room)


if __name__ == '__main__':
    db_session.global_init("db/blogs.db")
    app.run(port=8080, host='127.0.0.1')
