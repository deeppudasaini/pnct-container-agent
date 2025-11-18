# Project Readme

## Overview

This document explains how to set up and run the project using Docker, the main application, and the Temporal worker.

## How to Start

### Step 1: Build Docker Compose

Use Docker Compose to set up the required databases and Temporal server.
Run the compose file from the root folder.

### Step 2: Start the Main Application

Run the `main.py` file located in the root folder.

```bash
python main.py
```

### Step 3: Start the Temporal Worker

Go to the folder `app/layers/scraper/temporal/` and run the worker file.

```bash
python worker.py
```

### Step 4: Open API Docs

After the services are running, open the API documentation in your browser.

[http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs)
