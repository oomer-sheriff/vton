# Module: Frontend Architecture

**Goal**: Premium, responsive, and interactive user interface for the virtual closet.

## Technology Stack
*   **Framework**: **Next.js 14+** (App Router).
*   **Language**: TypeScript.
*   **Styling**: **Tailwind CSS**.
*   **Animations**: **Framer Motion**.

## Key UI Components

### 1. The Magic Mirror (Split/Swap View)
*   A component that shows the "Before" (User Photo) and "After" (Try-On Result).
*   **Interaction**: Slider to compare, or a "morph" animation when result arrives.

### 2. The Catalogue Drawer
*   A scrollable grid of garments (fetched from Ingestion API).
*   Each item shows the clean, background-removed thumbnail.

### 3. Upload Zone
*   Drag-and-drop area for user selfies.
*   Client-side validation (ensure full body is likely visible, file size limits).

### 4. Real-time Feedback
*   Since generation is async, the UI must poll or use WebSockets/SSE to show a progress bar.
*   *"Designing fit..."*, *"Aligning pose..."* specific loading states to keep user engaged.

## State Management
*   **Zustand**: For simple global state (Selected Garment, Current User Image, Session ID).
*   **React Query**: For fetching catalogues and polling task status.
