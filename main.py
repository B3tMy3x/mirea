from flask import Flask, render_template, redirect, request, abort
from data import db_session
from data.users import User
from data.news import News, NewsForm
from data.opendotadata import getuserdata
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from forms.login import LoginForm
from forms.user import RegisterForm
import requests
import sqlite3

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'j821fjw09h1jkh72w6g190i3bf12'
TEMPLATES_AUTO_RELOAD = True


def guidedata(a):
    if len(a) == 10 and a.isnumeric():
        r = f"https://www.dota2.com/workshop/builds/view?embedded=workshop&publishedfileid={a}&target_uri=https://steamcommunity.com&l=english&u=public"
        r = requests.get(r)
        r = r.text
        r = r[r.find('<div id="itemBuildContent">'):r.find('</body>')]
        r = r.replace('</div>', '</div>\n')
        with open('templates/news.html', 'w', encoding='utf-8') as f:
            f.write('''{% extends "base.html" %}
    {% block content %}
    <br>
        <div class="di1">
            <div class="col-md6">
                <h1>{{news.title}}</h1>
                <div>
                    {{news.content}}
                </div>
                <center>''' +
            r +
            '''</center>
            <div>
                    <a href='/profile/{{ news.user_id }}'><button type="button" class="btn btn-outline-light">Автор - {{news.user.name}}, Дата написания - {{news.created_date}}</button></a>
                </div>
            </div>
            <br>
        </div>
    {% endblock %})
            ''')
    else:
        with open('templates/news.html', 'w', encoding='utf-8') as f:
            f.write('''{% extends "base.html" %}
    {% block content %}
    <br>
        <div class="di1">
            <div class="col-md6">
                <h1>{{news.title}}</h1>
                <div>
                    {{news.content}}
                </div>
                <br>
                <div>
                    <a href='/profile/{{ news.user_id }}'><button type="button" class="btn btn-outline-light">Автор - {{news.user.name}}, Дата написания - {{news.created_date}}</button></a>                <div>
            </div>
        <br>
        </div>
    {% endblock %})''')
    f.close()


def main():
    db_session.global_init('C:/Users/Student/Desktop/db-master/db-main/db')
    app.run()


def is_admin():
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == current_user.get_id()).first()
    if str(type(user)) == "<class 'NoneType'>":
        return False
    elif user.role == "admin":
        return True
    return False


@app.route("/")
def visit():
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.is_private != True)
    return render_template("main.html", news=news)
    if current_user.is_authenticated:
        return redirect('/feed')


@app.route("/feed")
def index():
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.is_private != True)
    return render_template("index.html", news=news, role=is_admin(), id=current_user.get_id())
    if current_user.is_authenticated:
        news = db_sess.query(News).filter(
            (News.user == current_user) | (News.is_private != True))
    else:
        news = db_sess.query(News).filter(News.is_private != True)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data,
            steam_id=form.steam_id.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


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


@app.route('/news_edit',  methods=['GET', 'POST'])
@login_required
def add_news():
    form = NewsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = News()
        news.title = form.title.data
        news.content = form.content.data
        news.build = form.build.data
        news.is_private = form.is_private.data
        current_user.news.append(news)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/feed')
    return render_template('news_edit.html', title='Добавление новости',
                           form=form)


@app.route('/news/<int:id>', methods=['GET', 'POST'])
@login_required
def viewing_news(id):
    form = NewsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id, News.is_private != True).first()
        if news:
            form.title.data = news.title
            form.content.data = news.content
            form.build.data = news.build
            guidedata(news.build)
            form.is_private.data = news.is_private
        else:
            abort(404)
    return render_template('news.html',
                           news=news,
                           title='Редактирование новости'
                           )


@app.route('/drafts')
@login_required
def viewing_drafts():
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.user_id == current_user.get_id(), News.is_private == True)
    return render_template("drafts.html", news=news, role=is_admin(), id=current_user.get_id(), true=True)
    if current_user.is_authenticated:
        news = db_sess.query(News).filter(
            (News.user == current_user) | (News.is_private != True))
    else:
        news = db_sess.query(News).filter(News.is_private != True)


@app.route('/news_edit/<int:id>', methods=['GET', 'POST'])
@login_required
def news_edit(id):
    form = NewsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
        news1 = db_sess.query(News).filter(News.id == id).first()
        if news or is_admin():
            form.title.data = news1.title
            form.content.data = news1.content
            form.build.data = news1.build
            form.is_private.data = news1.is_private
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user).first()
        news1 = db_sess.query(News).filter(News.id == id).first()
        if news or is_admin():
            news1.title = form.title.data
            news1.content = form.content.data
            news1.build = form.build.data
            news1.is_private = form.is_private.data
            db_sess.commit()
            return redirect('/feed')
        else:
            abort(404)
    return render_template('news_edit.html',
                           title='Редактирование новости',
                           form=form
                           )


@app.route('/profile/<int:id>', methods=['GET'])
def viewing_profile(id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == id).first()
    news = db_sess.query(News).filter(News.user_id == id, News.is_private != True)
    data = getuserdata(user.steam_id)
    return render_template('profile.html',
                           steam=data[0],
                           rank=data[1],
                           avatar=data[2],
                           news=news,
                           user=user,
                           title='Редактирование новости'
                           )


@app.route('/news_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.id == id,
                                      News.user == current_user
                                      ).first()
    if news or is_admin():
        db_sess.delete(db_sess.query(News).filter(News.id == id).first())
        db_sess.commit()
    else:
        abort(404)
    return redirect('/feed')


if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    main()
    app.run()
