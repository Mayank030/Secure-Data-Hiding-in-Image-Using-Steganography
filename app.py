from flask import Flask, render_template, request, send_file, redirect, url_for
import cv2
import numpy as np
import os

app = Flask(__name__)

UPLOAD_FOLDER = "uploads/"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# ASCII dictionary for encoding/decoding
d = {chr(i): i for i in range(255)}
c = {i: chr(i) for i in range(255)}

# Home Page
@app.route("/")
def home():
    return render_template("home.html")

# Encrypt Page
@app.route("/encrypt", methods=["GET", "POST"])
def encrypt():
    if request.method == "POST":
        # Ensure the upload directory exists
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)

        # Get the uploaded image
        image_file = request.files["image"]
        message = request.form["message"]
        password = request.form["password"]

        if image_file.filename == "":
            return "No file selected", 400

        image_path = os.path.join(UPLOAD_FOLDER, "original.png")
        image_file.save(image_path)

        # Load image
        img = cv2.imread(image_path)
        if img is None:
            return "Invalid image", 400

        # Encode message length
        msg_length = f"{len(message):04d}"
        msg = msg_length + message  

        n, m, z = 0, 0, 0
        for char in msg:
            img[n, m, z] = d[char]
            z = (z + 1) % 3
            if z == 0:
                m += 1
                if m >= img.shape[1]:
                    m = 0
                    n += 1
                if n >= img.shape[0]:  
                    return "Message too long for image", 400

        # Save encrypted image
        encrypted_path = os.path.join(UPLOAD_FOLDER, "encrypted.png")
        cv2.imwrite(encrypted_path, img)

        return send_file(encrypted_path, as_attachment=True)

    return render_template("encrypt.html")

# Decrypt Page
@app.route("/decrypt", methods=["GET", "POST"])
def decrypt():
    if request.method == "POST":
        # Ensure the upload directory exists
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)

        image_file = request.files["image"]
        entered_passcode = request.form["password"]

        if image_file.filename == "":
            return "No file selected", 400

        image_path = os.path.join(UPLOAD_FOLDER, "uploaded_encrypted.png")
        image_file.save(image_path)

        img = cv2.imread(image_path)
        if img is None:
            return "Invalid image", 400

        # Extract message length
        message_length = ""
        n, m, z = 0, 0, 0
        for _ in range(4):
            message_length += c[img[n, m, z]]
            z = (z + 1) % 3
            if z == 0:
                m += 1
                if m >= img.shape[1]:
                    m = 0
                    n += 1
        message_length = int(message_length)

        # Extract actual message
        message = ""
        for _ in range(message_length):
            message += c[img[n, m, z]]
            z = (z + 1) % 3
            if z == 0:
                m += 1
                if m >= img.shape[1]:
                    m = 0
                    n += 1

        return render_template("decrypt.html", decrypted_message=message)

    return render_template("decrypt.html", decrypted_message=None)

if __name__ == "__main__":
    app.run(debug=True)
