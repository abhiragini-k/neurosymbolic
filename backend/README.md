# Neurosymbolic Drug Repurposing Backend

This is the backend service for the Neurosymbolic Drug Repurposing platform. It provides API endpoints for entity resolution, drug repurposing analysis (using R-GCN and symbolic reasoning), and job management.

## Prerequisites

- Python 3.9+
- MongoDB (running locally or a cloud instance like MongoDB Atlas)
- Node.js (if you plan to run the frontend, though not strictly required for this backend)

## Installation

1.  **Navigate to the backend directory:**
    ```bash
    cd backend
    ```

2.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    ```

3.  **Activate the virtual environment:**
    -   **Windows:**
        ```bash
        .\venv\Scripts\activate
        ```
    -   **macOS/Linux:**
        ```bash
        source venv/bin/activate
        ```

4.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

1.  Create a `.env` file in the `backend` root (if it doesn't already exist).
2.  Add the following variables:

    ```env
    PROJECT_NAME="Neurosymbolic Drug Repurposing Backend"
    MONGODB_URL="mongodb+srv://<user>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority"
    DATABASE_NAME="drug_repurposing_db"
    SECRET_KEY="your-super-secret-key-change-this-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES=10080
    ```

    *Note: Ensure your `MONGODB_URL` is valid and accessible.*

## Running the Application

Start the development server using `uvicorn`:

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

## API Documentation

Interactive API documentation (Swagger UI) is automatically generated and available at:

-   **Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
-   **ReDoc:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## Key Features & Endpoints

### 1. Authentication
Secure access using OAuth2 with Password correctness.
-   `POST /auth/register`: Create a new user account.
-   `POST /auth/login`: Login to receive an access token.

### 2. Entity Resolution
Map text queries to Knowledge Graph entities.
-   `GET /entities/resolve`: Check if a drug or disease exists in the database.

### 3. Analysis Workflow
Submit long-running analysis jobs.
-   `POST /analysis/submit`: Submit an entity (e.g., "Metformin") for repurposing analysis.
-   `GET /analysis/{job_id}`: Check the status and get results of a job.
-   `WS /analysis/ws/{job_id}`: (Optional) WebSocket for real-time status updates.

## Testing

You can use the provided helper script to check the MongoDB connection:

```bash
python check_mongo_conn.py
```

## Project Structure

-   `app/`: Main application source code.
    -   `core/`: Configuration and database logic.
    -   `routers/`: API route definitions.
    -   `models/`: Pydantic data models.
    -   `services/`: Business logic (Analysis, Mapping, Model Inference).
-   `finalKG/`: Directory containing the Knowledge Graph data (`nodes.csv`, etc.).
