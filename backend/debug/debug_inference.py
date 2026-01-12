import torch
from diffusers import StableDiffusionControlNetInpaintPipeline, ControlNetModel
from PIL import Image

device = "cpu"
print("Initializing models...")
controlnet = ControlNetModel.from_pretrained("MnLgt/densepose", torch_dtype=torch.float32).to(device)
pipe = StableDiffusionControlNetInpaintPipeline.from_pretrained(
    "runwayml/stable-diffusion-inpainting",
    controlnet=controlnet,
    torch_dtype=torch.float32,
    safety_checker=None
).to(device)

# Load IP Adapter manually to replicate environment
try:
    pipe.load_ip_adapter("h94/IP-Adapter", subfolder="models", weight_name="ip-adapter-plus_sd15.bin")
    pipe.set_ip_adapter_scale(1.0)
    print("IP Adapter Loaded.")
except Exception as e:
    print(f"IP Adapter Load Failed: {e}")

# Create Dummy Inputs (1024x1024 for simplicity, checking broadcast)
W, H = 768, 1024
image = Image.new("RGB", (W, H), (255, 255, 255))
mask = Image.new("RGB", (W, H), (0, 0, 0)) # Mask RGB
control_image = Image.new("RGB", (W, H), (100, 100, 100))
ip_adapter_image = Image.new("RGB", (224, 224), (0, 0, 255))

prompt = "test prompt"

print("--- Test 1: Full Pipeline ---")
try:
    pipe(
        prompt=prompt,
        image=image,
        mask_image=mask,
        control_image=control_image,
        ip_adapter_image=ip_adapter_image,
        num_inference_steps=1
    )
    print("Test 1 SUCCESS")
except Exception as e:
    print(f"Test 1 FAILED: {e}")

print("--- Test 2: No IP Adapter Image ---")
try:
    pipe(
        prompt=prompt,
        image=image,
        mask_image=mask,
        control_image=control_image,
        # ip_adapter_image=ip_adapter_image, 
        num_inference_steps=1
    )
    print("Test 2 SUCCESS")
except Exception as e:
    print(f"Test 2 FAILED: {e}")

print("--- Test 3: No Control Image (Expect Failure if required) ---")
try:
    pipe(
        prompt=prompt,
        image=image,
        mask_image=mask,
        # control_image=control_image,
        ip_adapter_image=ip_adapter_image,
        num_inference_steps=1
    )
    print("Test 3 SUCCESS")
except Exception as e:
    print(f"Test 3 FAILED: {e}")
