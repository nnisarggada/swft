from datetime import datetime, timedelta
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import re
import smtplib
import threading
import time

from dotenv import load_dotenv
from flask import Flask, render_template, request, send_from_directory
from flask_httpauth import HTTPBasicAuth
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

# Load environment variables
_ = load_dotenv()

# ---------------------------------------------------------------------------------------------------
# The following variables are extracted from the .env file and should be set before starting the app
# ---------------------------------------------------------------------------------------------------

URL = os.getenv("URL", "https://share.nnisarg.in")  # Url of the hosted app
DB_HOST = os.getenv("DB_HOST", "localhost")  # Database host
DB_PORT = int(os.getenv("DB_PORT", 5432))  # Database port
DB_USER = os.getenv("DB_USER", "postgres")  # Database user
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")  # Database password
DB_NAME = os.getenv("DB_NAME", "swft")  # Database name
MAX_TEMP_FOLDER_SIZE = (
    float(os.getenv("MAX_TEMP_FOLDER_SIZE", 50)) * 1024 * 1024 * 1024
)  # Maximum size of the temporary folder in GB
DEFAULT_DEL_TIME = float(
    os.getenv("DEFAULT_DEL_TIME", 3)
)  # Time until files will be deleted in hours
MAX_CONTENT_LENGTH = (
    float(os.getenv("MAX_CONTENT_LENGTH", 100)) * 1024 * 1024
)  # Maximum file size allowed in MB
MAX_DEL_TIME = float(
    os.getenv("MAX_DEL_TIME", 168)
)  # Maximum time until files will be deleted in hours
SMTP_SERVER = os.getenv(
    "SMTP_SERVER", "smtp.gmail.com"
)  # SMTP server for sending emails
SMTP_PORT = os.getenv("SMTP_PORT", 587)  # SMTP port for sending emails
SMTP_USERNAME = os.getenv(
    "SMTP_USERNAME", "swft@nnisarg.in"
)  # SMTP username for sending emails
SMTP_FROM = os.getenv(
    "SMTP_FROM", "SWFT by Nnisarg Gada <swft@nnisarg.in>"
)  # SMTP from address for sending emails
SMTP_PASSWORD = os.getenv(
    "SMTP_PASSWORD", "yourpassword"
)  # SMTP password for sending emails
# Umami script source
UMAMI_SRC = os.getenv("UMAMI_SRC", "https://umami.ls/script.js")
UMAMI_ID = os.getenv("UMAMI_ID", "your_website_id")  # Umami website id
UPLOAD_RATE_LIMIT = os.getenv("UPLOAD_RATE_LIMIT", "5 per minute")  # Number of uploads
DOWNLOAD_RATE_LIMIT = os.getenv(
    "DOWNLOAD_RATE_LIMIT", "10 per minute"
)  # Number of downbloads
# Storage URI for Flask Limiter
STORAGE_URI = os.getenv("STORAGE_URI", "memory://")
# Password for Admin Dashboard
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "swft")

# -------------------------------------------------------------------------------------
# Image extensions that are supported by browsers to view directly without downloading
# -------------------------------------------------------------------------------------

IMG_EXTENSIONS = [
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".svg",
    ".bmp",
    ".ico",
    ".apng",
    ".avif",
    ".jpe",
    ".jfif",
    ".jif",
]

TEMP_FOLDER = os.path.join(os.path.dirname(__file__), "data")
DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Flask application setup
app = Flask(
    __name__, static_url_path="", static_folder="static", template_folder="templates"
)
app.logger.setLevel("ERROR")
app.config["SQLALCHEMY_DATABASE_URI"] = DB_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
auth = HTTPBasicAuth()
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["10 per second"],
    storage_uri="memory://",
)


# Database models
class File(db.Model):
    __tablename__ = "files"

    id = db.Column(db.Integer, primary_key=True)
    link = db.Column(db.String(255), unique=True, nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    size = db.Column(db.Float, nullable=False)
    upload_time = db.Column(db.DateTime, nullable=False)
    expiry_time = db.Column(db.DateTime, nullable=False)

    def __init__(self, link, filename, size, upload_time, expiry_time):
        self.link = link
        self.filename = filename
        self.size = size
        self.upload_time = upload_time
        self.expiry_time = expiry_time

    def to_dict(self):
        return {
            "id": self.id,
            "link": self.link,
            "filename": self.filename,
            "size": round(self.size, 2),
            "upload_time": self.upload_time.strftime('%d %b %Y - %I:%M %p'),
            "expiry_time": self.expiry_time.strftime('%d %b %Y - %I:%M %p')
        }

    def __repr__(self):
        return f"<File {self.id}>"


# Routing for static files
@app.route("/security.txt")
@app.route("/robots.txt")
@app.route("/sitemap.xml")
@app.route("/favicon.ico")
def static_from_root():
    if not app.static_folder:
        app.static_folder = os.path.abspath(os.path.join(app.root_path, "static"))
    return send_from_directory(app.static_folder, request.path[1:])


# Create the temporary folder if it does not exist
if not os.path.exists(TEMP_FOLDER):
    os.makedirs(TEMP_FOLDER)


# Helper functions
def sanitize_string(input_string: str):
    input_string = input_string.lower().replace(" ", "_").strip()
    return re.sub(r"[^a-zA-Z0-9 ]", "_", input_string)


def is_valid_email(email: str):
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def generate_unique_filename(filename: str):
    # Replace periods in the filename with underscores for security reasons CVE-2024–1086
    base, ext = os.path.splitext(filename)
    base = sanitize_string(base)
    counter = 1
    filename = f"{base}{ext}"
    while os.path.exists(os.path.join(TEMP_FOLDER, filename)):
        filename = f"{base}_{counter}{ext}"
        counter += 1
    return filename


def get_folder_size(path: str):
    total_size = 0
    for dirpath, _, filenames in os.walk(path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            total_size += os.path.getsize(file_path)
    return total_size


def calculate_file_size(file: FileStorage) -> int:
    size = 0
    for chunk in file.stream:
        size += len(chunk)
    # Reset the file pointer to the beginning
    file.seek(0)
    return size


def send_email(email_address: str, file_path: str, file_url: str, expiry: float):
    def email_task():
        if not is_valid_email(email_address):
            print(f"Invalid email address: {email_address}")
            return
        if not all([SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_FROM, SMTP_PASSWORD]):
            print(f"Missing required configuration: {SMTP_SERVER}, {SMTP_PORT}, {SMTP_USERNAME}, {SMTP_FROM}, {SMTP_PASSWORD}")
            return
        try:
            message = MIMEMultipart()
            message["From"] = SMTP_FROM
            message["To"] = email_address
            message["Subject"] = f"File shared with you via {URL}"
            body = (
                f"Hello, the file you provided is attached, and the URL is "
                f"{file_url}. It expires in {round(expiry, 2)} hours."
            )
            message.attach(MIMEText(body, "plain"))
            if os.path.exists(file_path):
                with open(file_path, "rb") as file:
                    attachment = MIMEBase("application", "octet-stream")
                    attachment.set_payload(file.read())
                encoders.encode_base64(attachment)
                attachment.add_header(
                    "Content-Disposition",
                    f"attachment; filename={os.path.basename(file_path)}",
                )
                message.attach(attachment)
            with smtplib.SMTP(SMTP_SERVER, int(SMTP_PORT)) as server:
                _ = server.starttls()
                _ = server.login(SMTP_USERNAME, SMTP_PASSWORD)
                _ = server.sendmail(SMTP_FROM, email_address, message.as_string())
                print(f"Email sent to {email_address}")
        except Exception as e:
            print(f"Error: {e}")

    threading.Thread(target=email_task).start()


def delete_expired_files():
    with app.app_context():  # Activate application context
        while True:
            expired_files = File.query.filter(File.expiry_time < datetime.now()).all()
            for file in expired_files:
                if os.path.exists(os.path.join(TEMP_FOLDER, file.filename)):
                    os.remove(os.path.join(TEMP_FOLDER, file.filename))
                db.session.delete(file)
                db.session.commit()
            time.sleep(60)  # Check every minute


@app.before_request
def log_request():
    remote_addr = request.headers.get("X-Forwarded-For", request.remote_addr)
    user_agent = (
        request.headers.get("User-Agent", "Unknown")
        .replace("\n", " ")
        .replace(" ", "-")
    )
    time = datetime.now()
    method = request.method
    path = request.path
    scheme = request.scheme

    if method == "GET":
        log_content = (
            f"{time} | {remote_addr} | {user_agent} | "
            f"{method} | {path} | {scheme}\n"
        )
        print(log_content, end="")


@app.route("/", methods=["GET"])
def index():
    return render_template(
        "index.html", full_url=URL, umami_src=UMAMI_SRC, umami_id=UMAMI_ID
    )

@app.route("/about", methods=["GET"])
def about():
    return render_template(
        "about.html", full_url=URL, umami_src=UMAMI_SRC, umami_id=UMAMI_ID
    )


@app.route("/", methods=["POST"])
@limiter.limit(UPLOAD_RATE_LIMIT)
def upload_file():
    if "file" not in request.files:
        return "No file provided\n", 400

    uploaded_file = request.files["file"]
    if not uploaded_file or not uploaded_file.filename or uploaded_file.filename == "":
        return "No selected file\n", 400

    filename = generate_unique_filename(uploaded_file.filename)
    filename = secure_filename(filename)
    file_path = os.path.join(TEMP_FOLDER, filename)

    folder_size_bytes = get_folder_size(TEMP_FOLDER)
    file_size_bytes = calculate_file_size(uploaded_file)

    if (folder_size_bytes + file_size_bytes) > MAX_TEMP_FOLDER_SIZE:
        return "Server Space Full :/\nTry again later", 400

    del_time = float(request.form.get("time", DEFAULT_DEL_TIME))
    del_time = min(del_time, MAX_DEL_TIME)
    if del_time < 0:
        return "Invalid time\n", 400

    email_address = request.form.get("email")

    custom_link = request.form.get("link", filename)

    if custom_link == "":
        custom_link = filename

    if custom_link != filename:
        custom_link = sanitize_string(custom_link)

    invalid_links = [
        "admin",
        "about",
        "robots.txt",
        "sitemap.xml",
        "shared",
        "security.txt",
        "favicon.ico",
    ]

    if custom_link in invalid_links:
        return "Invalid link\n", 400

    if File.query.filter_by(link=custom_link).first():
        return "Link already taken\n", 400

    try:
        uploaded_file.save(file_path)

        # convert del_time to datetime object
        expiry_time = datetime.now() + timedelta(hours=del_time)

        file_record = File(link=custom_link, filename=filename,size=file_size_bytes, upload_time=datetime.now(), expiry_time=expiry_time)
        db.session.add(file_record)
        db.session.commit()

        if email_address is not None and email_address != "":
            send_email(email_address, file_path, URL + "/" + custom_link, del_time)
        else:
            email_address = ""

        remote_addr = request.headers.get("X-Forwarded-For", request.remote_addr)
        user_agent = (
            request.headers.get("User-Agent", "Unknown")
            .replace("\n", " ")
            .replace(" ", "-")
        )
        time = datetime.now()
        log_content = (
            f"{time} {remote_addr} | {user_agent} | "
            f"{filename} {custom_link} {del_time} | {email_address}\n"
        )
        print(log_content, end="")

        if "html" in str(request.headers.get("Accept", "")):
            return render_template(
                "shared.html",
                link=custom_link,
                full_url=URL,
                umami_src=UMAMI_SRC,
                umami_id=UMAMI_ID,
            )
        else:
            return URL + "/" + custom_link

    except Exception as e:
        return f"Error: {e}\n", 500


@app.route("/<link>", methods=["GET"])
@limiter.limit(DOWNLOAD_RATE_LIMIT)
def share_file(link: str):
    file = File.query.filter_by(link=link).first()
    if not file:
        return "Invalid link\n", 400
    _, ext = os.path.splitext(file.filename)
    is_img = ext in IMG_EXTENSIONS
    return send_from_directory(TEMP_FOLDER, file.filename, as_attachment=not is_img)

# Admin dashboard
@auth.verify_password
def verify_password(username, password):
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        return True
    return False

@app.route("/admin", methods=["GET"])
@auth.login_required
def admin_dashboard():
    active_files = File.query.all()
    files_data = [file.to_dict() for file in active_files]
    data = {
        "total_files": len(active_files),
        "files": files_data
    }
    return render_template("admin.html", data=data, full_url=URL)

@app.route("/delete/<id>", methods=["DELETE"])
@auth.login_required
def delete_file(id):
    file = File.query.filter_by(id=id).first()
    if not file:
        return "File not found", 404
    try:
        os.remove(os.path.join(TEMP_FOLDER, file.filename))
        db.session.delete(file)
        db.session.commit()
        return "File deleted successfully", 200
    except Exception as e:
        print(f"Error Deleting File {id}: {e}")
        return f"Error: {e}", 500


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    threading.Thread(target=delete_expired_files, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
