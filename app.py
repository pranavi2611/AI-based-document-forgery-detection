from flask import Flask, render_template, request
import os

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():

    if "document" not in request.files:
        return "No document selected"

    file = request.files["document"]

    if file.filename == "":
        return "No document selected"

    # Save uploaded document
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(file_path)

    return f"Document uploaded successfully: {file.filename}"


if __name__ == "__main__":
    app.run(debug=True)