from flask import Flask, request, render_template, send_from_directory, make_response
from werkzeug.utils import secure_filename
import os
import time
import threading
import json

# -------------------------------------------------------------------
# The following variables need to be changed before running the app:
# -------------------------------------------------------------------

PORT = 80 # Port that the app will run on
URL = "localhost" # Url of the hosted app
TEMP_FOLDER = "/home/nnisarggada/swft/share_temp" # Folder where the files will stored temporarily
DEFAULT_DEL_TIME = 1800 # Time until files will be deleted in seconds
ALLOWED_EXTENSIONS = {
    'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif',  # Images and Documents
    'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',  # Office Documents
    'zip', 'rar', 'tar', 'gz',  # Compressed Files
    'mp3', 'wav', 'ogg', 'flac',  # Audio Files
    'mp4', 'mov', 'avi', 'mkv',  # Video Files
    'csv', 'tsv',  # Data Files
    'html', 'htm', 'xml', 'json',  # Web Formats
    'css', 'js', 'py', 'java', 'cpp',  # Code Files
    'txt', 'log', 'ini', 'cfg',  # Config and Text Files
    'md', 'markdown', 'rst',  # Markup Languages
    'sql', 'db', 'sqlite', 'dbf',  # Database Files
}
MAX_CONTENT_LENGTH = 64 * 1024 * 1024  # 64MB
MAX_DEL_TIME = 24 * 60 * 60  # 24 hours in seconds

# -------------------------------------------------------------------


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = TEMP_FOLDER

# Dictionary to track files and their individual deletion times
files_managed = {}

def save_files_managed_to_file():
    with open('files_managed.json', 'w') as json_file:
        json.dump(files_managed, json_file)

def load_files_managed_from_file():
    if os.path.exists('files_managed.json'):
        with open('files_managed.json', 'r') as json_file:
            return json.load(json_file)
    return {}

def is_allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_unique_filename(filename):
    base, ext = os.path.splitext(filename)
    counter = 1
    while os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], filename)):
        filename = f"{base}_{counter}{ext}"
        counter += 1
    return filename

def delete_old_files():
    while True:
        current_time = time.time()
        to_delete = []

        for link, (filename, del_time) in files_managed.items():
            file_creation_time = os.path.getctime(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            if current_time - file_creation_time >= del_time:
                to_delete.append(link)

        for link in to_delete:
            filename, _ = files_managed.pop(link)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            os.remove(file_path)

        # Save the updated files_managed dictionary to a file
        save_files_managed_to_file()

        time.sleep(10)

file_management_thread = threading.Thread(target=delete_old_files)
file_management_thread.daemon = True
file_management_thread.start()

@app.route('/', methods=['GET'])
def upload_page():
    return render_template('index.html', full_url=URL)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file provided\n', 400

    uploaded_file = request.files['file']

    if uploaded_file.filename == '':
        return 'No selected file\n', 400

    if not is_allowed_file(uploaded_file.filename):
        return 'File type not allowed\n', 400

    del_time = int(request.form.get('time', DEFAULT_DEL_TIME))
    del_time = min(del_time, MAX_DEL_TIME)

    filename = secure_filename(generate_unique_filename(uploaded_file.filename))

    custom_link = request.form.get('link', filename)


    if custom_link == "":
        custom_link = f"{filename}"

    if custom_link in files_managed or custom_link == "upload" or custom_link == "qr":
        return f"Link {custom_link} already exists\n", 400


    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)


    try:
        uploaded_file.save(file_path)

        link = f'{URL}/{custom_link}\n'
        clickable_link = f'\033]8;;{link}\033\\{link}\033]8;;\033\\'

        # Store the file information along with its deletion time
        files_managed[str(custom_link).lower()] = (filename, del_time)

        user_agent = request.headers.get('User-Agent')
        if 'curl' in user_agent.lower() or 'wget' in user_agent.lower():
            return clickable_link
        else:
            return render_template('shared.html', url=URL, link=custom_link)

    except Exception as e:
        return f"Error: {e}\n", 500

@app.route('/<link>', methods=['GET'])
def share_file(link):
    if link not in files_managed:
        return "Invalid link\n", 400
    return send_from_directory(app.config['UPLOAD_FOLDER'], files_managed[link][0], as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT)
