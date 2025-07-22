# CV Analysis System

A system for analyzing IT candidate CVs using knowledge graphs and AI-powered querying.

## Prerequisites

- Python 3.8+
- PostgreSQL (must be installed and running on your machine)

## Setup and Installation

### 1. Environment Configuration

Create a `.env` file in the project root directory by copying from `.env.dev`:

```bash
cp .env.dev .env
```

Edit the `.env` file and update the configuration values according to your setup.

### 2. Install Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

### 3. Database Setup

Make sure PostgreSQL is installed and running on your machine. Create the necessary database as specified in your `.env` file.

**Important Database Table Creation:**

1. First, uncomment the table creation line in `db.py`:
   ```python
   # Remove the comment from this line:
   Base.metadata.create_all(engine)
   ```

2. Run the db.py once to create the database tables:
   ```bash
   python3 db.py
   ```

3. **After tables are created successfully**, comment the line back in `db.py`:
   ```python
   # Base.metadata.create_all(engine)
   ```

This prevents the system from trying to recreate tables on every startup.

## Running the Application

The application consists of two main components that need to be run simultaneously:

### 1. Start the RAG API Server

Open a terminal and run:

```bash
python3 rag_api.py
```

### 2. Start the Streamlit Web Interface

Open a second terminal and run:

```bash
streamlit run streamlit_app.py
```

## Usage

1. The RAG API will be available at the endpoint specified in your configuration
2. The Streamlit web interface will open in your browser (usually at `http://localhost:8501`)
3. Start chat with my chatbot.

## Features

- CV parsing and analysis
- Knowledge graph construction
- AI-powered candidate querying
- Interactive web interface for easy interaction

## Notes

- Ensure both terminals remain open while using the application
- Check your `.env` configuration if you encounter connection issues
- Make sure PostgreSQL service is running before starting the application
