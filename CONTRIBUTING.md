# Contributing to SWFT - Simple Web-based File Transfer

Thank you for considering contributing to SWFT! We appreciate your interest in making our web-based file sharing service even better. This document provides guidelines for contributing to the project. Please take a moment to read and follow these guidelines to ensure a smooth and collaborative development process.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
  - [Reporting Bugs](#reporting-bugs)
  - [Suggesting Enhancements](#suggesting-enhancements)
  - [Submitting Changes](#submitting-changes)
- [Development Setup](#development-setup)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#configuration)
  - [Running the App](#running-the-app)
- [Usage](#usage)
- [License](#license)

## Code of Conduct

Before contributing, please review our [Code of Conduct](CODE_OF_CONDUCT.md). We expect all contributors to adhere to this code to create a welcoming and inclusive community.

## How Can I Contribute?

### Reporting Bugs

If you encounter a bug while using SWFT or have identified a potential issue, please [open a new issue](https://github.com/nnisarggada/swft/issues/new) on our GitHub repository. Ensure that your report includes detailed information about the problem, such as the steps to reproduce it and any relevant error messages.

### Suggesting Enhancements

If you have ideas for new features or improvements to existing ones, feel free to [create an enhancement request](https://github.com/nnisarggada/swft/issues/new) on GitHub. Be clear and specific about the proposed enhancement and how it would benefit SWFT.

### Submitting Changes

If you'd like to contribute code to SWFT, follow these steps:

1. Fork the SWFT repository on GitHub.
2. Create a new branch from the `main` branch to work on your changes.
3. Make your changes and ensure that they follow the project's coding standards.
4. Test your changes thoroughly.
5. Create a pull request (PR) describing your changes, explaining their purpose, and providing steps for testing.
6. Be prepared to respond to feedback and make necessary adjustments.

## Development Setup

To set up a development environment for SWFT, follow these steps:

### Prerequisites

Ensure you have the following prerequisites installed:

- Python 3.x
- Flask (Python web framework)
- pip (Python package manager)

### Installation

Clone the SWFT repository to your server:

```bash
git clone https://github.com/nnisarggada/swft
cd swft
```

Make a directory for temporary storage:

```bash
mkdir share_temp
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
URL = "localhost"  # Url of the hosted app
TEMP_FOLDER = "/home/nnisarggada/GitRepos/swft/share_temp"  # Folder where the files will be stored temporarily
MAX_TEMP_FOLDER_SIZE = 50 * 1024 * 1024  # Maximum size of the temporary folder in bytes (50MB)
DEFAULT_DEL_TIME = 1800  # Time until files will be deleted in seconds (30 minutes)
MAX_CONTENT_LENGTH = 64 * 1024 * 1024  # Maximum file size allowed in bytes (64MB)
MAX_DEL_TIME = 24 * 60 * 60  # Maximum time until files will be deleted in seconds (24 hours)
```

### Running the App

Run the SWFT app with sudo (to give permissions):

```bash
sudo gunicorn -b 0.0.0.0:80 main:app
```

Here, `80` is the port on which the app will run. You can access the SWFT web interface in your web browser at http://localhost:80.

## Code of Conduct

We maintain a [Code of Conduct](CODE_OF_CONDUCT.md) to ensure a welcoming and inclusive environment for all contributors and users.
