# VTON - Virtual Try-On Application

AI-powered virtual try-on system that lets users visualize how garments would look on them using Stable Diffusion, ControlNet, and IP-Adapter.

## 🏗️ Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Frontend  │────▶│   FastAPI   │────▶│   Celery    │
│  (Next.js)  │     │    (API)    │     │  (Worker)   │
└─────────────┘     └─────────────┘     └─────────────┘
                           │                   │
                    ┌──────┴──────┐     ┌──────┴──────┐
                    │  PostgreSQL │     │    Redis    │
                    │  (pgvector) │     │  RabbitMQ   │
                    └─────────────┘     └─────────────┘
```

## ✅ Prerequisites

- **Docker** with Docker Compose v2
- **NVIDIA GPU** with CUDA support (minimum 4GB VRAM)
- **NVIDIA Container Toolkit** installed ([Installation Guide](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html))
- **Node.js 18+** (for frontend development)

### Verify GPU Access
```bash
# Check NVIDIA drivers
nvidia-smi

# Check Docker GPU access
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
```

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/oomer-sheriff/vton.git
cd vton/vton
```

### 2. Create Environment File
```bash
# Create backend/.env
cat > backend/.env << EOF
POSTGRES_SERVER=db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=vton
REDIS_HOST=redis
RABBITMQ_HOST=rabbitmq
GEMINI_API_KEY=your_gemini_api_key_here
EOF
```

### 3. Start Backend Services
```bash
docker compose up -d --build
```

This starts:
- **API** (FastAPI) on `http://localhost:8000`
- **Worker** (Celery with GPU)
- **PostgreSQL** with pgvector extension
- **Redis** and **RabbitMQ**

### 4. Start Frontend
```bash
cd frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:3000`

## 📁 Project Structure

```
vton/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/    # API routes
│   │   ├── core/
│   │   │   ├── config.py        # Environment settings
│   │   │   ├── vton_pipeline.py # Main VTON logic
│   │   │   ├── embeddings.py    # Semantic search
│   │   │   └── densepose_estimator.py
│   │   ├── models/              # SQLAlchemy models
│   │   └── worker/              # Celery tasks
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                    # Next.js app
├── docker-compose.yml
└── README.md
```

## ⚙️ Configuration

All settings are in `backend/app/core/config.py` and can be overridden via environment variables in `backend/.env`:

### Core Settings
| Variable | Default | Description |
|----------|---------|-------------|
| `POSTGRES_SERVER` | `localhost` | Database host |
| `GEMINI_API_KEY` | - | For AI metadata extraction |

### VTON Pipeline Tuning
| Variable | Default | Description |
|----------|---------|-------------|
| `UNLOAD_PIPELINE_AFTER_TASK` | `true` | Free VRAM after each task |
| `VTON_IP_ADAPTER_SCALE` | `1.0` | Garment influence (0.5-1.0) |
| `VTON_CONTROLNET_SCALE` | `1.0` | Pose rigidity (0.7-1.0) |
| `VTON_INFERENCE_STRENGTH` | `0.99` | Regeneration amount (0.7-0.99) |
| `VTON_GUIDANCE_SCALE` | `7.5` | CFG scale |
| `VTON_VAE_FULL_PRECISION` | `false` | Decode in FP32 for color accuracy |

> **Tip**: For better color accuracy (especially yellows/oranges), set `VTON_VAE_FULL_PRECISION=true`

## 🔧 Common Commands

```bash
# View logs
docker compose logs -f worker

# Restart worker after code changes
docker compose restart worker

# Rebuild containers
docker compose up -d --build

# Stop all services
docker compose down

# Check API health
curl http://localhost:8000/health
```

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/ingestion/upload` | Upload garment image |
| `GET` | `/api/v1/ingestion/garments` | List garments (with semantic search) |
| `POST` | `/api/v1/tryon/` | Start virtual try-on |
| `GET` | `/api/v1/ingestion/status/{task_id}` | Check task status |

### Upload Garment Example
```bash
curl -X POST http://localhost:8000/api/v1/ingestion/upload \
  -F "file=@garment.jpg" \
  -F "category=top" \
  -F "color=red" \
  -F "description=Casual summer t-shirt"
```

## 🧠 Features

- **Virtual Try-On**: Stable Diffusion + ControlNet + IP-Adapter
- **Semantic Search**: Find garments using natural language (pgvector)
- **Auto Metadata Extraction**: Gemini AI analyzes uploaded garments
- **CPU Offloading**: Runs on 4GB VRAM GPUs
- **DensePose**: Body pose estimation for accurate garment placement

## 🐛 Troubleshooting

### CUDA Out of Memory
Ensure `UNLOAD_PIPELINE_AFTER_TASK=true` in your `.env`

### Color Issues (Yellow → Green, etc.)
Set `VTON_VAE_FULL_PRECISION=true`

### Worker Not Processing Tasks
```bash
docker compose restart worker
docker compose logs -f worker
```

### Database Connection Issues
```bash
docker compose restart db api
```

## 📄 License

MIT License
