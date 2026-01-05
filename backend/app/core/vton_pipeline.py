from rembg import remove, new_session
import torch
from diffusers import AutoPipelineForInpainting, UNet2DConditionModel, EulerDiscreteScheduler
from PIL import Image
import os
import numpy as np
import io
from app.core.densepose_estimator import DensePoseEstimator

class VTONPipeline:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VTONPipeline, cls).__new__(cls)
            cls._instance.pipeline = None
            cls._instance.mask_session = None
            cls._instance.densepose_estimator = None
            cls._instance.device = "cuda" if torch.cuda.is_available() else "cpu"
        return cls._instance

    def load_model(self):
        if self.pipeline is None:
            print(f"Loading VTON Pipeline on {self.device}...")
            try:
                # 1. Load Masking Model (Cloth Segmentation)
                if self.mask_session is None:
                    print("Loading Cloth Segmentation Model (u2net_cloth_seg)...")
                    self.mask_session = new_session("u2net_cloth_seg")

                # 2. Load DensePose Estimator
                # Note: Detectron2 projects are not always installed via pip. 
                # We will make this optional to prevent blocking the IP-Adapter pipeline.
                if self.densepose_estimator is None:
                    try:
                        self.densepose_estimator = DensePoseEstimator(device=self.device)
                    except Exception as dp_error:
                        print(f"[{dp_error}] DensePose disabled (Optional). Continuing with IP-Adapter only.")
                        self.densepose_estimator = None

                # 3. Load Inpainting Model with IP-Adapter Plus
                print("Loading Inpainting Model + IP-Adapter Plus...")
                model_id = "runwayml/stable-diffusion-inpainting"
                self.pipeline = AutoPipelineForInpainting.from_pretrained(
                    model_id,
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                    variant="fp16" if self.device == "cuda" else None
                ).to(self.device)
                
                # IP-Adapter Plus requires the image encoder to be loaded? 
                # Diffusers load_ip_adapter handles it if 'h94/IP-Adapter' repo structure is standard.
                # using 'ip-adapter-plus_sd15.bin' gives better results for clothing details.
                self.pipeline.load_ip_adapter("h94/IP-Adapter", subfolder="models", weight_name="ip-adapter-plus_sd15.bin")
                self.pipeline.set_ip_adapter_scale(1.0) # Strong conditioning
                
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
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_bytes = img_byte_arr.getvalue()

        output_bytes = remove(img_bytes, session=self.mask_session)
        result_img = Image.open(io.BytesIO(output_bytes))
        
        mask = result_img.split()[-1] # A channel
        return mask

    def run(self, person_image_path: str, garment_image_path: str):
        self.load_model()
        
        person_img = self.preprocess_image(person_image_path)
        garment_img = self.preprocess_image(garment_image_path)
        
        # 1. Generate Cloth Mask
        print("Generating cloth mask...")
        mask_img = self.generate_mask(person_img)
        
        # DEBUG: Save mask
        debug_mask_path = person_image_path.replace(".jpg", "_mask.png").replace(".png", "_mask.png").replace(".webp", "_mask.png")
        mask_img.save(debug_mask_path)
        
        # 2. Generate DensePose (Optional)
        if self.densepose_estimator:
            try:
                print("Generating DensePose...")
                densepose_img = self.densepose_estimator.run(person_img)
                debug_pose_path = person_image_path.replace(".jpg", "_densepose.png").replace(".png", "_densepose.png").replace(".webp", "_densepose.png")
                densepose_img.save(debug_pose_path)
            except Exception as e:
                print(f"DensePose generation failed: {e}")
        else:
            print("Skipping DensePose (Model not loaded).")

        # 3. Run Inference with IP-Adapter Plus
        # Note: We are using just 'prompt' and 'ip_adapter_image' here.
        # To truly use DensePose, we would need ControlNet.
        # But switching to IP-Adapter Plus should improve the outfit transfer significantly alone.
        
        prompt = "model wearing this garment, best quality, photorealistic"
        negative_prompt = "monochrome, lowres, bad anatomy, worst quality, low quality"

        generator = torch.Generator(device=self.device).manual_seed(42)
        
        result = self.pipeline(
            prompt=prompt,
            negative_prompt=negative_prompt,
            image=person_img,
            mask_image=mask_img,
            ip_adapter_image=garment_img,
            guidance_scale=7.5,
            num_inference_steps=30,
            strength=0.99, # Force high denoising in mask area (1.0 = complete replacement)
            generator=generator
        ).images[0]
        
        output_path = person_image_path.replace(".jpg", "_tryon.png").replace(".png", "_tryon.png").replace(".webp", "_tryon.png")
        result.save(output_path)
        
        return output_path

vton_pipeline = VTONPipeline()
