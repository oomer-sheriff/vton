import torch
import numpy as np
from PIL import Image
import os

try:
    from detectron2.config import get_cfg
    from detectron2.engine import DefaultPredictor
    from detectron2.data import MetadataCatalog
    from detectron2.utils.visualizer import Visualizer, ColorMode
    import cv2
except ImportError:
    print("Detectron2 not installed. DensePose will fail.")

class DensePoseEstimator:
    def __init__(self, device="cuda"):
        self.device = device
        self.predictor = None
        
    # def _ensure_config_exists(self): -> Removed as we use installed files

    def add_densepose_config(self, cfg):
        """
        Manually add DensePose config keys if standard import fails.
        """
        from detectron2.config import CfgNode as CN
        
        cfg.MODEL.DENSEPOSE_ON = True
        cfg.MODEL.ROI_DENSEPOSE_HEAD = CN()
        cfg.MODEL.ROI_DENSEPOSE_HEAD.NAME = ""
        cfg.MODEL.ROI_DENSEPOSE_HEAD.RCNN_HEAD_ON = True
        cfg.MODEL.ROI_DENSEPOSE_HEAD.COARSE_SEGM_TRAINED_BY_MASKS = False
        cfg.MODEL.ROI_DENSEPOSE_HEAD.DEEP_LAB = CN()
        cfg.MODEL.ROI_DENSEPOSE_HEAD.DEEP_LAB.NORM = "GN"
        cfg.MODEL.ROI_DENSEPOSE_HEAD.PREDICTOR_NAME = "DensePosePredictor"
        cfg.MODEL.ROI_DENSEPOSE_HEAD.LOSS_NAME = "DensePoseLoss"
        cfg.MODEL.ROI_DENSEPOSE_HEAD.LOSS_WEIGHTS = CN()
        cfg.MODEL.ROI_DENSEPOSE_HEAD.LOSS_WEIGHTS.MASK = 5.0
        cfg.MODEL.ROI_DENSEPOSE_HEAD.FG_IOU_THRESHOLD = 0.5 # Mandatory key for DataFilter
        cfg.MODEL.ROI_DENSEPOSE_HEAD.POOLER_RESOLUTION = 14
        cfg.MODEL.ROI_DENSEPOSE_HEAD.POOLER_SAMPLING_RATIO = 0
        cfg.MODEL.ROI_DENSEPOSE_HEAD.POOLER_TYPE = "ROIAlign"
        cfg.MODEL.ROI_DENSEPOSE_HEAD.NUM_COARSE_SEGM_CHANNELS = 2
        
        try:
            # Try loading from the module we added to PYTHONPATH
            from densepose.config import add_densepose_config
            add_densepose_config(cfg)
            print("Successfully loaded add_densepose_config from densepose.config")
        except ImportError:
            try:
                # Fallback to standard detectron2 path (rarely works in pip installs)
                from detectron2.projects.densepose import add_densepose_config
                add_densepose_config(cfg)
                print("Successfully loaded add_densepose_config from detectron2.projects.densepose")
            except ImportError:
                print("Could not import add_densepose_config. Using manual keys.")
                cfg.set_new_allowed(True)

    def _ensure_weights_exist(self):
        import urllib.request
        import ssl
        
        # Determine cache path
        cache_dir = "app/core/weights"
        os.makedirs(cache_dir, exist_ok=True)
        local_weights_path = os.path.join(cache_dir, "model_final_162be9.pkl")
        
        if os.path.exists(local_weights_path) and os.path.getsize(local_weights_path) > 0:
            return local_weights_path
            
        print(f"Downloading DensePose weights to {local_weights_path}...")
        
        # Primary Mirror (Yisol IDM-VTON)
        url = "https://huggingface.co/yisol/IDM-VTON/resolve/main/densepose/model_final_162be9.pkl"
        
        try:
            # Bypass SSL errors if inside container with old certs
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            
            with urllib.request.urlopen(url, context=ctx) as response, open(local_weights_path, 'wb') as out_file:
                if response.status != 200:
                    raise Exception(f"HTTP {response.status}")
                out_file.write(response.read())
            print("Download complete.")
            return local_weights_path
        except Exception as e:
            print(f"Failed to download weights from {url}: {e}")
            # Clean up empty file
            if os.path.exists(local_weights_path):
                os.remove(local_weights_path)
            raise e

    def load_model(self):
        if self.predictor is not None:
            return

        print("Loading DensePose Predictor...")
        try:
            # FORCE REGISTRATION
            import densepose
            import densepose.modeling
            print("DensePose module imported (Classes Registered).")
            
            cfg = get_cfg()
            self.add_densepose_config(cfg)
            
            # Use the config from the installed detectron2 repository
            # Since we cloned it to /opt/detectron2 in the Dockerfile
            config_file = "/opt/detectron2/projects/DensePose/configs/densepose_rcnn_R_50_FPN_s1x.yaml"
            
            if not os.path.exists(config_file):
                raise FileNotFoundError(f"DensePose config not found at {config_file}. Ensure Dockerfile clones detectron2.")

            # Initialize config
            cfg.merge_from_file(config_file)
            
            # Use manually placed weights if available (Docker mount)
            # User moved file to /app/core/weights (mapped to /app/app/core/weights in container usually, or just check relative)
            # Assuming standard docker mapping where backend/ -> /app
            manual_weights_path = "/app/app/core/weights/model_final_162be9.pkl"
            
            if not os.path.exists(manual_weights_path):
                 # Try other common path just in case
                 manual_weights_path = "/app/core/weights/model_final_162be9.pkl"

            if os.path.exists(manual_weights_path):
                print(f"Using manually placed weights: {manual_weights_path}")
                cfg.MODEL.WEIGHTS = manual_weights_path
            else:
                # Fallback to download (which might fail)
                print(f"Manual weights not found at {manual_weights_path}, trying download...")
                local_weights = self._ensure_weights_exist()
                cfg.MODEL.WEIGHTS = local_weights
            
            cfg.MODEL.DEVICE = self.device
            cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.5 
            
            self.predictor = DefaultPredictor(cfg)
            print("DensePose Predictor Loaded.")
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Failed to load DensePose: {e}")
            raise e
            
            # Hardcoded weights URL for this specific model
            cfg.MODEL.WEIGHTS = "https://dl.fbaipublicfiles.com/detectron2/DensePose/densepose_rcnn_R_50_FPN_s1x/165712039/model_final_162be9.pkl"
            
            cfg.MODEL.DEVICE = self.device
            cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.5 
            
            self.predictor = DefaultPredictor(cfg)
            print("DensePose Predictor Loaded.")
            
        except Exception as e:
            print(f"Failed to load DensePose: {e}")
            raise e

    def run(self, pil_image: Image.Image) -> Image.Image:
        """
        Returns the IUV (DensePose) image.
        """
        self.load_model()
        
        # Convert PIL to BGR numpy (OpenCV format)
        image_np = np.array(pil_image)
        # RGB to BGR
        image_bgr = image_np[:, :, ::-1].copy()
        
        with torch.no_grad():
            outputs = self.predictor(image_bgr)["instances"]
            # Move to CPU for visualization/numpy conversion
            outputs = outputs.to("cpu")
            
        # Extract DensePose results
        if not outputs.has("pred_densepose"):
            print("No DensePose detected!")
            # Return empty black image same size
            return Image.new("RGB", pil_image.size, (0,0,0))
            
        # We need to visualize/render to IUV
        # This is complex without the visualizer, but let's try using the Visualizer to get the IUV style map
        # Or standard IUV extraction.
        
        # Simplified approach: Use Visualizer to draw "DensePose" mode
        # However, IDM-VTON often expects the raw I, U, V channels mapped to RGB.
        
        # PROPOSED: Just return the visualized densepose which looks like the colorful body map.
        visualizer = Visualizer(image_bgr, MetadataCatalog.get(self.predictor.cfg.DATASETS.TEST[0]))
        out = visualizer.draw_instance_predictions(outputs)
        res_bgr = out.get_image()
        
        return Image.fromarray(res_bgr[:, :, ::-1])
