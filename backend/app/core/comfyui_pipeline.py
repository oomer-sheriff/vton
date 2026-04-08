import json
import urllib.request
import urllib.parse
import time
import os


class ComfyUIClient:
    def __init__(self):
        # Points to the ComfyUI service on the internal Docker network
        self.server_address = "http://comfyui:8188"
        self.client_id = "vton_api_client"

        with open("./app/core/workflow_api.json", "r") as f:
            self.workflow = json.load(f)

    def queue_prompt(self, prompt):
        p = {"prompt": prompt, "client_id": self.client_id}
        data = json.dumps(p).encode("utf-8")
        req = urllib.request.Request(f"{self.server_address}/prompt", data=data)
        response = urllib.request.urlopen(req)
        return json.loads(response.read())

    def check_status(self, prompt_id):
        req = urllib.request.Request(f"{self.server_address}/history/{prompt_id}")
        response = urllib.request.urlopen(req)
        return json.loads(response.read())

    def run(self, person_image_path: str, garment_image_path: str) -> str:
        """
        Dispatches a Flux 2 VTON job to ComfyUI and polls until complete.
        Returns the local path to the generated result image.
        """
        print("Sending VTON request to ComfyUI (transformer mode)...")

        # ComfyUI's input directory is mapped to `backend/media`.
        # person_image_path is usually `media/raw/file.ext`
        # We need to strip the leading `media/` so ComfyUI sees `raw/file.ext`
        person_rel_path = person_image_path.split("media/", 1)[-1]
        garment_rel_path = garment_image_path.split("media/", 1)[-1]

        # Inject image filenames into the workflow graph
        self.workflow["76"]["inputs"]["image"] = person_rel_path
        self.workflow["81"]["inputs"]["image"] = garment_rel_path

        try:
            queue_response = self.queue_prompt(self.workflow)
            prompt_id = queue_response["prompt_id"]
            print(f"Task queued in ComfyUI with prompt_id: {prompt_id}")

            # Poll until Node 94 (SaveImage) produces an output
            while True:
                history = self.check_status(prompt_id)
                if prompt_id in history:
                    print("ComfyUI generation complete.")
                    outputs = history[prompt_id]["outputs"]

                    if "94" in outputs and "images" in outputs["94"]:
                        final_filename = outputs["94"]["images"][0]["filename"]
                        print(f"Output image: {final_filename}")

                        # The result lives in the shared media/results volume
                        base_media_dir = os.path.dirname(os.path.dirname(person_image_path))
                        result_path = os.path.join(
                            base_media_dir,
                            "results",
                            final_filename,
                        )
                        return result_path
                    else:
                        raise Exception(
                            "ComfyUI finished but Node 94 produced no image."
                        )

                time.sleep(2)

        except Exception as e:
            print(f"ComfyUI inference failed: {e}")
            raise


# Module-level singleton — imported by transformer_tasks
comfyui_pipeline = ComfyUIClient()
