import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Books(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'books'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    author_id = sqlalchemy.Column(sqlalchemy.Integer,
                                    sqlalchemy.ForeignKey("author.id"))
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    genre_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("genre.id"))
    date = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    price = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    cover = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    review = sqlalchemy.Column(sqlalchemy.TEXT(10000), nullable=True)

    author = orm.relation("Author")
    genre = orm.relation("Genre")
