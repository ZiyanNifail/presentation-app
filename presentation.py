import os
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from database import db
from models import Presentation

presentation_bp = Blueprint('presentation', __name__)

# Configure where to save videos
# This points to the 'uploads' folder we just created
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@presentation_bp.route('/upload', methods=['POST'])
def upload_presentation():
    print("DEBUG CHECK:", request.files)
    
    if 'video' not in request.files:
        return jsonify({"error": "No video file part"}), 400
    
    file = request.files['video']
    user_id = request.form.get('userID') # We get the student ID from the form text

    # 2. Basic Validation
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if not user_id:
        return jsonify({"error": "UserID is required"}), 400

    # 3. Save the File
    if file and allowed_file(file.filename):
        # secure_filename removes dangerous characters (e.g., "../hack.exe" becomes "hack.exe")
        filename = secure_filename(file.filename)
        
        # Create a unique name to prevent overwriting (e.g., "1_myvideo.mp4")
        unique_filename = f"{user_id}_{filename}"
        
        # Save to the computer's hard drive
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(file_path)

        # 4. Save Record to Database
        new_presentation = Presentation(
            userID=user_id,
            videoFile=file_path
        )

        try:
            db.session.add(new_presentation)
            db.session.commit()
            return jsonify({
                "message": "Video uploaded successfully", 
                "presentationID": new_presentation.presentationID,
                "path": file_path
            }), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    return jsonify({"error": "Invalid file type. Only mp4, avi, mov allowed."}), 400