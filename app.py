from flask import Flask
from database import db
from auth import auth_bp
from presentation import presentation_bp
from analysis import analysis_bp

def create_app():
    app = Flask(__name__)

    
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:Nirvana2003.@localhost/presentation_app'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    app.config['MAX_CONTENT_LENGTH'] = 30 * 1024 * 1024 

    # Initialize extensions
    db.init_app(app)

    # Register Blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    app.register_blueprint(presentation_bp, url_prefix='/api') # <--- NEW REGISTRATION 2

    app.register_blueprint(analysis_bp, url_prefix='/api')

    return app

if __name__ == '__main__':
    app = create_app()
    
    with app.app_context():
        db.create_all()
        
    app.run(debug=True)

    