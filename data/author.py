import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Author(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'author'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    surname = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    years = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    list_of_books = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    books = orm.relation("Books", back_populates='author')
