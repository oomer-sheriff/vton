# Module: Backend Architecture

**Goal**: scalable API service to manage requests, users, and long-running AI tasks.

## Technology Stack
*   **Framework**: **FastAPI** (Python).
*   **Async Processing**: **Celery** (Workers) + **Redis** (Broker).
*   **Database**: **PostgreSQL**.
*   **Storage**: Local FS (Dev) / S3 (Prod).

## API Design

### Endpoints

#### 1. Ingestion
*   `POST /api/v1/garments/upload`: Uploads a raw photo. Triggers `rembg` task immediately.
*   `GET /api/v1/garments`: List catalogue.

#### 2. Try-On
*   `POST /api/v1/try-on`:
    *   **Body**: `{ user_image: File, garment_id: UUID }`
    *   **Response**: `{ task_id: "123-abc" }` (Async accepted).
*   `GET /api/v1/tasks/{task_id}`:
    *   **Response**: `{ status: "PROCESSING" | "COMPLETED", result_url: "..." }`

## Workflows

### The "Try-On" Queue
Since VTON inference takes 5-15 seconds, we cannot block the request.

1.  **FastAPI** receives request -> Pushes task to **Redis**.
2.  **Celery Worker** (GPU enabled) picks up task.
3.  **Worker** loads IDM-VTON model (kept in VRAM if possible).
4.  **Worker** runs inference -> Saves image to S3.
5.  **Worker** updates Postgres/Redis with "COMPLETED".
