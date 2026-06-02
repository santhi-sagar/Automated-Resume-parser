from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from parser import parse_resume
import os
import logging

app = Flask(__name__)
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
    return render_template("index.html")


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

        if len(file.read()) > MAX_FILE_SIZE:
            return jsonify({"error": "File size exceeds 10MB limit"}), 400

        file.seek(0)  # Reset file pointer after size check
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        data = parse_resume(filepath)
        return jsonify({"success": True, "data": data}), 200

    except Exception as e:
        logger.error(f"Error processing resume: {str(e)}")
        return jsonify({"error": "Failed to process resume"}), 500


if __name__ == "__main__":
    app.run(debug=True)
