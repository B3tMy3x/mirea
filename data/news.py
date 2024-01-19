import datetime
import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired


class NewsForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    content = TextAreaField("Содержание")
    tags = StringField("Теги")
    is_private = BooleanField("Черновик")
    submit = SubmitField("Применить")


class NewsprivForm(FlaskForm):
    is_private = BooleanField("Приватная лекция")


class News(SqlAlchemyBase):
    __tablename__ = 'news'
    categories = orm.relationship("Category",
                                  secondary="association",
                                  backref="news")
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    content = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    tags = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    a = str(datetime.datetime.now())
    a = a[:19]
    created_date = sqlalchemy.Column(sqlalchemy.String,
                                     default=a)
    is_private = sqlalchemy.Column(sqlalchemy.Boolean, default=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    user = orm.relationship('User')
