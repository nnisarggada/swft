# SWFT - Simple Web-based File Transfer

SWFT is a lightweight and user-friendly web-based file sharing service that allows you to quickly and securely share files with others. With SWFT, you can easily upload files, get shareable links, and even customize links for easy sharing.

## Table of Contents

- [Features](#features)
- [Getting Started](#getting-started)
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

### Installation

To install SWFT using Docker, follow these steps:

1. **Clone the SWFT repository:**

   Clone the SWFT repository from GitHub to your local machine:

   ```bash
   git clone https://github.com/nnisarggada/swft.git
   cd swft
   ```

2. **Copy the sample `.env` file:**

   Copy the `.env.sample` file to create a `.env` file for configuration:

   ```bash
   cp .env.sample .env
   ```

3. **Run the app using Docker Compose:**

   Start SWFT with the following command:

   ```bash
   docker-compose up -d
   ```

### Configuration

Modify the `.env` file to suit your environment. At minimum, configure the following variables:

```bash
URL = "https://share.nnisarg.in" # URL of the hosted app
PORT = 8080 # Port of the hosted app
DB_HOST = "localhost" # Database host
DB_PORT = 5432 # Database port
DB_NAME = "swft" # Database name
DB_USER = "postgres" # Database user
DB_PASSWORD = "password" # Database password
ADMIN_USERNAME = "admin" # Username for the admin dashboard
ADMIN_PASSWORD = "swft" # Password for the admin dashboard
```

Additional settings can be configured as needed (e.g., email notifications, rate limits, analytics).

### Running the App

Once configured, run the app using Docker Compose as described above. The app will be accessible in your browser at `http://localhost:8080`.
The admin dashboard can be accessed at `http://localhost:8080/admin`. The default admin username is `admin` and password is `swft`.

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
curl -F "file=@/path/to/file" -F "link=my-secret-file" -F "time=3" -F "email=email@example.com" http://localhost:8080/
```

This will give a shareable URL to the file like `http://localhost:8080/my-secret-file`, which will be deleted after the specified time.

The `email` and `link` parameters are optional. The `time` parameter should be provided in hours and should not exceed 168 hours (1 week).

---

## TODO

- [x] ~~Add support for sending files via email.~~
- [x] ~~Implement rate limiting to prevent abuse.~~
- [x] ~~Add logging for email-related actions.~~
- [x] ~~Develop an admin dashboard for managing uploads.~~
- [ ] Add logging to admin dashboard.

## License

This project is licensed under the GNU General Public License v3 - see the [LICENSE](LICENSE.md) file for details.

## Contributing

We welcome contributions from the community! Please read our [Contribution Guidelines](CONTRIBUTING.md) for details on how to get started.

## Code of Conduct

We maintain a [Code of Conduct](CODE_OF_CONDUCT.md) to ensure a welcoming and inclusive environment for all contributors and users.
