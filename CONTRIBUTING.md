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
  - [Testing Your Changes](#testing-your-changes)
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

To set up a development environment for SWFT using Docker, follow these steps:

### Prerequisites

- Docker
- Docker Compose

### Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/nnisarggada/swft
   cd swft
   ```

2. **Set Up the Environment:**

   Copy the sample `.env` file:

   ```bash
   cp .env.sample .env
   ```

   Edit the `.env` file to configure the development environment. Essential variables include:

   ```bash
   URL = "http://localhost:8080" # URL of the hosted app
   PORT = 8080 # Port of the app
   DB_HOST = "db" # Database host (as defined in docker-compose)
   DB_PORT = 5432 # Database port
   DB_NAME = "swft_dev" # Database name
   DB_USER = "postgres" # Database user
   DB_PASSWORD = "password" # Database password
   ```

   Ensure the database host (`db`) matches the service name in the `docker-compose.yml` file.

### Running the App

1. **Start the App:**

   Use Docker Compose to bring up the app and database containers:

   ```bash
   docker-compose up --build
   ```

   This starts the application on `http://localhost:8080` and sets up a PostgreSQL database.

2. **Access the Logs:**

   View logs using:

   ```bash
   docker-compose logs -f app
   ```

3. **Stop the App:**

   Shut down the containers with:

   ```bash
   docker-compose down
   ```

### Testing Your Changes

- Edit the application files in the local repository. Changes will be reflected in the running container if the `docker-compose.yml` file uses volume mounts to sync code between your local machine and the container.
- Run tests to verify the behavior of your changes.

### Running Commands in the App Container

To execute commands inside the app container, use:

```bash
docker exec -it swft-app sh
```

Replace `swft-app` with the actual container name for the app.

---

Thank you for your contributions! Together, we can make SWFT a more robust and user-friendly file sharing service.
