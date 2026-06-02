from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from parser import parse_resume
import os
import logging

# Initialize Flask app
app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Setup
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Configure Flask to serve static files
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def home():
    """Serve the index.html file"""
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            return f.read(), 200, {'Content-Type': 'text/html; charset=utf-8'}
    except Exception as e:
        logger.error(f"Error serving index.html: {str(e)}")
        return jsonify({"error": "Unable to load home page"}), 500


@app.route("/upload", methods=["POST"])
def upload():
    """Handle resume upload and parsing"""
    try:
        logger.info("Upload request received")
        
        # Check if file exists in request
        if "resume" not in request.files:
            logger.warning("No file part in request")
            return jsonify({"error": "No file provided"}), 400

        file = request.files["resume"]

        # Check if filename is empty
        if file.filename == "":
            logger.warning("Empty filename")
            return jsonify({"error": "No file selected"}), 400

        # Validate file type
        if not allowed_file(file.filename):
            logger.warning(f"Invalid file type: {file.filename}")
            return jsonify({"error": "Only PDF files are allowed"}), 400

        # Check file size
        file_content = file.read()
        if len(file_content) > MAX_FILE_SIZE:
            logger.warning(f"File too large: {len(file_content)} bytes")
            return jsonify({"error": "File size exceeds 10MB limit"}), 400

        # Reset file pointer
        file.seek(0)
        
        # Save file
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        logger.info(f"File saved to: {filepath}")

        # Parse resume
        logger.info(f"Starting to parse resume: {filepath}")
        data = parse_resume(filepath)
        logger.info(f"Resume parsed successfully: {data}")
        
        # Return success response with data
        return jsonify({
            "success": True,
            "data": data
        }), 200

    except FileNotFoundError as e:
        logger.error(f"File not found: {str(e)}")
        return jsonify({"error": "PDF file not found"}), 404
    except ValueError as e:
        logger.error(f"Value error: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error processing resume: {str(e)}", exc_info=True)
        return jsonify({"error": f"Failed to process resume: {str(e)}"}), 500


# Error handlers
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def server_error(e):
    logger.error(f"Server error: {str(e)}")
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    logger.info("Starting Flask app on http://0.0.0.0:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
