import cv2  # This is OpenCV
import os
from flask import Blueprint, jsonify
from database import db
from models import Presentation

analysis_bp = Blueprint('analysis', __name__)

def get_video_stats(video_path):
    """
    Opens a video file and calculates duration and frame count.
    """
    # Open the video file
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        return None, "Error: Could not open video file."

    # Get metadata using OpenCV constants
    fps = cap.get(cv2.CAP_PROP_FPS)      # Frames per second
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    
    # Calculate duration (Total Frames / Frames Per Second)
    duration = 0
    if fps > 0:
        duration = frame_count / fps

    cap.release() # Close the video file properly
    
    return {
        "fps": round(fps, 2),
        "frame_count": int(frame_count),
        "duration_seconds": round(duration, 2)
    }, None

@analysis_bp.route('/analyze/<int:presentation_id>', methods=['POST'])
def analyze_presentation(presentation_id):
    # 1. Find the presentation in the database
    presentation = Presentation.query.get(presentation_id)
    
    if not presentation:
        return jsonify({"error": "Presentation not found"}), 404

    # 2. Check if file exists on disk
    if not os.path.exists(presentation.videoFile):
        return jsonify({"error": "Video file missing from server"}), 404

    # 3. Run Computer Vision Analysis
    stats, error = get_video_stats(presentation.videoFile)
    
    if error:
        return jsonify({"error": error}), 500

    # 4. Update Database with Results
    # For now, we generate a "dummy" feedback string based on the stats
    feedback_text = (
        f"Analysis Complete.\n"
        f"Duration: {stats['duration_seconds']} seconds.\n"
        f"Total Frames: {stats['frame_count']}.\n"
        f"FPS: {stats['fps']}."
    )
    
    # Saving to the new columns
    presentation.feedback = feedback_text
    presentation.score = 85  # Dummy score for now
    
    try:
        db.session.commit()
        return jsonify({
            "message": "Analysis successful",
            "data": stats,
            "feedback": feedback_text
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500