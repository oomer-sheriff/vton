# Project Status & Architecture Overview
**Date**: 2026-01-05
**Status**: Phase 4 Complete (Frontend Foundation)

## High-Level Architecture
The VTON application is a **Microservices-style** hybrid system running on Windows (Host) and Docker (Linux Worker).

```mermaid
graph TD
    User[User (Browser)] <-->|Next.js| Frontend[Frontend (Next.js)]
    Frontend <-->|REST API| Backend[Backend (FastAPI - Port 8000)]
    Backend <-->|SQLAlchemy| DB[(PostgreSQL)]
    
    subgraph "Asynchronous Processing"
        Backend -->|Tasks| RabbitMQ[RabbitMQ Broker]
        RabbitMQ -->|Consume| Worker[GPU Worker (Docker/Linux)]
        Worker -->|Update Status| Redis[Redis (Result Backend)]
        Worker -->|Read/Write| DB
        Worker -->|Files| Media[Media Volume]
    end

    subgraph "AI Pipelines (Worker)"
        Worker -->|Rembg + u2net| Ingestion[Ingestion Pipeline]
        Worker -->|Gemini 1.5| Metadata[Metadata Extractor]
        Worker -->|SD 1.5 + IP-Adapter| VTON[VTON Pipeline]
    end
```

---

## Component Implementation Details

### 1. Frontend (`/frontend`)
*   **Tech**: Next.js 14 (App Router), TailwindCSS, Lucide Icons.
*   **Current State**: Fully functional UI for the MVP.
*   **Components**:
    *   **GarmentUploader**: Handles file upload to `/api/v1/ingestion/upload`.
    *   **GarmentSelector**: Fetches closet from `/api/v1/ingestion/garments` and displays a grid.
    *   **MagicMirror**: Interactive Try-On panel. Handles person upload, polling task status, and displaying the result.

### 2. Backend API (`/backend/app/api`)
*   **Tech**: FastAPI, Uvicorn.
*   **Current State**: Robust API serving frontend and managing workflow.
*   **Endpoints**:
    *   `POST /ingestion/upload`: Ingests raw garment, triggers `remove_background` and `extract_metadata`.
    *   `GET /ingestion/garments`: Database query for all valid garments.
    *   `POST /tryon/`: Triggers `virtual_tryon_task`.
    *   `GET /ingestion/status/{id}`: Generic task status poller (proxies Celery AsyncResult).

### 3. Database Layer
*   **Tech**: PostgreSQL 15, SQLAlchemy ORM.
*   **Current State**: Single `Garments` table.
*   **Schema**:
    *   `id` (UUID)
    *   `raw_image_path`, `processed_image_path` (System Paths)
    *   `metadata_json` (JSONB for Gemini tags)
    *   `created_at` (Timestamp)

### 4. GPU Worker (Docker)
*   **Tech**: Python 3.10, Celery, PyTorch (CUDA 11.8).
*   **Environment**: Docker container with `nvidia-container-toolkit` enabled.
*   **Task Layout**:
    *   `remove_background_task`: Uses `rembg` (CPU/GPU) to clean garment images.
    *   `extract_metadata_task`: Calls Google Gemini API for tagging.
    *   `virtual_tryon_task`: Runs the heavy VTON Pipeline.

### 5. VTON AI Pipeline (`vton_pipeline.py`)
*   **Tech**: `diffusers`, `transformers`, `h94/IP-Adapter`.
*   **Models**:
    *   **Inpainter**: `runwayml/stable-diffusion-inpainting`.
    *   **Conditioning**: `h94/IP-Adapter` (sd1.5 version) with scale `0.7`.
    *   **Masking**: `rembg` with `u2net_cloth_seg` (Automatic cloth segmentation).
*   **Current Flow**:
    1.  Receive Person Image + Garment Image.
    2.  Segment clothing on Person (Mask Generation).
    3.  Run Inpainting guided by Text Prompt + Garment Image (IP-Adapter).

---

## Next Steps & Improvements

### Immediate Refinements
1.  **VTON Quality**:
    *   Switch from generic SD 1.5 Inpainting to **IDM-VTON** (Yisol) specialized model for better sleeve/neck handling.
    *   Improve masking: Handle "lower body" vs "upper body" segmentation logic.
2.  **Frontend Polish**:
    *   Add "Delete Garment" functionality.
    *   Show metadata tags in the UI (Category, Color).

### Future Roadmap
1.  **Vector Search**:
    *   Generate embeddings for garments (CLIP).
    *   Allow text search "Show me red dresses" using `pgvector`.
2.  **User Accounts**:
    *   Multi-user support with Clerk or NextAuth.
3.  **Deployment**:
    *   Move from localhost to a cloud GPU provider (RunPod/Lambda Labs).
