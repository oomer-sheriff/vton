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
                if self.densepose_estimator is None:
                    try:
                        self.densepose_estimator = DensePoseEstimator(device=self.device)
                    except Exception as dp_error:
                        print(f"[{dp_error}] DensePose disabled (Optional). Continuing with IP-Adapter only.")
                        self.densepose_estimator = None

                # 3. Load ControlNet (DensePose) & Inpainting Model
                print("Loading ControlNet + Inpainting Model + IP-Adapter Plus...")
                
                from diffusers import ControlNetModel, StableDiffusionControlNetInpaintPipeline
                
                # Load DensePose ControlNet
                controlnet = ControlNetModel.from_pretrained(
                    "MnLgt/densepose", 
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
                ).to(self.device)

                model_id = "runwayml/stable-diffusion-inpainting"
                self.pipeline = StableDiffusionControlNetInpaintPipeline.from_pretrained(
                    model_id,
                    controlnet=controlnet,
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                    variant="fp16" if self.device == "cuda" else None,
                    safety_checker=None
                ).to(self.device)
                
                # Load IP-Adapter Plus
                self.pipeline.load_ip_adapter("h94/IP-Adapter", subfolder="models", weight_name="ip-adapter-plus_sd15.bin")
                self.pipeline.set_ip_adapter_scale(1.0) 
                
                self.pipeline.scheduler = EulerDiscreteScheduler.from_config(self.pipeline.scheduler.config)
                print("VTON Pipeline Loaded (with ControlNet).")
                
            except Exception as e:
                print(f"Failed to load VTON model: {e}")
                raise e

    def preprocess_image(self, image_path):
        return Image.open(image_path).convert("RGB").resize((768, 1024))

    def generate_mask(self, image: Image.Image) -> Image.Image:
        """
        Generates a mask of the CLOTHING on the person.
        """
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_bytes = img_byte_arr.getvalue()

        output_bytes = remove(img_bytes, session=self.mask_session)
        result_img = Image.open(io.BytesIO(output_bytes))
        
        mask = result_img.split()[-1] # A channel
        
        # u2net_cloth_seg often returns vertically stacked images (Upper, Lower, Full)
        # If height is 3x width (or 3x intended height), split and merge.
        if mask.height == image.height * 3:
            print("Detected stacked cloth segmentation mask. Merging...")
            from PIL import ImageChops
            
            w, h = image.size
            top = mask.crop((0, 0, w, h))
            middle = mask.crop((0, h, w, h*2))
            bottom = mask.crop((0, h*2, w, h*3))
            
            # Combine all parts to mask ALL clothing
            merged = ImageChops.lighter(top, middle)
            merged = ImageChops.lighter(merged, bottom)
            return merged
            
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
        
        # 2. Generate DensePose
        densepose_img = None
        if self.densepose_estimator:
            try:
                print("Generating DensePose...")
                densepose_img = self.densepose_estimator.run(person_img)
                # Ensure it's the same size
                densepose_img = densepose_img.resize(person_img.size)
                
                debug_pose_path = person_image_path.replace(".jpg", "_densepose.png").replace(".png", "_densepose.png").replace(".webp", "_densepose.png")
                densepose_img.save(debug_pose_path)
            except Exception as e:
                print(f"DensePose generation failed: {e}")
        
        if densepose_img is None:
             # Create black image if DensePose failed
             densepose_img = Image.new("RGB", person_img.size, (0, 0, 0))

        # 3. Run Inference with ControlNet + IP-Adapter Plus
        prompt = "model wearing this garment, best quality, photorealistic"
        negative_prompt = "monochrome, lowres, bad anatomy, worst quality, low quality"

        generator = torch.Generator(device=self.device).manual_seed(42)
        
        # Ensure DensePose is RGB if present
        if densepose_img:
            densepose_img = densepose_img.convert("RGB")

        result = self.pipeline(
            prompt=prompt,
            negative_prompt=negative_prompt,
            image=person_img,
            mask_image=mask_img,
            control_image=densepose_img,  # Pass DensePose to ControlNet
            ip_adapter_image=garment_img, # Pass Garment to IP-Adapter
            controlnet_conditioning_scale=1.0, # Strong shape guidance
            guidance_scale=7.5,
            num_inference_steps=30,
            strength=0.99, 
            generator=generator
        ).images[0]
        
        output_path = person_image_path.replace(".jpg", "_tryon.png").replace(".png", "_tryon.png").replace(".webp", "_tryon.png")
        result.save(output_path)
        
        return output_path

vton_pipeline = VTONPipeline()
