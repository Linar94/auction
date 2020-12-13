from ..db_utils import db


class UserModel(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(), index=True)
    email = db.Column(db.String(), index=True)
    pswd = db.Column(db.String())
