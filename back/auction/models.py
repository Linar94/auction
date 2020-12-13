import sqlalchemy

from ..db_utils import db


class AuctionModel(db.Model):
    __tablename__ = 'auctions'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(), index=True)
    owner = db.Column(db.Integer(), db.ForeignKey('users.id'), index=True)
    steps = db.Column(db.Integer())
    price = db.Column(db.Integer())
    created = db.Column(db.DateTime(), index=True, server_default='now()')
    is_active = db.Column(db.Boolean(), index=True)
    end = db.Column(db.DateTime(), index=True, nullable=True)


class BetModel(db.Model):
    __tablename__ = 'bets'

    id = db.Column(db.Integer(), primary_key=True)
    auction = db.Column(db.Integer(), db.ForeignKey('auctions.id'), index=True)
    user = db.Column(db.Integer(), db.ForeignKey('users.id'), index=True)
    price = db.Column(db.Integer())
    created = db.Column(db.DateTime(), index=True, server_default=sqlalchemy.sql.func.now())
