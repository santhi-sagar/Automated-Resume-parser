from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from parser import parse_resume
import os
import logging

app = Flask(__name__, static_folder='.', static_url_path='')
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def home():
    return send_from_directory('.', 'index.html')


@app.route("/upload", methods=["POST"])
def upload():
    try:
        if "resume" not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files["resume"]

        if file.filename == "":
            return jsonify({"error": "No file selected"}), 400

        if not allowed_file(file.filename):
            return jsonify({"error": "Only PDF files are allowed"}), 400

        # Check file size
        file_content = file.read()
        if len(file_content) > MAX_FILE_SIZE:
            return jsonify({"error": "File size exceeds 10MB limit"}), 400

        # Reset file pointer and save
        file.seek(0)
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        # Parse the resume
        logger.info(f"Parsing resume: {filepath}")
        data = parse_resume(filepath)
        
        logger.info(f"Successfully parsed resume: {data}")
        return jsonify({"success": True, "data": data}), 200

    except FileNotFoundError as e:
        logger.error(f"File not found: {str(e)}")
        return jsonify({"error": "File not found"}), 404
    except ValueError as e:
        logger.error(f"Value error: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error processing resume: {str(e)}")
        return jsonify({"error": f"Failed to process resume: {str(e)}"}), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
