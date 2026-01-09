# Judge Evaluation API

An enterprise-grade, async REST API for managing multi-judge competition evaluations and generating consolidated feedback using an LLM.

The project explores how qualitative human feedback from multiple independent sources can be aggregated into a single, meaningful assessment while remaining resilient to partial system failures (e.g., AI model downtime).


## Motivation & Design Context

This project was built to explore a common real-world backend problem: collecting independent human evaluations and transforming them into structured, actionable feedback.

In many judging, review, or scoring systems, raw scores alone are insufficient. This API focuses on combining numerical scores with qualitative feedback and synthesizing them into a high-level summary using an LLM, while ensuring the system remains reliable even when external AI services fail.


### Use Case: "AI-Powered Contestant Feedback Aggregator"
The system enables a workflow where:
1.  **Judges** submit independent, isolated evaluations (Scores + Notes) for a contestant.
2.  **Contestants/Admins** query the system to get a holistic view: all raw data plus an **AI-generated summary** that synthesizes the judges' disparate feedback into a cohesive assessment.

## Design Assumptions & Scope
1.  **Authentication & Authorization**: These are intentionally excluded to keep the focus on domain logic and system design.
2.  **ID Management**: `contestant_id` and `judge_id` are treated as opaque identifiers supplied by an external system. We assume they are valid if provided.
3.  **LLM Reliability**: External AI services are inherently unreliable. The system assumes successful text generation is **optional** for the primary function (retrieving scores).
    - **Constraint**: If the LLM times out or fails, the API **MUST** return the raw evaluations rather than failing the entire request.
4.  **Data Volume**: The total text from all evaluations for a single contestant fits within the context window of standard LLMs (e.g., Llama2/Mistral).
5.  **Concurrency**: The system is designed for high concurrency using `asyncio` and `asyncpg` to handle multiple judges submitting simultaneously.



## Database Schema

We use **PostgreSQL** with `SQLAlchemy 2.0` (Async Mode).

**Table: `evaluations`**

| Column         | Type        | Indexing     | Purpose |
|---------------|-------------|--------------|---------|
| `id`          | `UUID` (PK) | Primary Key  | Unique record identifier (auto-generated). |
| `contestant_id` | `VARCHAR` | Indexed      | Enables fast lookup when fetching evaluations for a contestant (read-heavy path). |
| `judge_id`    | `VARCHAR`   | Indexed      | Supports querying or analyzing evaluations by judge. |
| `score`       | `INTEGER`   | —            | Numerical assessment in the range 0–100. |
| `notes`       | `TEXT`      | —            | Qualitative feedback used for summarization. |
| `created_at`  | `TIMESTAMP` | —            | Audit timestamp for record creation. |
| `updated_at`  | `TIMESTAMP` | —            | Audit timestamp for record update. |


### Project Structure: Clean Architecture
The codebase enforces strict separation of concerns to ensure maintainability and testability:
- **`app/api/` (Presentation)**: FastAPI routers handling HTTP semantics, status codes, and dependency injection.
- **`app/services/` (Business Logic)**: Contains `EvaluationService` which orchestrates data fetching and LLM calls. It holds the core logic (e.g., "Don't fail if LLM fails").
- **`app/repositories/` (Data Access)**: Abstracted DB interactions. The service layer never writes raw SQL.
- **`app/models/`**: SQLAlchemy ORM definitions mapping to DB tables.
- **`app/schemas/`**: Pydantic models for Request/Response validation.
- **`app/services/llm/`**: **Adapter Pattern** implementation for the LLM.

### Validation Logic
Data integrity is enforced at the API boundary using **Pydantic**:
- **Score Integrity**: `score` field is strictly constrained `ge=0, le=100`.
- **Content Requirements**: `notes`, `contestant_id`, and `judge_id` must be non-empty strings (`min_length=1`).
- **UUID Validation**: Path parameters are validated as proper UUIDs to prevent database-level type errors.

### External API Design (LLM Integration)
- **Adapter Pattern**: An abstract `LLMProvider` base class allows seamless switching between local models (Ollama) and cloud APIs (OpenAI/Gemini) via configuration changes, without touching business code.
- **Timeouts**: To prevent thread starvation, the `OllamaLLMProvider` implements a strict **10-second hard timeout** using `asyncio.wait_for`.
- **Asynchronous Execution**: The potentially blocking I/O of the LLM call is offloaded to a thread pool (`asyncio.to_thread`) to ensure the main event loop remains non-blocking.



## 3️⃣ Solution Approach

**Data Flow Walkthrough: `GET /evaluations?contestant_id=123`**

1.  **Request Ingestion**: The API Endpoint receives the request and validates `contestant_id`.
2.  **Data Retrieval**: `EvaluationService` calls `EvaluationRepository.get_by_contestant("123")` to retrieve all evaluation records.
3.  **Prompt Engineering**: The Service constructs a text prompt aggregating all judges' notes and scores.
4.  **LLM Execution**:
    - The `LLMProvider.summarize()` method is invoked.
    - The request is sent asynchronously to the Ollama instance.
    - **Outcome A (Success)**: Returns a concise summary string.
    - **Outcome B (Failure/Timeout)**: The Service catches the exception.
5.  **Response Construction**: An `EvaluationSummary` object is built containing the list of evaluations, the summary (or error message), and the **overall score** (average of all evaluations).
6.  **Client Response**: The final JSON is returned to the client.



## 4️⃣ Error Handling Strategy

The application employs a defensive programming strategy:

### 1. Database Connection Failures
- **Scenario**: Database goes offline or connection pool is exhausted.
- **Handling**: Caught by a global `SQLAlchemyError` handler in `app/exceptions/handlers.py`.
- **Response**: Returns `500 Internal Server Error` with a sanitized message `"Internal Database Error"`, preventing stack trace leakage.

### 2. Third-Party API (LLM) Downtime
- **Scenario**: Ollama is crashed, network is unreachable, or generation takes >10s.
- **Handling**:
    - Caught locally within `EvaluationService.get_evaluations_for_contestant`.
    - Logged via Python's `logging` module for debugging.
- **Response**: **Graceful Degradation**. The API returns `200 OK`.
    - `data`: Complete list of evaluations.
    - `overall_score`: Calculated average score (Int).
    - `summary`: `null`
    - `summary_error`: `"LLM generation timed out"` or `"LLM generation failed"`.

### 3. Resource Not Found
- **Scenario**: Updating/Deleting a non-existent evaluation.
- **Handling**: Raises `NotFoundError` (custom exception).
- **Response**: `404 Not Found`.



## 5️⃣ How to Run the Project

### Prerequisites
- Python 3.10+
- PostgreSQL (or sufficient rights to run tests with in-memory SQLite)
- [Ollama](https://ollama.ai/) (Running locally with a model pulled, e.g., `ollama run llama2`)

### Setup

1.  **Clone & Install**:
    ```bash
    git clone <repo_url>
    cd <repo_directory>
    python -m venv venv
    # Windows
    .\venv\Scripts\activate
    # Linux/Mac
    source venv/bin/activate
    
    pip install -r requirements.txt
    ```

2.  **Environment Variables**:
    Create a `.env` file in the root directory:
    ```ini
    # Database
    DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/evaluation_db
    
    # LLM Settings
    LLM_PROVIDER=ollama
    # Ensure this matches your local Ollama port (default 11434)
    LLM_BASE_URL=http://localhost:11434
    LLM_MODEL=llama2
    ```

3.  **Run Application**:
    ```bash
    uvicorn app.main:app --reload
    ```
    *Tables are automatically created on startup.*

### Example API Calls

**1. Submit an Evaluation**
```bash
curl -X POST "http://localhost:8000/api/v1/evaluations" \
     -H "Content-Type: application/json" \
     -d '{
           "contestant_id": "c1",
           "judge_id": "j1",
           "score": 95,
           "notes": "Excellent stage presence, but pacing was slightly off."
         }'
```

**2. Get Aggregated Summary**
```bash
curl "http://localhost:8000/api/v1/evaluations?contestant_id=c1"
```



## 🧪 Testing

The project maintains a high standard of code quality with a comprehensive `pytest` suite covering positive and negative scenarios.

### Running Tests
Execute the full test suite (Unit + Integration):
```bash
pytest
```

### Test Scope
- **Unit Tests (`tests/unit/`)**:
    - `test_service.py`: Verifies core business logic and correct mocking.
    - `test_service_failures.py`: **Negative Testing** for DB crashes and LLM timeouts.
- **Integration Tests (`tests/`)**:
    - `test_api.py`: End-to-end API verification.
    - `test_api_failures.py`: Verifies HTTP 500 responses for DB errors and HTTP 200 graceful degradation for LLM errors.
