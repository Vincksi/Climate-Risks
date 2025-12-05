# Multi-Model Financial Analysis Tool

A sophisticated web application that leverages multiple Ollama language models to perform financial and market analysis. This project consists of a FastAPI backend server and a Streamlit frontend interface, allowing users to upload financial data and get AI-powered insights.

## Features

- **Multi-Model Analysis**: Query multiple Ollama models simultaneously for diverse perspectives
- **Role-Based Analysis**: Choose from predefined analyst roles (Financial Expert, Risk Advisor, Marketing Strategist, etc.)
- **Interactive Web Interface**: User-friendly Streamlit dashboard for data upload and analysis
- **RESTful API**: Built with FastAPI for easy integration with other services
- **Real-time Health Monitoring**: Check server and model status at a glance

## Prerequisites

- Python 3.9+
- Ollama installed and running locally
- Required Python packages (see Installation)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <project-directory>
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```
   
   The main dependencies include:
   - fastapi
   - uvicorn
   - streamlit
   - pandas
   - python-ollama
   - pydantic

## Usage

### Starting the Backend Server

1. Ensure Ollama is running locally
2. Start the FastAPI server:
   ```bash
   uvicorn server:app --reload --host 0.0.0.0 --port 8000
   ```
   The API will be available at `http://127.0.0.1:8000`

### Starting the Frontend

1. In a new terminal, navigate to the project directory
2. Activate the virtual environment if not already active
3. Start the Streamlit app:
   ```bash
   streamlit run app.py
   ```
4. Open your browser to the provided local URL (typically `http://localhost:8501`)

## API Endpoints

- `GET /health`: Check server and Ollama connection status
- `GET /roles`: Get list of available analyst roles
- `POST /analyze`: Submit data for analysis (expects JSON payload)

## Project Structure

- `server.py`: FastAPI backend with analysis endpoints
- `app.py`: Streamlit frontend application
- `README.md`: This documentation file

## Example Usage

1. Upload a CSV file containing financial data
2. Select one or more Ollama models to use for analysis
3. Choose an analyst role or create a custom prompt
4. Enter your analysis question
5. View and compare results from different models

## Acknowledgements

- Built with FastAPI and Streamlit
- Powered by Ollama's language models
- Inspired by modern financial analysis tools