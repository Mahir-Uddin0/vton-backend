from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import Response
import asyncio, os
from tempfile import NamedTemporaryFile
from gradio_client import Client, handle_file

from app.config import ALLOWED_ORIGINS
from fastapi.middleware.cors import CORSMiddleware

from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the gradio_client once for all requests
from app.config import HF_SPACE_NAME, HF_TOKEN

import inspect
import gradio_client
from gradio_client import Client

print("gradio_client version:", gradio_client.__version__)
print("Client imported from:", inspect.getfile(Client))
print("Client signature:", inspect.signature(Client.__init__))

client = Client(HF_SPACE_NAME, token=HF_TOKEN)

@app.post("/tryon")
async def generate_tryon(
    person_image: UploadFile = File(...),
    garment_image: UploadFile = File(...),
    description: str = Form(...)
):
    # Save uploaded files to temporary files
    try:
        suffix_p = os.path.splitext(person_image.filename)[1] or ".jpg"
        person_temp = NamedTemporaryFile(delete=False, suffix=suffix_p)
        person_bytes = await person_image.read()
        person_temp.write(person_bytes); person_temp.flush(); person_temp.close()
        person_path = person_temp.name

        suffix_g = os.path.splitext(garment_image.filename)[1] or ".jpg"
        garment_temp = NamedTemporaryFile(delete=False, suffix=suffix_g)
        garment_bytes = await garment_image.read()
        garment_temp.write(garment_bytes); garment_temp.flush(); garment_temp.close()
        garment_path = garment_temp.name
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving uploads: {e}")

    # Call the IDM-VTON space via gradio_client (asynchronously)
    try:
        job = client.submit(
            dict={
                "background": handle_file(person_path),
                "layers": [],
                "composite": handle_file(person_path)
            },
            garm_img=handle_file(garment_path),
            garment_des=description,
            is_checked=True,
            is_checked_crop=False,
            denoise_steps=30,
            seed=42,
            api_name="/tryon"
        )
        # Wait for the prediction result in a thread to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, job.result)
    except Exception as e:
        os.remove(person_path); os.remove(garment_path)
        raise HTTPException(status_code=502, detail=f"Inference failed: {e}")

    # Read the generated image and clean up
    try:
        output_path, mask_path = result  # result is (image_path, mask_path)
        with open(output_path, "rb") as img_file:
            image_data = img_file.read()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading result: {e}")
    finally:
        # Remove all temp files
        for path in [person_path, garment_path, output_path, mask_path]:
            if path and os.path.exists(path):
                os.remove(path)

    # Return image bytes with proper MIME type
    return Response(content=image_data, media_type="image/png")
