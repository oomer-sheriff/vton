# Module: VTON Core Pipeline

**Goal**: Realistically visualize the selected garment on the user using Generative AI.

## Architecture: IDM-VTON (Improving Diffusion Models for VTON)

We utilize the SOTA **IDM-VTON** architecture, which allows for high-fidelity preservation of garment details without explicit 3D warping artifacts.

### Key Components

1.  **Pose Estimation (DensePose)**
    *   **Role**: Maps the 2D user photo to a 3D UV coordinate system.
    *   **Why**: Provides the "shape" guidance so the diffusion model knows body curvature.
    *   **Tool**: `detectron2` with DensePose config.

2.  **Auto-Masking (Graphonomy/SAM)**
    *   **Role**: Identifies the pixels of the *current* clothes the user is wearing.
    *   **Why**: We need to "erase" these pixels to give the AI a canvas to paint the new dress.
    *   **Tool**: `Graphonomy` (Universal Human Parsing).

3.  **Generative Warping (UNet + IP-Adapter)**
    *   **Role**: The core generation step.
    *   **Input**:
        *   `M`: Masked User Image (Input with clothes erased).
        *   `P`: DensePose Map (Shape guidance).
        *   `G`: Garment Image (The dress to try on).
    *   **Mechanism**: Cross-attention layers in the UNet attend to features extracted from `G` to paint realistic texture into the masked area of `M`.

## Implementation Strategy

### Containerization
This module contains heavy dependencies (PyTorch, CUDA, Diffusers). It should be isolated in its own Docker container or a dedicated Python environment.

### Inference Optimization
*   **Precision**: Use `torch.float16` for faster inference on consumer GPUs.
*   **Compilation**: Use `torch.compile()` if on Linux/WSL for 20% speedup.
*   **Scheduler**: Use `DPMSolverMultistepScheduler` for fewer steps (30 steps instead of 50).
