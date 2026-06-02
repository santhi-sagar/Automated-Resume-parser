from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from parser import parse_resume
import os
import logging
import traceback

# Initialize Flask app with proper static configuration
app = Flask(__name__, static_folder='.', static_url_path='')
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Setup directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
logger.info("Flask app starting...")

# Configure Flask
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=["GET"])
def home():
    """Serve the index.html file"""
    try:
        logger.info("Serving index.html from home route")
        with open(os.path.join(os.getcwd(), 'index.html'), 'r', encoding='utf-8') as f:
            html_content = f.read()
        return html_content, 200, {'Content-Type': 'text/html; charset=utf-8'}
    except FileNotFoundError as e:
        logger.error(f"index.html not found: {str(e)}")
        return jsonify({"error": "index.html not found"}), 500
    except Exception as e:
        logger.error(f"Error serving index.html: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"error": "Internal server error"}), 500


@app.route("/upload", methods=["POST"])
def upload():
    """Handle resume upload and parsing"""
    try:
        logger.info("=" * 80)
        logger.info("UPLOAD REQUEST RECEIVED")
        logger.info("=" * 80)
        
        # Check if file exists in request
        if "resume" not in request.files:
            logger.warning("No 'resume' field in request.files")
            logger.info(f"Available fields: {list(request.files.keys())}")
            return jsonify({"error": "No file provided"}), 400

        file = request.files["resume"]
        logger.info(f"File received: {file.filename}")

        # Check if filename is empty
        if file.filename == "":
            logger.warning("Empty filename received")
            return jsonify({"error": "No file selected"}), 400

        # Validate file type
        if not allowed_file(file.filename):
            logger.warning(f"Invalid file type: {file.filename}")
            return jsonify({"error": "Only PDF files are allowed"}), 400

        # Check file size
        file_content = file.read()
        file_size = len(file_content)
        logger.info(f"File size: {file_size} bytes")
        
        if file_size > MAX_FILE_SIZE:
            logger.warning(f"File too large: {file_size} bytes (max: {MAX_FILE_SIZE})")
            return jsonify({"error": "File size exceeds 10MB limit"}), 400

        # Reset file pointer
        file.seek(0)
        
        # Save file
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        logger.info(f"Saving file to: {filepath}")
        file.save(filepath)
        logger.info(f"File saved successfully")

        # Parse resume
        logger.info(f"Starting to parse resume from: {filepath}")
        if not os.path.exists(filepath):
            logger.error(f"File does not exist after save: {filepath}")
            return jsonify({"error": "File not found after save"}), 500
            
        data = parse_resume(filepath)
        logger.info(f"Resume parsed successfully")
        logger.info(f"Parsed data: {data}")
        
        # Return success response with data
        response_data = {
            "success": True,
            "data": data
        }
        logger.info(f"Returning response: {response_data}")
        return jsonify(response_data), 200

    except FileNotFoundError as e:
        logger.error(f"FileNotFoundError: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"error": f"PDF file not found: {str(e)}"}), 404
    except ValueError as e:
        logger.error(f"ValueError: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"error": f"Value error: {str(e)}"}), 400
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"error": f"Failed to process resume: {str(e)}"}), 500
    finally:
        logger.info("=" * 80)


# Error handlers
@app.errorhandler(404)
def not_found(e):
    logger.warning(f"404 Error: {str(e)}")
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def server_error(e):
    logger.error(f"500 Error: {str(e)}\n{traceback.format_exc()}")
    return jsonify({"error": "Internal server error"}), 500


@app.before_request
def log_request():
    logger.debug(f"Request: {request.method} {request.path}")
    logger.debug(f"Content-Type: {request.content_type}")


@app.after_request
def log_response(response):
    logger.debug(f"Response: {response.status_code}")
    return response


if __name__ == "__main__":
    logger.info("Starting Flask app...")
    logger.info(f"Working directory: {os.getcwd()}")
    logger.info(f"index.html exists: {os.path.exists('index.html')}")
    logger.info("Running on http://0.0.0.0:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
