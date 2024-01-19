import os
import sqlite3

from flask import Flask, render_template, redirect, request, abort, flash, url_for
from werkzeug.utils import secure_filename
from data import db_session
from data.users import User
from data.classes import Classes, ClassesForm, ClassesprivForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from forms.login import LoginForm
from forms.user import RegisterForm
import requests
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = '4827c890c1b84580a2efd2fb7257aa8d'
login_manager = LoginManager()
login_manager.init_app(app)
UPLOAD_FOLDER = 'static/il/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def main():
    db_session.global_init('base.db')
    app.run()


@app.route("/")
def visit():
    return render_template("visit.html")


@login_manager.user_loader
def load_classes(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(Classes).get(id)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/login")
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('/feed')
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/feed  ")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)    


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route("/register", methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('registration.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('registration.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('registration.html', title='Регистрация', form=form)


@app.route("/feed", methods=['GET', 'POST'])
def feed():
    return render_template('news.html', title='Новости')


if __name__ == '__main__':
    main()
    app.run()
