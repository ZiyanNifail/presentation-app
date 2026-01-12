from flask import Flask
from database import db
from auth import auth_bp

def create_app():
    app = Flask(__name__)

    # Database Configuration (Update your password here if needed!)
    # Note: Using the same connection string you used in your test script
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:Nirvana2003.@localhost/presentation_app'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)

    # Register the Blueprints (Connects auth.py to the main app)
    app.register_blueprint(auth_bp, url_prefix='/auth')

    return app

if __name__ == '__main__':
    app = create_app()
    
    # Create tables if they don't exist yet (just in case)
    with app.app_context():
        db.create_all()
        
    # Run the server!
    app.run(debug=True)