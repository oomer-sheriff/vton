import os
from celery import shared_task
from rembg import remove
from PIL import Image
import io

@shared_task(name="app.worker.tasks.remove_background_task")
def remove_background_task(input_path: str, output_path: str):
    """
    Reads an image from input_path, removes background, removes any alpha matting artifacts,
    resizes to standard VTON size (768x1024), and saves to output_path.
    """
    try:
        # Load image
        with open(input_path, "rb") as input_file:
            input_data = input_file.read()

        # Remove background
        # alpha_matting=True improves edges for hair/transparency but is slower.
        output_data = remove(input_data, alpha_matting=True)
        
        # Post-process with PIL
        image = Image.open(io.BytesIO(output_data)).convert("RGBA")
        
        # Standardize size (Optional: Maintain aspect ratio or force fit)
        # For now, we resize to fixed width of 768, maintaining aspect ratio
        base_width = 768
        w_percent = (base_width / float(image.size[0]))
        h_size = int((float(image.size[1]) * float(w_percent)))
        image = image.resize((base_width, h_size), Image.Resampling.LANCZOS)

        # Save
        image.save(output_path, "PNG")
        
        return {"status": "completed", "output_path": output_path}
    except Exception as e:
        return {"status": "failed", "error": str(e)}

@shared_task(name="app.worker.tasks.extract_metadata_task")
def extract_metadata_task(image_path: str):
    """
    Uses Gemini 1.5 Flash to extract metadata from the garment image.
    Returns a JSON object with category, color, pattern, etc.
    """
    try:
        import google.generativeai as genai
        from app.core.config import settings
        
        if not settings.GEMINI_API_KEY:
             return {"status": "skipped", "reason": "No API Key"}

        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')

        # Load image
        img = Image.open(image_path)

        prompt = """
        Analyze this garment image and return a JSON object with the following fields:
        - category: (e.g., dress, top, pants, skirt)
        - color: (primary color)
        - pattern: (e.g., solid, floral, striped, plaid)
        - sleeve_length: (e.g., sleeveless, short, long)
        - neckline: (e.g., v-neck, crew, collar)
        - style_tags: [list of 3-5 style keywords]
        
        Return ONLY the JSON.
        """
        
        response = model.generate_content([prompt, img])
        # simple cleanup in case it returns markdown blocks
        text = response.text.replace("```json", "").replace("```", "").strip()
        
        return {"status": "completed", "metadata": text}
    except Exception as e:
        return {"status": "failed", "error": str(e)}
