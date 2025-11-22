# Project Readme

## Overview

This project provides a complete system for scraping PNCT container data using natural language queries. The system includes a Python API backend, a Gemini powered AI agent, an MCP tool server, and a Temporal based scraping service that runs workflows and activities to fetch real time container data from the PNCT website.

Users can ask questions like:

* Get info for MSDU123456  
* Is MSDU123456 available for pickup  
* Any holds on MSDU123456  
* Get last free day for MSDU123456  

The agent extracts the container ID, determines the intent, and triggers the PNCT scraper workflow.

## System Architecture Flow

User Query → Python API → Gemini Agent → MCP Tool → PNCT Scraper API → Temporal Workflow → PNCT.net Scraping Activities → Response Sent to User

## Architecture Details

### Python API Backend

The backend exposes a REST endpoint that accepts a natural language query. It initializes the Gemini agent, which processes the request and invokes MCP tools. The final structured result is prepared and sent back to the client.

### AI Agent

The agent uses the Google Gemini SDK. It parses user queries, extracts container numbers, interprets the intent, and calls MCP tools using structured parameters.

### MCP Tool Server

The MCP layer exposes functions that can be called by the agent. These functions contact the PNCT scraper API and trigger the workflow responsible for scraping container data.

### PNCT Scraper API with Temporal

The scraper API exposes an endpoint that initiates Temporal workflows. Each workflow handles scraping a container. Temporal manages orchestration, retries, and ensures reliability during PNCT scraping operations.

### Scraping Activities

Activities perform the actual scraping steps. This includes navigating to PNCT, searching for containers, parsing extracted details, and returning structured data. Playwright is used for automation and BeautifulSoup is used for parsing when needed.

## How to Start the Project

### Create Virtual Environment and Install Dependencies

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 1: Build Docker Services

Run Docker Compose from the project root to start PostgreSQL, Temporal, and other required services.

### Step 2: Start the Main Application

Run the main backend service:

```bash
python main.py
```

### Step 3: Start the Temporal Worker

Navigate to the worker directory and start the worker:

```bash
cd app/layers/scraper/temporal/
python worker.py
```

### Step 4: Configure Environment Variables

Configure your keys inside the Settings file.

Then export your Gemini API key:

```bash
export GOOGLE_API_KEY="your_key_here"
```

### Step 5: Open API Documentation

After all services are running, open the docs in your browser:

http://localhost:8000/api/v1/docs

## Project Structure Overview

* **main.py**  
  Runs the FastAPI server and initializes the agent.

* **MCP Module**  
  Provides tool functions that communicate with the scraper API.

* **PNCT Scraper API**  
  Calls Temporal workflows and returns scraped data.

* **Workflows and Activities**  
  Define the scraping logic and interaction with PNCT.net.
