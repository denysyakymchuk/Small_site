from app import db

from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash



class User(UserMixin, db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(50), index=True, unique=True)
  email = db.Column(db.String(150), unique=True, index=True)
  password_hash = db.Column(db.String(150))
  joined_at = db.Column(db.DateTime(), default=datetime.utcnow, index=True)

  def set_password(self, password):
        self.password_hash = generate_password_hash(password)

  def check_password(self,password):
      return check_password_hash(self.password_hash,password)

  def __repr__(self):
      return '<User %r>' % self.username



class Products(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.Text)
    price = db.Column(db.Integer)
    free_size = db.Column(db.String)
    how = db.Column(db.Integer)
    img = db.Column(db.Text)
    img1 = db.Column(db.Text)
    img2 = db.Column(db.Text)
    img3 = db.Column(db.Text)
    img4 = db.Column(db.Text)
    img5 = db.Column(db.Text)
    img6 = db.Column(db.Text)


    def __repr__(self):
        return '<Product %r>' % self.id
