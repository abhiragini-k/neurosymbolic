# Neurosymbolic Drug Repurposing Backend

The **Neurosymbolic Drug Repurposing Backend** is a high-performance, hybrid AI system designed to predict and explain potential drug-disease associations. It uniquely combines the predictive power of **Deep Learning (Relational Graph Convolutional Networks - R-GCN)** with the interpretability of **Symbolic Reasoning (LLM-driven Logic)** to provide transparent and actionable insights for biomedical researchers.

## 🚀 Key Capabilities

1.  **Neural Prediction (R-GCN)**:
    -   Utilizes a trained R-GCN model to predict the probability of links between compounds and diseases within a massive Knowledge Graph (KG).
    -   Provides fast, matrix-based inference for thousands of potential drug candidates.

2.  **Symbolic Explanation (Polo Agent)**:
    -   Deployment of an agentic Large Language Model (LLM) framework ("Polo") to traverse the KG.
    -   Extracts **reasoning chains** (e.g., *Drug A inhibits Gene B, which is associated with Disease C*).
    -   Synthesizes these paths into human-readable logical rules.

3.  **Explainability & Visualization**:
    -   **GNNExplainer Integration**: Generates heatmaps showing which biological pathways and genes contributed most to a specific prediction.
    -   **Confidence Scoring**: Calculates a transparent confidence score broken down by Embedding Similarity, Pathway Influence, Gene Matching, and Symbolic Rule verification.

---

## 🛠️ Architecture Pipeline

The backend functions as a unified API service coordinating three main layers:

1.  **Layer 1: Neural Inference Engine**
    -   Loads a pre-computed prediction matrix (`compound_disease_predictions.npy`) into memory at startup.
    -   Performs instant O(1) lookups for drug-disease scores.

2.  **Layer 2: Symbolic Logic Layer**
    -   On request, the **Polo Agent** (`polo_sci4.py`) performs a targeted search in the Neo4j/KV-store database.
    -   Retrieves multi-hop paths connecting the drug and disease.

3.  **Layer 3: Explainability Service**
    -   Computes feature importance using GNN gradients.
    -   Aggregates scores to identify top influential biological pathways.

---

## 📦 Prerequisites

Ensure your environment meets the following requirements:

-   **Operating System**: Windows / Linux / macOS
-   **Python**: Version 3.9 or higher
-   **Database**:
    -   **MongoDB**: For storing job status, caches, and user data.
    -   *(Optional for Inference)*: Connection to the Knowledge Graph data source (if running full rule mining).
-   **Files**:
    -   `compound_disease_predictions.npy` (R-GCN Output Matrix)
    -   `compound_id_to_name.json` (ID Mapping)
    -   `disease_id_to_name.json` (ID Mapping)

---

## ⚙️ Installation & Setup

1.  **Clone the Repository**
    ```bash
    git clone <repository-url>
    cd neurosymbolic/backend
    ```

2.  **Create a Virtual Environment**
    It is recommended to use a clean environment to avoid dependency conflicts.
    ```bash
    python -m venv venv
    ```
    *Activate:*
    -   **Windows:** `.\venv\Scripts\activate`
    -   **Mac/Linux:** `source venv/bin/activate`

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Environment Configuration**
    Create a `.env` file in the `backend` directory with your secrets:
    ```env
    # MongoDB Connection
    MONGODB_URL="mongodb://localhost:27017"
    DATABASE_NAME="drug_repurposing_db"

    # API Security (Optional for local dev)
    SECRET_KEY="your-secret-key"
    ```

---

## 🏃‍♂️ Running the Server

This backend leverages **FastAPI** for high throughput.

### Production Mode (Recommended)
Run the V2 backend entry point directly:
```bash
python backend.py
```
> This starts the server on `http://0.0.0.0:8000`.

### Development Mode
If you need hot-reloading during development:
```bash
uvicorn backend:app --reload --host 0.0.0.0 --port 8000
```

---

## 🔌 API Documentation

Once the server is running, you can access the interactive Swagger UI at:
👉 **http://localhost:8000/docs**

### Core Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **POST** | `/predict/drug` | **Main Pipeline Entry**. Input a drug name to get top disease candidates. |
| **GET** | `/predict/drug/{id}` | Get top predictions for a specific Compound ID. |
| **GET** | `/api/analysis/{cid}/{did}` | Trigger full **Neurosymbolic Analysis** (Neural + Symbolic + Graph). |
| **GET** | `/api/explainability/pathway` | Retrieve specific pathway influence scores for heatmaps. |

---

## 🧩 Project Structure

-   **`backend.py`**: **Main Entry Point (V2)**. Contains the API routes and initializes the Polo Agent.
-   **`app/`**: Contains modularized service logic (Legacy/Shared).
-   **`explainability/`**: Modules for GNNExplainer and heatmap generation (`pathway_influence.py`, `gene_match.py`).
-   **`polo_sci4.py`**: The core Symbolic Agent logic.
-   **`requirements.txt`**: Python package dependencies.

---

## 🤝 Contribution

1.  Fork the repository.
2.  Create a feature branch (`git checkout -b feature/amazing-feature`).
3.  Commit your changes.
4.  Open a Pull Request.

---

**© 2025 Neurosymbolic Drug Repurposing Project**
