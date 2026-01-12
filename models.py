from database import db

class User(db.Model):
    __tablename__ = 'users'  

    
    userID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    passwordHash = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'