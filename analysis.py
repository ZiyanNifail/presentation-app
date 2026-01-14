import cv2
import os
import speech_recognition as sr
from moviepy.editor import VideoFileClip
from flask import Blueprint, jsonify
from database import db
from models import Presentation

analysis_bp = Blueprint('analysis', __name__)

def get_video_stats(video_path):
    """
    Step 1: Video Processing (OpenCV)
    Calculates duration and frame count.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return None, "Error: Could not open video file."

    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    
    duration = 0
    if fps > 0:
        duration = frame_count / fps

    cap.release()
    
    return {
        "fps": round(fps, 2),
        "frame_count": int(frame_count),
        "duration_seconds": round(duration, 2)
    }, None

def extract_and_transcribe(video_path):
    """
    Step 2: Audio Processing
    Extracts audio from video and transcribes it using Google Speech API.
    """
    # Define a temporary path for the audio file
    audio_path = "temp_audio.wav"
    
    try:
        # A. Extract Audio using MoviePy
        # Load the video clip
        video_clip = VideoFileClip(video_path)
        # Extract audio and save as .wav
        video_clip.audio.write_audiofile(audio_path, logger=None)
        video_clip.close() # Close to free up memory

        # B. Transcribe using SpeechRecognition
        recognizer = sr.Recognizer()
        
        with sr.AudioFile(audio_path) as source:
            # Read the entire audio file
            audio_data = recognizer.record(source)
            
            # --- CRITICAL: SET LANGUAGE TO MALAYSIAN ENGLISH ---
            # This fulfills your FYP Proposal requirement for Localization
            text = recognizer.recognize_google(audio_data, language="en-MY")
            # ---------------------------------------------------
            
            return text, None

    except sr.UnknownValueError:
        return "", "Google Speech Recognition could not understand audio (Audio might be silent)"
    except sr.RequestError as e:
        return "", f"Could not request results from Google Speech Recognition service; {e}"
    except Exception as e:
        return "", str(e)
    finally:
        # C. Cleanup: Delete the temp file so we don't clutter the server
        if os.path.exists(audio_path):
            os.remove(audio_path)

@analysis_bp.route('/analyze/<int:presentation_id>', methods=['POST'])
def analyze_presentation(presentation_id):
    # 1. Fetch Presentation
    presentation = Presentation.query.get(presentation_id)
    if not presentation:
        return jsonify({"error": "Presentation not found"}), 404

    if not os.path.exists(presentation.videoFile):
        return jsonify({"error": "Video file missing from server"}), 404

    # 2. Run Video Analysis (OpenCV)
    video_stats, v_error = get_video_stats(presentation.videoFile)
    if v_error:
        return jsonify({"error": v_error}), 500

    # 3. Run Audio Analysis (SpeechRecognition)
    transcript_text, a_error = extract_and_transcribe(presentation.videoFile)
    
    if a_error and not transcript_text:
        # If transcription failed completely, we log it but don't crash the whole analysis
        print(f"Audio Warning: {a_error}")
        transcript_text = "(Audio transcription failed or was silent)"

    # 4. Calculate Words Per Minute (WPM)
    # Formula: Word Count / (Duration in seconds / 60)
    word_count = len(transcript_text.split())
    duration_minutes = video_stats['duration_seconds'] / 60
    
    wpm = 0
    if duration_minutes > 0:
        wpm = int(word_count / duration_minutes)

    # 5. Generate Feedback
    # This combines technical stats into a readable report
    feedback_text = (
        f"--- VIDEO STATS ---\n"
        f"Duration: {video_stats['duration_seconds']}s\n"
        f"FPS: {video_stats['fps']}\n\n"
        f"--- AUDIO STATS ---\n"
        f"Transcript: \"{transcript_text[:50]}...\" (Full transcript saved)\n"
        f"Speaking Pace: {wpm} Words Per Minute (WPM)\n"
    )

    # 6. Save Everything to Database
    presentation.feedback = feedback_text
    presentation.score = 85 # Still dummy score, we will fix this next!
    presentation.transcript = transcript_text
    presentation.words_per_minute = wpm

    try:
        db.session.commit()
        return jsonify({
            "message": "Analysis successful",
            "video_stats": video_stats,
            "transcript_snippet": transcript_text[:100],
            "wpm": wpm
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500