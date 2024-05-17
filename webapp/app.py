from flask import Flask, request, render_template, jsonify, url_for, send_from_directory, after_this_request, Response, send_file
from werkzeug.utils import secure_filename
from stegAES import Activity
import os
import zipfile
import io
import tempfile
from flask_executor import Executor
from Crypto.Random import get_random_bytes
import threading
import time
import shutil
from PIL import Image

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100 MB
executor = Executor(app)

# Ensure the uploads directory exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/encode', methods=['GET', 'POST'])
def encode():
    if request.method == 'POST':
        image = request.files['image']
        message = request.form['message']
        zip_file = request.files.get('zip_file')
        key_file = request.files['key_file']

        image_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(image.filename))
        zip_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(zip_file.filename)) if zip_file else None
        key_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(key_file.filename))

        image.save(image_path)
        if zip_file:
            zip_file.save(zip_path)
        key_file.save(key_path)

        # Check if the image is a JPEG and convert it to PNG for encoding
        if image_path.lower().endswith(('.jpg', '.jpeg')):
            with Image.open(image_path) as img:
                png_image_path = image_path.rsplit('.', 1)[0] + '.png'
                img.save(png_image_path, 'PNG')
            image_path = png_image_path

        activity = Activity(image_path, message, zip_path, key_path, 'encode', save=False)
        encoded_image_path = activity.execute()

        @after_this_request
        def cleanup_files(response):
            executor.submit(cleanup_files, [image_path, zip_path, key_path, encoded_image_path])
            return response

        return jsonify({'download_url': url_for('download_file', filename=os.path.basename(encoded_image_path))})

    return render_template('encode.html')

@app.route('/decode', methods=['GET', 'POST'])
def decode():
    if request.method == 'POST':
        image = request.files['image']
        key_file = request.files['key_file']

        image_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(image.filename))
        key_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(key_file.filename))

        image.save(image_path)
        key_file.save(key_path)

        # Check if the image is a JPEG and convert it to PNG for decoding
        if image_path.lower().endswith(('.jpg', '.jpeg')):
            with Image.open(image_path) as img:
                png_image_path = image_path.rsplit('.', 1)[0] + '.png'
                img.save(png_image_path, 'PNG')
            image_path = png_image_path

        activity = Activity(image_path, None, None, key_path, 'decode', save=False)
        decrypted_message, decrypted_zip = activity.execute()

        # Create a file named 'decoded.zip' in the UPLOAD_FOLDER
        temp_zip_path = os.path.join(app.config['UPLOAD_FOLDER'], 'decoded.zip')

        with zipfile.ZipFile(temp_zip_path, 'w') as zf:
            zf.writestr('decrypted_message.txt', decrypted_message)
            if decrypted_zip:
                with zipfile.ZipFile(io.BytesIO(decrypted_zip), 'r') as inner_zip:
                    for file_name in inner_zip.namelist():
                        zf.writestr(file_name, inner_zip.read(file_name))

        # Return the download URL
        return jsonify({'download_url': url_for('download_file', filename='decoded.zip')})

    return render_template('decode.html')

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True, download_name=filename)

@app.route('/generate_key', methods=['POST'])
def generate_key():
    key = get_random_bytes(32)  # Generate a 256-bit key
    hex_key = key.hex()  # Convert bytes to hexadecimal
    key_path = os.path.join(app.config['UPLOAD_FOLDER'], 'aes_key.txt')
    with open(key_path, 'w') as key_file:  # Write as text
        key_file.write(hex_key)
    return send_file(key_path, as_attachment=True, download_name='aes_key.txt')

def cleanup_files(paths):
    # Delay to ensure the file is downloaded
    import time; time.sleep(30)
    for path in paths:
        if path and os.path.exists(path) and 'aes_key.txt' not in path:
            try:
                os.remove(path)
            except Exception as e:
                app.logger.error(f"Error removing file {path}", exc_info=True)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

