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
