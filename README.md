# SWFT - Simple Web-based File Transfer

SWFT is a lightweight and user-friendly web-based file sharing service that allows you to quickly and securely share files with others. With SWFT, you can easily upload files, get shareable links, and even customize links for easy sharing.

## Table of Contents

- [Features](#features)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#configuration)
  - [Running the App](#running-the-app)
- [Usage](#usage)
  - [Upload a File](#upload-a-file)
  - [Share a File](#share-a-file)
  - [Delete Files](#delete-files)
  - [Command-Line Usage (curl/wget)](#command-line-usage-curlwget)
- [TODO](#todo)
- [License](#license)
- [Contributing](#contributing)
- [Code of Conduct](#code-of-conduct)

## Features

- Upload files and get shareable links.
- Customize links with user-defined names.
- Automatically delete files after a specified time period.
- Supports sharing files with users who prefer command-line tools like curl or wget.

## Getting Started

Follow these steps to set up and run SWFT on your server using Docker.

### Prerequisites

- Docker (Make sure Docker is installed and running on your server.)

### Installation

To install SWFT via Docker, follow these steps:

1. **Download the Docker image:**

   Run the following command to download the Docker image:

   ```bash
   curl -O https://docker.nnisarg.in/swft.tar
   ```

2. **Load the Docker image:**

   Run the following command to load the Docker image:

   ```bash
   docker load < swft.tar
   ```

3. **Get the sample `.env` file:**

   Before running the app, you need to configure it. To download the `.env.sample` file, use this command:

   ```bash
   curl -o .env.sample https://raw.githubusercontent.com/nnisarggada/swft/refs/heads/main/.env.sample
   ```

   Then, modify the `.env` file according to your environment. This file contains essential configuration settings such as:

   - `URL`: The URL of the hosted app.
   - `TEMP_FOLDER`: Folder where the files will be stored temporarily.
   - `DEFAULT_DEL_TIME`: Time until files will be deleted in hours.
   - `MAX_CONTENT_LENGTH`: Maximum file size allowed (in MB).
   - Optional: Email (SMTP) and analytics (UMAMI) settings if those features are required.

4. **Create a `.env` file:**

   After modifying the `.env.sample` file, rename it to `.env` in the same directory where the Docker container will run.

### Running the App

After configuring the `.env` file, you can run the app using Docker:

1. **Run the Docker container:**

   Run the following command to start SWFT in a Docker container:

   ```bash
   docker run -d -p 5000:5000 --env-file .env --name swft swft
   ```

   This will start the SWFT app, and it will be accessible in your browser at `http://localhost:5000`.

---

## Usage

You can use SWFT to perform the following actions:

### Upload a File

1. Click "Select a file" to choose a file from your local storage.
2. Optionally, provide a custom link name.
3. Click "Share" to upload the file and get a shareable link.

### Share a File

Use the provided shareable link to access the uploaded file. You can also customize links for easier sharing.  
Additionally, there is an option to send the file to your email by providing your email address.

### Delete Files

Uploaded files are automatically deleted after the specified time, based on the configuration.

### Command-Line Usage (curl/wget)

SWFT supports sharing files using command-line tools like curl or wget. For example:

```bash
curl -F "file=@/path/to/file" -F "link=my-secret-file" -F "time=3" -F "email=email@example.com" http://localhost:5000/
```

This will give a shareable URL to the file like `http://localhost:5000/my-secret-file`, which will be deleted after the specified time.

The `email` and `link` parameters are optional. The `time` parameter should be provided in hours and should not exceed 168 hours (1 week).

---

## TODO

- [x] ~~Add support for sending files via email.~~
- [x] ~~Implement rate limiting to prevent abuse.~~
- [x] ~~Add logging for email-related actions.~~
- [ ] Develop an admin dashboard for managing uploads and monitoring usage.

## License

This project is licensed under the GNU General Public License v3 - see the [LICENSE](LICENSE.md) file for details.

## Contributing

We welcome contributions from the community! Please read our [Contribution Guidelines](CONTRIBUTING.md) for details on how to get started.

## Code of Conduct

We maintain a [Code of Conduct](CODE_OF_CONDUCT.md) to ensure a welcoming and inclusive environment for all contributors and users.
