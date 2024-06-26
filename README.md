# SWFT - Simple Web-based File Transfer

SWFT is a lightweight and user-friendly web-based file sharing service that allows you to quickly and securely share files with others. With SWFT, you can easily upload files, get shareable links, and even customize links for easy sharing.

## Features

- Upload files and get shareable links.
- Customize links with user-defined names.
- Automatically delete files after a specified time period.
- Supports sharing files with users who prefer command-line tools like curl or wget.

## Getting Started

Follow these steps to set up and run SWFT on your server.

### Prerequisites

- Python 3.x
- Flask (Python web framework)
- pip (Python package manager)

### Installation

Clone the SWFT repository to your server:

```bash
git clone https://github.com/nnisarggada/swft
cd swft
```

Create a Python virtual environment and activate it:

```bash
python -m venv env
source env/bin/activate
```

Install the required dependencies from the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

### Configuration

Edit the SWFT configuration in the `main.py` file to customize settings such as the port, URL, folder for storing files, and the time until files are deleted. Modify the following variables as needed:

```python
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
```

### Running the App

Run the SWFT app by specifying the port number:

```bash
gunicorn -b 0.0.0.0:5000 main:app
```

Here, `5000` is the port on which the app will run. You can access the SWFT web interface in your web browser at http://localhost:5000.

## Usage

You can use SWFT to perform the following actions:

### Upload a File

1. Click "Select a file" to choose a file from your local storage.
2. Optionally, provide a custom link name.
3. Click "Share" to upload the file and get a shareable link.

### Share a File

Use the provided shareable link to access the uploaded file. Customize links for easier sharing.

### Delete Files

Uploaded files are automatically deleted after the specified time.

### Command-Line Usage (curl/wget)

SWFT supports sharing files using command-line tools like curl or wget. For example:

```bash
curl -F "file=@/path/to/file" -F "link=my-secret-file" -F "time=1800" http://localhost:5000/
```

This will give a sharable URL to the file like http://localhost:5000/my-secret-file that will get deleted after 1800 seconds.

## License

This project is licensed under the GNU General Public License v3 - see the [LICENSE](LICENSE.md) file for details.

## Contributing

We welcome contributions from the community! Please read our [Contribution Guidelines](CONTRIBUTING.md) for details on how to get started.

## Code of Conduct

We maintain a [Code of Conduct](CODE_OF_CONDUCT.md) to ensure a welcoming and inclusive environment for all contributors and users.
