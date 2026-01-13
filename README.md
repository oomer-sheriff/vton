# VTON (Virtual Try-On) Application

An intelligent, microservice-based Virtual Try-On application. It combines semantic search with generative AI to provide a seamless product discovery and try-on experience.


## Features
- **Virtual Try-On**: Generate realistic try-on images using advanced diffusion models.
- **Semantic Search**: Text-to-image and image-to-image search capabilities powered by `sentence-transformers` and `pgvector`.
- **Microservice Architecture**:
  - **Backend**: FastAPI (Async)
  - **Frontend**: Next.js
  - **Workers**: Celery + RabbitMQ (Scalable & GPU-accelerated)
  - **Database**: PostgreSQL (pgvector)

## Documentation
- **[Master Plan](docs/master_plan.md)**: Project roadmap and high-level goals.
- **[Architecture Overview](docs/architecture_overview.md)**: System design and component interaction.
- **[Backend Architecture](docs/backend_architecture.md)**: Detailed API and worker design.
- **[Frontend Architecture](docs/frontend_architecture.md)**: Frontend components and state management.

## Quick Start (Docker Compose)
Best for local testing with GPU support.

1. **Clone & Setup**:
   ```bash
   git clone <repository-url>
   cd vton
   ```

2. **Run Backend & Services**:
   ```bash
   docker-compose up --build
   ```

3. **Run Frontend**:
   Open a new terminal:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. **Use**:
   - Frontend: `http://localhost:3000`
   - API Docs: `http://localhost:8000/docs`

## Quick Start (Kubernetes)
*(Coming Soon)*
