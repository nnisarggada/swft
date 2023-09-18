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

```bash
# Clone the SWFT repository to your server
git clone https://github.com/nnisarggada/swft

# Navigate to the project directory
cd swft

#Make a directory for temporary storage
mkdir share_temp

# Create a Python virtual environment and activate it
python -m venv env
source env/bin/activate

# Install the required dependencies from the requirements.txt file
pip install -r requirements.txt
```

### Configuration

1. Edit the SWFT configuration in the `main.py` file to customize settings such as the port, URL, folder for storing files, and the time until files are deleted.

   ```python
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
   ```

### Running the App

1. Run the SWFT app with sudo (to give permissions):

   ```bash
   sudo python main.py
   ```

2. Access the SWFT web interface in your web browser:

   ```
   http://localhost:80
   ```

### Usage

1. Upload a File:
   - Click "Select a file" to choose a file from your local storage.
   - Optionally, provide a custom link name.
   - Click "Share" to upload the file and get a shareable link.

2. Share a File:
   - Use the provided shareable link to access the uploaded file.
   - Customize links for easier sharing.

3. Delete Files:
   - Uploaded files are automatically deleted after the specified time.

4. Command-Line Usage (curl/wget):
   - SWFT supports sharing files using command-line tools like curl or wget. For example,
     
     ```bash
     curl -X POST -F "file=@/path/to/file" -F "link=my-secret-file" -F "time=1800" http://localhost:80/upload
     ```
     This will give a sharable URL to the `file` like `http://localhost:80/my-secret-file` that will get deleted after `1800` seconds

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
