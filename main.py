from flask import Flask, request, render_template, send_from_directory, make_response
import os
import time
import threading
import json
from datetime import datetime

# -------------------------------------------------------------------
# The following variables need to be changed before running the app:
# -------------------------------------------------------------------

URL = "localhost" # Url of the hosted app
TEMP_FOLDER = os.path.join(os.getcwd(), "share_temp") # Folder where the files will stored temporarily
MAX_TEMP_FOLDER_SIZE = 50 * 1024 * 1024 * 1024 # Maximum size of the temporary folder in bytes (50GB)
DEFAULT_DEL_TIME = 30 * 60 # Time until files will be deleted in seconds (30 minutes)
MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # Maximum file size allowed in bytes (100MB)
MAX_DEL_TIME = 24 * 60 * 60  # Maximum time until files will be deleted in seconds (24 hours)
UPLOAD_LOG_FILE = os.path.join(os.getcwd(), "upload.log") # Log file for uploads
ACCESS_LOG_FILE = os.path.join(os.getcwd(), "access.log") # Log file for access (requests)
MAX_LOG_ENTRIES = 500 # Maximum number of log entries for each log file

# -------------------------------------------------------------------


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = TEMP_FOLDER

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def load_files_managed_from_file():
    if os.path.exists('files_managed.json'):
        with open('files_managed.json', 'r') as json_file:
            return json.load(json_file)
    return {}

files_managed = load_files_managed_from_file()

def save_files_managed_to_file():
    with open('files_managed.json', 'w') as json_file:
        json.dump(files_managed, json_file)

def generate_unique_filename(filename):
    filename = filename.replace(" ", "_")
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

def get_folder_size(path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            total_size += os.path.getsize(file_path)
    return total_size

def log_message(logfile, content):

    entries = []
    if os.path.exists(logfile):
        with open(logfile, 'r') as file:
            entries = file.readlines()

    entries.append(content)

    if len(entries) > MAX_LOG_ENTRIES:
        entries.pop(0)

    with open(logfile, 'w') as file:
        file.writelines(entries)

@app.route('/', methods=['GET'])
def upload_page():
    return render_template('index.html', full_url=URL)

@app.route('/', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file provided\n', 400

    uploaded_file = request.files['file']

    if uploaded_file.filename == '':
        return 'No selected file\n', 400

    folder_path = app.config['UPLOAD_FOLDER']
    folder_size_bytes = get_folder_size(folder_path)
    file_size_bytes = int(request.headers['Content-Length'])


    if (folder_size_bytes + file_size_bytes) >= MAX_TEMP_FOLDER_SIZE:
        return 'Server Space Full :/\nTry again later\n', 400

    del_time = int(request.form.get('time', DEFAULT_DEL_TIME))
    del_time = min(del_time, MAX_DEL_TIME)

    filename = generate_unique_filename(uploaded_file.filename)

    custom_link = request.form.get('link', filename)


    if custom_link == "":
        custom_link = filename

    custom_link = custom_link.lower()
    custom_link = custom_link.replace(" ", "_")

    if custom_link in files_managed or custom_link == "about":
        return f"Link {custom_link} already exists\n", 400


    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)


    try:
        uploaded_file.save(file_path)

        files_managed[custom_link] = (filename, del_time)

        client_ip = request.remote_addr
        timestamp = datetime.now().strftime("%Y/%m/%d-%H:%M:%S")
        log_content = f"{client_ip} {filename} {timestamp}\n"
        log_message(UPLOAD_LOG_FILE, log_content)

        user_agent = request.headers.get('User-Agent')
        if 'curl' in user_agent.lower() or 'wget' in user_agent.lower():
            return "https://" + URL + "/" + custom_link + "\n"
        else:
            return render_template('shared.html', url=URL, link=custom_link)

    except Exception as e:
        return f"Error: {e}\n", 500

@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html', full_url=URL)

@app.route('/<link>', methods=['GET'])
def share_file(link):

    link = link.lower()

    client_ip = request.remote_addr
    timestamp = datetime.now().strftime("%Y/%m/%d-%H:%M:%S")
    log_content = f"{client_ip} {link} {timestamp}\n"
    log_message(ACCESS_LOG_FILE, log_content)

    if link not in files_managed:
        return "Invalid link\n", 400
    return send_from_directory(app.config['UPLOAD_FOLDER'], files_managed[link][0], as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
