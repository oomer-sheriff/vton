from rembg import remove, new_session
import torch
from diffusers import AutoPipelineForInpainting, UNet2DConditionModel, EulerDiscreteScheduler
from PIL import Image
import os
import numpy as np
import io

class VTONPipeline:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VTONPipeline, cls).__new__(cls)
            cls._instance.pipeline = None
            cls._instance.mask_session = None
            cls._instance.device = "cuda" if torch.cuda.is_available() else "cpu"
        return cls._instance

    def load_model(self):
        if self.pipeline is None:
            print(f"Loading VTON Pipeline on {self.device}...")
            try:
                # 1. Load Masking Model (Cloth Segmentation)
                if self.mask_session is None:
                    print("Loading Cloth Segmentation Model (u2net_cloth_seg)...")
                    # 'u2net_cloth_seg' segments cloths specifically
                    self.mask_session = new_session("u2net_cloth_seg")

                # 2. Load Inpainting Model
                model_id = "runwayml/stable-diffusion-inpainting"
                self.pipeline = AutoPipelineForInpainting.from_pretrained(
                    model_id,
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                    variant="fp16" if self.device == "cuda" else None
                ).to(self.device)
                
                # 3. Load IP-Adapter (for Garment Conditioning)
                print("Loading IP-Adapter for Garment Conditioning...")
                self.pipeline.load_ip_adapter("h94/IP-Adapter", subfolder="models", weight_name="ip-adapter_sd15.bin")
                self.pipeline.set_ip_adapter_scale(0.7) # High scale to force garment appearance
                
                self.pipeline.scheduler = EulerDiscreteScheduler.from_config(self.pipeline.scheduler.config)
                print("VTON Pipeline Loaded.")
                
            except Exception as e:
                print(f"Failed to load VTON model: {e}")
                raise e

    def preprocess_image(self, image_path):
        return Image.open(image_path).convert("RGB").resize((768, 1024))

    def generate_mask(self, image: Image.Image) -> Image.Image:
        """
        Generates a mask of the CLOTHING on the person.
        We use rembg with u2net_cloth_seg.
        """
        # Convert PIL to bytes
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_bytes = img_byte_arr.getvalue()

        # rembg returns the image with background removed. 
        # With u2net_cloth_seg, the "foreground" is the cloth.
        # So we just extract the alpha channel to get the mask.
        output_bytes = remove(img_bytes, session=self.mask_session)
        result_img = Image.open(io.BytesIO(output_bytes))
        
        # Extract Alpha channel as Mask
        mask = result_img.split()[-1] # A channel
        return mask

    def run(self, person_image_path: str, garment_image_path: str):
        self.load_model()
        
        person_img = self.preprocess_image(person_image_path)
        garment_img = self.preprocess_image(garment_image_path)
        
        # Generate Cloth Mask
        print("Generating cloth mask...")
        mask_img = self.generate_mask(person_img)
        
        # Run Inference
        # We pass the garment_img to the IP-Adapter to condition the generation
        prompt = "a person wearing this garment, high quality, photorealistic"
        
        generator = torch.Generator(device=self.device).manual_seed(42)
        
        result = self.pipeline(
            prompt=prompt,
            image=person_img,
            mask_image=mask_img,
            ip_adapter_image=garment_img,
            guidance_scale=7.5,
            num_inference_steps=30,
            generator=generator
        ).images[0]
        
        output_path = person_image_path.replace(".jpg", "_tryon.png").replace(".png", "_tryon.png").replace(".webp", "_tryon.png")
        result.save(output_path)
        
        return output_path

vton_pipeline = VTONPipeline()
