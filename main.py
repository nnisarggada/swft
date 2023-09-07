from flask import Flask, request, render_template, send_from_directory
from werkzeug.utils import secure_filename
import os
import time
import threading
import json

# -------------------------------------------------------------------
# The following variables need to be changed before running the app:
# -------------------------------------------------------------------

port = 80 # Port that the app will run on
url = "localhost" # Url of the hosted app
folder = "/home/nnisarggada/swft/share_temp" # Folder where the files will stored temporarily
del_time = 1800 # Time until files will be deleted in seconds

# -------------------------------------------------------------------

def save_files_managed_to_file():
    with open('files_managed.json', 'w') as json_file:
        json.dump(files_managed, json_file)

def load_files_managed_from_file():
    if os.path.exists('files_managed.json'):
        with open('files_managed.json', 'r') as json_file:
            return json.load(json_file)
    return {}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = folder
files_managed = load_files_managed_from_file()

def delete_old_files():
    while True:
        current_time = time.time()
        to_delete = []
        
        for link, filename in files_managed.items():
            file_creation_time = os.path.getctime(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            if current_time - file_creation_time >= del_time:
                to_delete.append(link)
        
        for link in to_delete:
            filename = files_managed.pop(link)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            os.remove(file_path)

        save_files_managed_to_file()
        
        time.sleep(10)

file_management_thread = threading.Thread(target=delete_old_files)
file_management_thread.daemon = True
file_management_thread.start()

@app.route('/', methods=['GET'])
def upload_page():
    return render_template('index.html', full_url=url)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file provided\n', 400

    uploaded_file = request.files['file']

    if uploaded_file.filename == '':
        return 'No selected file\n', 400

    ext = uploaded_file.filename.rsplit('.', 1)[1].lower()
    
    current_time = int(time.time())

    custom_link = request.form.get('link', None)

    if custom_link == "":
        custom_link = f"{current_time}"

    if custom_link in files_managed:
        return f"Link {custom_link} already exists\n", 400

    filename = secure_filename(f"{current_time}.{ext}")

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    try:
        uploaded_file.save(file_path)

        link = f'{url}/{custom_link}\n'
        clickable_link = f'\033]8;;{link}\033\\{link}\033]8;;\033\\'

        files_managed[custom_link] = filename

        user_agent = request.headers.get('User-Agent')
        if 'curl' in user_agent.lower() or 'wget' in user_agent.lower():
            return clickable_link
        else:
            return render_template('shared.html', url=url, link=custom_link)

    except Exception as e:
        return f"Error: {e}\n", 500

@app.route('/<link>', methods=['GET'])
def share_file(link):
    if link not in files_managed:
        return "Invalid link\n", 400
    return send_from_directory(app.config['UPLOAD_FOLDER'], files_managed[link], as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)
