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

def purge_upload_folder():
    while True:
        time.sleep(120)  # Wait for 2 minutes
        print("Auto-purging the uploads folder...")
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                print(f'Successfully deleted {file_path}')
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')
        print("Uploads folder purged successfully.")

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
        response = jsonify({'download_url': url_for('download_file', filename='decoded.zip')})
        
        # Schedule cleanup after response
        @after_this_request
        def cleanup_files(response):
            executor.submit(purge_upload_folder_once)
            return response
        
        return response

    return render_template('decode.html')

@app.route('/download/<filename>')
def download_file(filename):
    @after_this_request
    def cleanup(response):
        # Delay cleanup to ensure download is complete
        executor.submit(cleanup_file, os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return response
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
        if path and os.path.exists(path):
            try:
                os.remove(path)
            except Exception as e:
                app.logger.error(f"Error removing file {path}", exc_info=True)

def cleanup_file(path):
    # Delay to ensure the file is downloaded
    import time; time.sleep(30)
    if os.path.exists(path):
        try:
            os.remove(path)
        except Exception as e:
            app.logger.error(f"Error removing file {path}", exc_info=True)

def purge_upload_folder_once():
    time.sleep(30)  # Delay to ensure download is complete
    print("Purging the uploads folder once after download...")
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
            app.logger.info(f'Successfully deleted {file_path}')
        except Exception as e:
            app.logger.error(f'Failed to delete {file_path}. Reason: {e}')
    print("Uploads folder purged successfully after download.")

if __name__ == '__main__':
    # Start the background thread for purging the uploads folder
    purge_thread = threading.Thread(target=purge_upload_folder, daemon=True)
    purge_thread.start()

    app.run(debug=True, host='0.0.0.0', port=5000)
