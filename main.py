import os
import sqlite3

from flask import Flask, render_template, redirect, request, abort, flash, url_for
from werkzeug.utils import secure_filename
from data import db_session
from data.users import User
from data.news import News, NewsForm, NewsprivForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from forms.login import LoginForm
from forms.user import RegisterForm
import requests
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = '4827c890c1b84580a2efd2fb7257aa8d'
login_manager = LoginManager()
login_manager.init_app(app)



def main():
    db_session.global_init('base.db')
    app.run()


@app.route("/")
def visit():
    return render_template("visit.html")


@login_manager.user_loader
def load_news(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(News).get(id)


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
            return redirect("/feed")
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
            about=form.about.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('registration.html', title='Регистрация', form=form)

@app.route('/create_news',  methods=['GET', 'POST'])
@login_required
def add_news():
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == current_user.get_id()).first()
    if user.is_admin == 1:
        form = NewsForm()
        if form.validate_on_submit():
            db_sess = db_session.create_session()
            news = News()
            news.title = form.title.data
            news.content = form.content.data
            news.tags = form.tags.data
            news.is_private = form.is_private.data
            current_user.news.append(news)
            db_sess.merge(current_user)
            db_sess.commit()
            return redirect('/feed')
        return render_template('news_edit.html', title='Добавление новости',
                               form=form)
    return redirect('/feed')



@app.route('/news/<int:id>', methods=['GET', 'POST'])
@login_required
def viewing_news(id):
    form = NewsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id, News.is_private == False).first()
        if news:
            id = news.id
            title = news.title
            content = news.content
            name = news.user
            name = name.name
            created_date = news.created_date
            return render_template('view_news.html',
                            id=id, title1=title, content=content,
                            created_date=created_date, name=name,
                            title='Новость <int:id>'
                            )
        else:
            return render_template('notexist.html', title="Этой новости не сущетвует")

@app.route('/profile/<int:id>', methods=['GET'])
def viewing_profile(id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == id).first()
    news = db_sess.query(News).filter(News.user_id == id, News.is_private != True)
    return render_template('profile.html', news=news, user=user)



@app.route("/feed", methods=['GET', 'POST'])
def feed():
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.is_private == False)
    return render_template("news.html", news=news, title='Главная')


if __name__ == '__main__':
    main()
    app.run()
