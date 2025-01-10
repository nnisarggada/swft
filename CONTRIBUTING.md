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
  - [Running the App](#running-the-app)
  - [Running Commands in the App Container](#running-commands-in-the-app-container)

---

## Code of Conduct

Before contributing, please review our [Code of Conduct](CODE_OF_CONDUCT.md). We expect all contributors to adhere to this code to create a welcoming and inclusive community.

---

## How Can I Contribute?

### Reporting Bugs

If you encounter a bug while using SWFT or have identified a potential issue, please [open a new issue](https://github.com/nnisarggada/swft/issues/new) on our GitHub repository. Ensure that your report includes:

- A clear and descriptive title.
- Steps to reproduce the problem.
- Any relevant error messages or screenshots.

### Suggesting Enhancements

Have an idea for improving SWFT? [Create an enhancement request](https://github.com/nnisarggada/swft/issues/new) on GitHub. Include:

- A concise description of the enhancement.
- The problem it addresses or the value it adds.
- Any additional details or examples to support your suggestion.

### Submitting Changes

To contribute code to SWFT:

1. Fork the SWFT repository on GitHub.
2. Create a feature branch based on the `main` branch.
3. Implement your changes while adhering to coding standards.
4. Test your changes thoroughly.
5. Create a pull request (PR) describing your changes, including:
   - The purpose of the changes.
   - Any issues fixed or features added.
   - Instructions for testing.

Be prepared to discuss your PR and address any requested changes.

---

## Development Setup

To set up a development environment for SWFT using a virtual environment, follow these steps:

### Prerequisites

- Python 3.7 or higher
- `pip`
- `virtualenv` (optional, if you want to use it)

### Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/nnisarggada/swft
   cd swft
   ```

2. **Create and Activate the Virtual Environment:**

   Use Python's built-in `venv` module to create a virtual environment:

   ```bash
   python3 -m venv env
   ```

   Then, activate the virtual environment:

   - On **Linux/macOS**:

     ```bash
     source env/bin/activate
     ```

   - On **Windows**:

     ```bash
     .\env\Scripts\activate
     ```

3. **Install the Dependencies:**

   With the virtual environment activated, install the required dependencies from the `requirements.txt` file:

   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up the Environment:**

   Copy the sample `.env` file:

   ```bash
   cp .env.sample .env
   ```

   Edit the `.env` file to configure the development environment. Essential variables include:

   ```bash
   URL = "http://localhost:8080" # URL of the hosted app
   PORT = 8080 # Port of the app
   DB_HOST = "localhost" # Database host (you can use a local database like PostgreSQL)
   DB_PORT = 5432 # Database port
   DB_NAME = "swft_dev" # Database name
   DB_USER = "postgres" # Database user
   DB_PASSWORD = "password" # Database password
   ```

   Ensure that the database host (`localhost`) corresponds to the service where you are running your database.

### Running the App

1. **Run the Application:**

   Start the application by running the following command:

   ```bash
   python app.py
   ```

   This should start the application on `http://localhost:8080`.

2. **Access the Logs:**

   If the app has logging configured, you can view the logs from the console output when running the application.

3. **Stop the App:**

   To stop the app, simply press `Ctrl+C` in the terminal.


### Running Commands in the App Environment

If you need to run commands in the virtual environment, make sure it's activated (`source env/bin/activate` on macOS/Linux, `.env\Scripts\activate` on Windows), and execute any necessary commands from the terminal.

---

Thank you for your contributions! Together, we can make SWFT a more robust and user-friendly file sharing service.
