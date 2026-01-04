# Module: Garment Ingestion Pipeline

**Goal**: Convert raw photos of clothes into high-quality digital assets ready for the VTON model.

## Workflow Description

1.  **Input**: Admin uploads a raw photo.
2.  **Preprocessing (Rembg)**:
    *   The system immediately processes the image using `rembg` (U-2-Net) to remove the background.
    *   **Output**: A 4-channel RGBA PNG image.
    *   **Normalization**: The image is resized to `768x1024` (Width x Height).
3.  **Metadata Extraction (VLM)**:
    *   The cleaned image is sent to a Vision Language Model (e.g., Gemini Flash or Moondream).
    *   **Prompt**: "Return JSON: { category, color, pattern, sleeve_length, neckline, style_tags }".
4.  **Persistence**:
    *   File saved to Object Storage (S3/MinIO).
    *   Metadata saved to Postgres.

## Technical Requirements

### Libraries
*   `rembg[gpu]`: For background removal.
*   `PIL` (Pillow): For image resizing and manipulation.
*   `google-generativeai` (or alternative VLM client): For metadata tagging.

### Data Schema (Garment)
```sql
CREATE TABLE garments (
    id UUID PRIMARY KEY,
    name VARCHAR(255),
    category VARCHAR(50), -- 'dress', 'top', 'pants'
    image_url TEXT,
    mask_url TEXT, -- Application specific mask if needed
    metadata JSONB, -- { "color": "red", "style": "casual" }
    created_at TIMESTAMP
);
```
