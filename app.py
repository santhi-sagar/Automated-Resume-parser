from flask import Flask, render_template, request
from parser import parse_resume
import os

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["resume"]
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    data = parse_resume(filepath)
    return f"<h3>Extracted Data:</h3><p>{data}</p>"

if __name__ == "__main__":
    app.run(debug=True)
