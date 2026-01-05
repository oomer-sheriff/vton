FROM python:3.10-slim

WORKDIR /app

# Install system dependencies (for rembg and building python packages)
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    git \
    && rm -rf /var/lib/apt/lists/*


COPY requirements.txt .
# Install torch first because detectron2 needs it for setup.py
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Clone Detectron2 to get the Projects (DensePose) which are not in the pip package
RUN git clone https://github.com/facebookresearch/detectron2.git /opt/detectron2 && \
    pip install -e /opt/detectron2

RUN pip install --no-cache-dir -r requirements.txt

# Add DensePose to Python Path
ENV PYTHONPATH=$PYTHONPATH:/opt/detectron2/projects/DensePose

COPY . .

# Expose port (FastAPI)
EXPOSE 8000

# Default command (overridden by docker-compose)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
