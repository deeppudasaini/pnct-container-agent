# How To Setup

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

### Step 4: Configure Environment Variables

Update the `Settings` class inside the shared module with your required keys and values. Anyone cloning this project must set their own environment values through that class.

After adding your values, inject the secret for `GEMINI_API_KEY` using the command below.

```bash
export GOOGLE_API_KEY="your_key_here"
```

### Step 5: Open API Docs

After the services are running, open the API documentation in your browser.

[http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs)
