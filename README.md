# VTON (Virtual Try-On) Application

An intelligent, microservice-based Virtual Try-On application. It combines semantic search with generative AI to provide a seamless product discovery and try-on experience.

## Features

- **Virtual Try-On**: Generate realistic try-on images using a dual generative pipeline — a Stable Diffusion route and a toggleable Flux-2 route.
- **Semantic Search**: Text-to-image and image-to-image search capabilities powered by `sentence-transformers` and `pgvector`.
- **Microservice Architecture**:
  - **Backend**: FastAPI (Async)
  - **Frontend**: Next.js
  - **Workers**: Celery + RabbitMQ (Scalable & GPU-accelerated)
  - **Database**: PostgreSQL (pgvector)

## Generative Pipelines

The system supports two interchangeable generation routes, selectable at inference time:

### 1. Stable Diffusion route
The original try-on pipeline, built on Stable Diffusion for garment-swap inpainting.

### 2. Flux-2 route (toggleable)
An alternative pipeline built around a **Quantized Rectified Flow Transformer (Flux-2 Klein)** with a custom **LoRA adapter** fine-tuned for cloth-swap tasks. Highlights, based on our internal research writeup (see [Research](#research) below):

- Runs at **Q2 quantization**, fitting fully in VRAM on consumer 12 GB GPUs.
- Uses **fixed-step flow matching at 4 denoising steps**, bringing inference down to roughly 8–10 seconds per image on 12 GB VRAM hardware (vs. 25–60s for typical full diffusion pipelines).
- LoRA adapter (default merge strength 0.85) preserves high-frequency garment detail — logos, embroidery, knit texture — that standard diffusion pipelines tend to blur.
- Automated preprocessing: `Rembg` for garment background/foreground extraction, Gemini Flash API for garment captioning, `Qwen_4b` (quantized) as the text/image conditioning encoder.

Both routes share the same FastAPI → RabbitMQ → Celery → Redis backend, so switching routes doesn't change the deployment topology — only which model the worker loads.

## Documentation

- **[Master Plan](https://github.com/Rubans231/Virtual-Try-On/blob/main/docs/master_plan.md)**: Project roadmap and high-level goals.
- **[Architecture Overview](https://github.com/Rubans231/Virtual-Try-On/blob/main/docs/architecture_overview.md)**: System design and component interaction.
- **[Backend Architecture](https://github.com/Rubans231/Virtual-Try-On/blob/main/docs/backend_architecture.md)**: Detailed API and worker design.
- **[Frontend Architecture](https://github.com/Rubans231/Virtual-Try-On/blob/main/docs/frontend_architecture.md)**: Frontend components and state management.

## Research

[`docs/journal.docx`](docs/journal.docx) is our project writeup covering the Flux-2 route in depth: motivation, related work (CP-VTON+, VITON-HD, GP-VTON, TryOnDiffusion, StableVITON, OOTDiffusion, IDM-VTON, CAT-DM), the quantized rectified flow + LoRA architecture, dataset preparation, and evaluation.

Summary of what's in there:
- **Problem**: existing GAN- and diffusion-based VTON methods either distort textures/warp garments poorly, or are too slow (25–60s) for real-time use.
- **Approach**: a Flux-2 Klein backbone (rectified flow transformer) distilled and quantized to Q2, paired with a LoRA adapter trained on a ~90-sample custom dataset (garment images + human images + ComfyUI-generated targets), running fixed-step flow matching at 4 steps.
- **Result**: ~2s generation on 12 GB VRAM hardware in the optimized configuration, SSIM 0.858 / FID 11.7 / LPIPS 0.039, outperforming evaluated baselines on these metrics.
- **Scaling test**: near-linear throughput scaling across Celery workers (~30 req/min single worker → ~60 req/min with two workers).
- **Search eval**: 0.78 top-5 precision on text-to-image garment retrieval over a 500-item catalog.
- **Future work**: broader LoRA training data (body types, skin tones, poses), single-pass full-outfit generation, ControlNet/DensePose conditioning for non-frontal poses, video VTON, and a lighter mobile-oriented model variant.

## Quick Start (Docker Compose)

Best for local testing with GPU support.

1. **Clone & Setup**:

   ```
   git clone <repository-url>
   cd vton
   ```

2. **Run Backend & Services**:

   ```
   docker-compose up --build
   ```

3. **Run Frontend**:
   Open a new terminal:

   ```
   cd frontend
   npm install
   npm run dev
   ```

4. **Use**:
   - Frontend: `http://localhost:3000`
   - API Docs: `http://localhost:8000/docs`
   - Toggle the generation route (Stable Diffusion / Flux-2) from the try-on studio in the frontend, or via the relevant backend config — see [Backend Architecture](https://github.com/Rubans231/Virtual-Try-On/blob/main/docs/backend_architecture.md) for the flag/setting name.

## Quick Start (Kubernetes)

*(Coming Soon)*
