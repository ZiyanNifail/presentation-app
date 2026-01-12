from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from database import db
from models import User

# Create a "Blueprint" - a group of related routes
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    # 1. Get data from the request (sent by Postman or Frontend)
    data = request.get_json()
    
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    # 2. Simple Validation
    if not username or not email or not password:
        return jsonify({"error": "Missing required fields"}), 400

    # 3. Check if user already exists
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 409

    # 4. Hash the password (Security!)
    # We never save "secret123" directly. We save a scrambled version.
    hashed_password = generate_password_hash(password)

    # 5. Create new User object
    new_user = User(
        username=username,
        email=email,
        passwordHash=hashed_password
    )

    # 6. Save to Database
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "User registered successfully!", "userID": new_user.userID}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500