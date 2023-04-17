import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase


class Form(SqlAlchemyBase):
    __tablename__ = 'form'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    age = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    locality = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    sex = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    photo_id = sqlalchemy.Column(sqlalchemy.String, nullable=True)
