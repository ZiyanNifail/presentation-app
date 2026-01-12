from flask import Flask
from database import db
from models import User

# 1. Setup a dummy Flask app context
app = Flask(__name__)

# REPLACE these with your actual MySQL username and password
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:Nirvana2003.@localhost/presentation_app'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# 2. Test the connection
with app.app_context():
    try:
        # Create tables based on our models
        db.create_all()
        print("✅ Connection successful! Tables created.")

        # Create a dummy user
        new_user = User(username="TestStudent", email="test@msu.edu.my", passwordHash="hashed_secret_123")
        
        # Add to session and commit (save)
        db.session.add(new_user)
        db.session.commit()
        print(f"✅ Dummy user '{new_user.username}' created with ID: {new_user.userID}")

    except Exception as e:
        print(f"❌ Error: {e}")