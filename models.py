from database import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'  

    
    userID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    passwordHash = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'
class Presentation(db.Model):
    __tablename__ = 'presentations'

    presentationID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userID = db.Column(db.Integer, db.ForeignKey('users.userID'), nullable=False)
    videoFile = db.Column(db.String(255), nullable=False) # Stores the filename/path
    uploadDate = db.Column(db.DateTime, default=datetime.utcnow)
    student = db.relationship('User', backref=db.backref('presentations', lazy=True))