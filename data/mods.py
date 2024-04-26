import datetime
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


class Mod(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'mods'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    mod_id = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    version = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    loader = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    game_version = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    min_loader_version = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    uploaded_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    filename = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    user = orm.relationship('User')
    comments = orm.relationship('Comment', back_populates='mod')

    def get_rate(self):
        rate = []
        for i in self.comments:
            rate.append(i.rate)
        if len(rate) == 0:
            return 0.0
        return round(sum(rate) / len(rate), 1)
