#from hashlib import md5
from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import base64
from datetime import datetime,timedelta
import os

class User(UserMixin, db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(256))

    # Der aktuelle API-Token in der Datenbank
    token = db.Column(db.String(32), index=True, unique=True) 
    # Das Ablaufdatum des Token in der Datenbank 
    token_expiration = db.Column(db.DateTime)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # need to be overwritten, because flask-login needs this info
    def get_id(self):
        return str(self.user_id)
    
    # Token erzeugen, speichern und zurückgeben
    def get_token(self, expires_in=3600):
        now=datetime.utcnow()
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token
        self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        return self.token
    
    # Token ungültig machen
    def revoke_token(self):
        # Ablaufdatum auf aktuelle Zeit - 1 sek. setzen
        self.token_expiration = datetime.utcnow() - timedelta(seconds=1)
    
    # Token prüfen
    @staticmethod
    def check_token(token):
        user = User.query.filter_by(token=token).first()
        if user is None or user.token_expiration < datetime.utcnow():
            return None # Token nicht gefunden oder abgelaufen
        return user     # Token ist gültig
    


@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Category(db.Model):
    category_id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(140), index=True, unique=True)
    links = db.relationship('Link', back_populates='category')

    def __repr__(self):
        return '<Category {}>'.format(self.category)

class Link(db.Model):
    link_id = db.Column(db.Integer, primary_key=True)
    link = db.Column(db.String(250), index=True, unique=True)
    keywords = db.Column(db.String(250))
    id_category = db.Column(db.Integer, db.ForeignKey('category.category_id'))
    category = db.relationship('Category', back_populates='links')

    def __repr__(self):
        return '<Link {}>'.format(self.link)

    def to_dict(self):
        data = { 
            'link': self.link,
            'keywords': self.keywords
            # next step - how to to add all the categories
        }
        return data

    @staticmethod
    def to_collection():
        links = Link.query.all()
        data = {'links':[link.to_dict() for link in links]}
        return(data)