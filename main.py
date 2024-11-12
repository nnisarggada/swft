from flask import Flask, request, render_template, send_from_directory
import os
import time
import threading
import json
from datetime import datetime
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv


load_dotenv()

# ---------------------------------------------------------------------------------------------------
# The following variables are extracted from the .env file and should be set before starting the app
# ---------------------------------------------------------------------------------------------------

URL = os.getenv("URL", "https://share.nnisarg.in") # Url of the hosted app
TEMP_FOLDER = os.path.join(os.getcwd(), os.getenv("TEMP_FOLDER", "share_temp")) # Folder name where the files will stored temporarily
MAX_TEMP_FOLDER_SIZE = float(os.getenv("MAX_TEMP_FOLDER_SIZE", 50)) * 1024 * 1024 * 1024 # Maximum size of the temporary folder in GB
DEFAULT_DEL_TIME = float(os.getenv("DEFAULT_DEL_TIME", 3)) # Time until files will be deleted in hours
MAX_CONTENT_LENGTH = float(os.getenv("MAX_CONTENT_LENGTH", 100)) * 1024 * 1024 # Maximum file size allowed in MB
MAX_DEL_TIME = float(os.getenv("MAX_DEL_TIME", 168))  # Maximum time until files will be deleted in hours
UPLOAD_LOG_FILE = os.path.join(os.getcwd(), os.getenv("UPLOAD_LOG_FILE", "upload.log")) # Log file for uploads
ACCESS_LOG_FILE = os.path.join(os.getcwd(), os.getenv("ACCESS_LOG_FILE", "access.log")) # Log file for access
MAX_LOG_ENTRIES = int(os.getenv("MAX_LOG_ENTRIES", 500)) # Maximum number of log entries for each log file
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com") # SMTP server for sending emails
SMTP_PORT = os.getenv("SMTP_PORT", 587) # SMTP port for sending emails
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "swft@nnisarg.in") # SMTP username for sending emails
SMTP_FROM = os.getenv("SMTP_FROM", "SWFT by Nnisarg Gada <swft@nnisarg.in>") # SMTP from address for sending emails
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "yourpassword") # SMTP password for sending emails
UMAMI_SRC = os.getenv("UMAMI_SRC", "https://umami.ls/script.js") # Umami script source
UMAMI_ID = os.getenv("UMAMI_ID", "your_website_id") # Umami website id

# -------------------------------------------------------------------------------------
# Image extensions that are supported by browsers to view directly without downloading
# -------------------------------------------------------------------------------------

IMG_EXTENSIONS = [".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".bmp", ".ico", ".apng", ".avif", ".jpe", ".jfif", ".jif"]


app = Flask(__name__)

# Routing for static files
@app.route("/security.txt")
@app.route("/robots.txt")
@app.route("/sitemap.xml")
@app.route("/favicon.ico")
def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])


# Create the temporary folder if it does not exist
if not os.path.exists(TEMP_FOLDER):
    os.makedirs(TEMP_FOLDER)


# Returns the total files stored in the temporary folder in json format
def load_files_managed_from_file():
    if os.path.exists("files_managed.json"):
        if os.path.getsize("files_managed.json") == 0:
            # Write if the file is empty.
            with open("files_managed.json", "w") as json_file:
                json_file.write("{}")
        with open("files_managed.json", "r") as json_file:
            return json.load(json_file)
    return {}


files_managed = load_files_managed_from_file()

# Updates the list of files stored in the temporary folder
def save_files_managed_to_file():
    with open("files_managed.json", "w") as json_file:
        json.dump(files_managed, json_file)

def sanitize_string(input_string):
    # Replace any character that is not a letter, number, or space with an underscore
    sanitized = re.sub(r"[^a-zA-Z0-9 ]", "_", input_string)
    return sanitized

def is_valid_email(email):
    # Basic regex pattern for validating email
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None

# Returns a unique filename after removing whitespaces and implementing a counter if the filename already exists
def generate_unique_filename(filename):
    # Replace periods in the filename with underscores for security reasons CVE-2024–1086
    base, ext = os.path.splitext(filename)
    base = sanitize_string(base)
    counter = 1
    filename = f"{base}{ext}"
    while os.path.exists(os.path.join(TEMP_FOLDER, filename)):
        filename = f"{base}_{counter}{ext}"
        counter += 1
    return filename

# Deletes files that have expired
def delete_old_files():
    while True:
        current_time = time.time()
        to_delete = []
        remove_from_json = []

        # Identify files that need to be deleted
        for link, (filename, del_time) in files_managed.items():
            if not os.path.exists(os.path.join(TEMP_FOLDER, filename)):
                remove_from_json.append(link)
            else:
                file_creation_time = os.path.getctime(os.path.join(TEMP_FOLDER, filename))
                if current_time - file_creation_time >= del_time:
                    to_delete.append(link)

        # Remove expired files from json
        for link in remove_from_json:
            files_managed.pop(link)

        # Actual deletion of files
        for link in to_delete:
            filename, _ = files_managed.pop(link)
            file_path = os.path.join(TEMP_FOLDER, filename)
            os.remove(file_path)

        # Save the updated files_managed dictionary to a file
        save_files_managed_to_file()

        time.sleep(60) # Checks every 1 minute

# Keep the file management thread running in the background
file_management_thread = threading.Thread(target=delete_old_files)
file_management_thread.daemon = True
file_management_thread.start()

# Returns the total size of a folder in bytes
def get_folder_size(path):
    total_size = 0
    for dirpath, _, filenames in os.walk(path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            total_size += os.path.getsize(file_path)
    return total_size

# Logging for access and uploads
def log_message(logfile, content):
    def write_to_logfile():
        with open(logfile, "a") as file:
            file.write(content + "\n")

        if os.path.exists(logfile):
            with open(logfile, "r") as file:
                entries = file.readlines()

            if len(entries) > MAX_LOG_ENTRIES:
                with open(logfile, "w") as file:
                    file.writelines(entries[-MAX_LOG_ENTRIES:])

    # Log parallely to avoid blocking the main thread
    io_thread = threading.Thread(target=write_to_logfile)
    io_thread.start()

# Send email to the user
def send_email(email_address, file_path, file_url, expiry):
    def email_task():
        if not is_valid_email(email_address):
            print("Invalid email address\n")
        
        # Check for SMTP credentials
        if not all([SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_FROM, SMTP_PASSWORD]):
            log_message(UPLOAD_LOG_FILE, "SMTP credentials not provided")
            print("SMTP credentials not provided\n")
            print("Invalid SMTP credentials\n")

        # Create the email message
        message = MIMEMultipart()
        message["From"] = SMTP_FROM
        message["To"] = email_address
        message["Subject"] = f"File shared with you via {URL}"

        body = f"Hello {email_address} the file you provided has been attached to this email and the url where it was shared is: {file_url} and expires in {expiry}!"
        message.attach(MIMEText(body, "plain"))

        # Check if the file exists and attach it
        if os.path.exists(file_path):
            with open(file_path, "rb") as file:
                attachment = MIMEBase("application", "octet-stream")
                attachment.set_payload(file.read())
            encoders.encode_base64(attachment)
            attachment.add_header(
                "Content-Disposition",
                f"attachment; filename={os.path.basename(file_path)}"
            )
            message.attach(attachment)
        else:
            print("File not found, try without entering email")

        # Send the email
        try:
            with smtplib.SMTP(SMTP_SERVER, int(SMTP_PORT)) as server:
                server.starttls()  # Upgrade the connection to secure
                server.login(SMTP_USERNAME, SMTP_PASSWORD)  # Log in to the server
                server.sendmail(SMTP_FROM, email_address, message.as_string())
            print("Email sent successfully!")
        except Exception as e:
            print(f"Error: {e}\n")
    
    # Send the email in a separate thread to avoid blocking the main thread
    thread = threading.Thread(target=email_task)
    thread.start()

@app.before_request
def log_request():
    remote_addr = request.headers.get("X-Forwarded-For", request.remote_addr)
    user_agent = request.headers.get("User-Agent", "Unknown").replace("\n", " ").replace(" ", "-")
    date = datetime.now().strftime("%Y/%m/%d-%H:%M:%S")
    method = request.method
    path = request.path
    scheme = request.scheme

    if method == "GET":
        log_content = f"{remote_addr} {user_agent} {date} {method} {path} {scheme}\n"
        log_message(ACCESS_LOG_FILE, log_content)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", full_url=URL, umami_src=UMAMI_SRC, umami_id=UMAMI_ID)

@app.route("/", methods=["POST"])
def upload_file():
    
    if "file" not in request.files:
        return "No file provided\n", 400

    uploaded_file = request.files["file"]

    if uploaded_file.filename == "":
        return "No selected file\n", 400
    
    filename = generate_unique_filename(uploaded_file.filename).lower()
    file_path = os.path.join(TEMP_FOLDER, filename)

    folder_path = TEMP_FOLDER
    folder_size_bytes = get_folder_size(folder_path)
    file_size_bytes = int(request.headers["Content-Length"])

    email_address = request.form.get("email")

    if (folder_size_bytes + file_size_bytes) >= MAX_TEMP_FOLDER_SIZE:
        return "Server Space Full :/\nTry again later\n", 400

    del_time = float(request.form.get("time", DEFAULT_DEL_TIME))
    del_time = min(del_time, MAX_DEL_TIME) * 60 * 60
    if del_time < 0 :
        return "Invalid time\n", 400

    custom_link = request.form.get("link", filename)

    if custom_link == "":
        custom_link = filename
    else:
        custom_link = sanitize_string(custom_link.lower())

    invalid_links = ["about", "robots.txt", "sitemap.xml", "shared", "security.txt", "favicon.ico"]

    if custom_link in files_managed or custom_link in invalid_links:
        return f"The link you are looking for is already taken, Please try a different link\n", 400

    try:
        uploaded_file.save(file_path)
        if email_address is not None and email_address != "":
            send_email(email_address, file_path, URL+"/"+custom_link, del_time/3600)
        files_managed[custom_link] = (filename, del_time)
        save_files_managed_to_file()

        remote_addr = request.headers.get("X-Forwarded-For", request.remote_addr)
        user_agent = request.headers.get("User-Agent", "Unknown").replace("\n", " ").replace(" ", "-")
        date = datetime.now().strftime("%Y/%m/%d-%H:%M:%S")
        log_content = f"{remote_addr} {user_agent} {date} {filename} {custom_link} {del_time}\n"
        log_message(UPLOAD_LOG_FILE, log_content)
        if "html" in request.headers.get("Accept"):
            return render_template("shared.html", link=custom_link, full_url=URL, umami_src=UMAMI_SRC, umami_id=UMAMI_ID)
        else:
            return URL + "/" + custom_link

    except Exception as e:
        log_message(UPLOAD_LOG_FILE, f"Error: {e}")
        return f"Error: {e}\n", 500

@app.route("/about", methods=["GET"])
def about():
    return render_template("about.html", full_url=URL, umami_src=UMAMI_SRC, umami_id=UMAMI_ID)

@app.route("/<link>", methods=["GET"])
def share_file(link):

    link = link.lower()
    is_img = False

    if link not in files_managed:
        return "Invalid link\n", 400

    _, ext = os.path.splitext(files_managed[link][0])
    is_img = ext in IMG_EXTENSIONS

    return send_from_directory(TEMP_FOLDER, files_managed[link][0], as_attachment= not is_img)

if __name__ == "__main__":
    app.run(debug=True)
