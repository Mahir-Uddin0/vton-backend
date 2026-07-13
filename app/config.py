from dotenv import load_dotenv
import os

load_dotenv()

HF_SPACE_NAME = os.getenv("HF_SPACE_NAME")

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS").split(",")

HOST = os.getenv("HOST")

PORT = int(os.getenv("PORT"))