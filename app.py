import easyocr
import base64
import os
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
reader = easyocr.Reader(['en'])

# File to store the count of calls
count_file = "call_count.txt"

def read_call_count():
    """Read the current call count from the file."""
    if os.path.exists(count_file):
        with open(count_file, "r") as f:
            return int(f.read().strip())
    return 0

def write_call_count(count):
    """Write the updated call count to the file."""
    with open(count_file, "w") as f:
        f.write(str(count))

@app.route('/', methods=['GET'])
def Home():
    return jsonify({"Ok": "Working Home"}), 200

@app.route('/captcha', methods=['GET'])
def load():
    return jsonify({"Ok": "Working Captcha"}), 200

@app.route('/captcha', methods=['POST'])
def process_captcha():
    print("New image request")
    
    # Read and update call count
    count = read_call_count()
    count += 1
    write_call_count(count)

    if 'Image' not in request.json:
        return jsonify({"error": "No image data provided"}), 400
    
    image_data = request.json['Image']
    try:
        image_data = image_data.replace("data:image/jpeg;base64,", "")
        img_data = base64.b64decode(image_data)
        filename = "temp.jpg"
        with open(filename, "wb") as f:
            f.write(img_data)

        print("Image saved successfully")
    except Exception as e:
        return jsonify({"error": "Failed to decode and save image", "details": str(e)}), 400

    try:
        results = reader.readtext(filename)
        extracted_text = " ".join([text for (_, text, _) in results]).upper()
    finally:
        if os.path.exists(filename):
            os.remove(filename)

    return jsonify({"Captcha": extracted_text.replace(" ", ""), "Call Count": count})

if __name__ == '__main__':
    app.run(debug=True)
