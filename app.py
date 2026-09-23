from flask import Flask, render_template, request
import os
from PIL import Image, ImageChops, ImageEnhance
import fitz

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def calculate_forgery_score(image):
    """
    Basic prototype using Error Level Analysis (ELA).
    This is NOT a trained AI model.
    """

    image = image.convert("RGB")

    # Save temporary JPEG
    temp_file = "temp_ela.jpg"
    image.save(temp_file, "JPEG", quality=90)

    # Open compressed image
    compressed = Image.open(temp_file)

    # Calculate difference
    difference = ImageChops.difference(image, compressed)

    # Increase difference visibility
    enhanced = ImageEnhance.Brightness(difference)
    enhanced = enhanced.enhance(10)

    # Calculate average difference
    pixels = list(enhanced.getdata())

    total = 0

    for pixel in pixels:
        total += sum(pixel) / 3

    average_difference = total / len(pixels)

    # Convert difference into a percentage
    score = min(average_difference * 2, 100)

    os.remove(temp_file)

    return round(score, 2)


def get_image_from_file(file_path):
    """
    Convert uploaded image/PDF into an image.
    """

    extension = os.path.splitext(file_path)[1].lower()

    # Image files
    if extension in [".jpg", ".jpeg", ".png", ".webp"]:
        return Image.open(file_path)

    # PDF files
    elif extension == ".pdf":

        pdf = fitz.open(file_path)

        if len(pdf) == 0:
            return None

        page = pdf[0]

        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))

        image = Image.frombytes(
            "RGB",
            [pix.width, pix.height],
            pix.samples
        )

        pdf.close()

        return image

    return None


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
    file_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        file.filename
    )

    file.save(file_path)

    # Convert document to image
    image = get_image_from_file(file_path)

    if image is None:
        return "Unsupported file type"

    # Calculate forgery score
    forgery_score = calculate_forgery_score(image)

    authenticity_score = round(100 - forgery_score, 2)

    # Decide result
    if forgery_score >= 50:
        result = "Potentially Forged"
    else:
        result = "Likely Authentic"

    return render_template(
        "index.html",
        result=result,
        forgery_score=forgery_score,
        authenticity_score=authenticity_score,
        filename=file.filename
    )


if __name__ == "__main__":
    app.run(debug=True)