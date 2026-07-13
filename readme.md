# Virtual Try-On Backend

A production-ready FastAPI backend for an AI-powered Virtual Try-On application using the open-source **IDM-VTON** model.

The backend exposes a REST API that accepts a person image, a garment image, and a garment description, then generates a virtual try-on result by communicating with the IDM-VTON inference service through the Hugging Face `gradio_client`.

This project is designed to be lightweight, asynchronous, containerized, and easily deployable to cloud platforms such as **AWS EC2**, **Google Cloud Platform (Cloud Run)** or **Render**.

---

## Features

- FastAPI-based REST API
- Asynchronous request handling
- Single shared `gradio_client` instance
- Temporary file management (no persistent storage)
- Dockerized for deployment
- CORS support for frontend integration

---

## Project Structure

```
backend/
│
├── app/
│   ├── main.py
│   └── ...
│
├── requirements.txt
├── Dockerfile
├── .dockerignore
├── .gitignore
├── .env.example
└── README.md
```

---

## Architecture

```
                +----------------------+
                |      Frontend        |
                | (Next.js / React)    |
                +----------+-----------+
                           |
                    HTTPS POST Request
                           |
                           ▼
                +----------------------+
                | FastAPI Backend      |
                | (This Repository)    |
                +----------+-----------+
                           |
                  gradio_client Request
                           |
                           ▼
                +----------------------+
                |     IDM-VTON         |
                | Hugging Face Space   |
                +----------------------+
```

The frontend communicates only with this backend.

The backend is responsible for:

- Receiving uploaded images
- Managing temporary files
- Calling the IDM-VTON inference API
- Returning the generated image

No images are stored permanently.

---

## Tech Stack

- Python 3.11
- FastAPI
- Uvicorn
- Gradio Client
- Docker

---

## API

### POST `/tryon`

Generates a virtual try-on image.

### Request

Content-Type

```
multipart/form-data
```

Parameters

| Name | Type | Description |
|-------|------|-------------|
| person_image | File | Image of the person |
| garment_image | File | Garment image |
| description | String | Garment description |

Example

```
person_image = person.jpg
garment_image = tshirt.png
description = "Full sleeve black t-shirt"
```

### Response

```
image/png
```

The endpoint returns the generated try-on image directly.

---

## Running Locally

### Clone

```bash
git clone https://github.com/<username>/<repo>.git
cd <repo>
```

### Create Virtual Environment

```bash
python -m venv venv
```

Linux

```bash
source venv/bin/activate
```

Windows

```bash
venv\Scripts\activate
```

---

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

### Environment Variables

Create a `.env` file.

```
HF_SPACE_NAME=yisol/IDM-VTON
HF_TOKEN=your_huggingface_access_token
ALLOWED_ORIGINS=http://localhost:5173
```

---

### Run

```bash
uvicorn app.main:app --reload
```

Swagger UI

```
http://localhost:8000/docs
```

---

## Docker

Build

```bash
docker build -t virtual-tryon-backend .
```

Run

```bash
docker run -p 8000:8000 virtual-tryon-backend
```

---

## Deployment

The application is fully containerized and can be deployed to:

- AWS EC2
- Render
- Google Cloud Run


Environment variables should be configured through the deployment platform instead of committing sensitive information to the repository.

---

## Design Decisions

### Why FastAPI?

FastAPI provides high-performance asynchronous request handling, automatic OpenAPI documentation, and native support for file uploads, making it well suited for AI inference APIs.

### Why a single `gradio_client` instance?

The Hugging Face client is initialized once during application startup and shared across all incoming requests. This avoids repeated initialization overhead and improves response time.

### Why asynchronous endpoints?

The IDM-VTON inference process can take several seconds. Asynchronous request handling allows the server to remain responsive while waiting for inference results.

### Why temporary files?

Uploaded images are stored only for the duration of the request. Once inference completes, all temporary files are removed automatically, ensuring minimal storage usage and improved privacy.

### Why no database?

This backend performs stateless inference only.

Since no user information, images, or inference history need to be retained, introducing a database would add unnecessary complexity.

---

## Security

- Sensitive credentials are stored as environment variables.
- No uploaded images are permanently stored.
- CORS is configurable for frontend domains.
- Temporary files are automatically cleaned after inference.

---

## Future Improvements

- Local IDM-VTON inference without Hugging Face dependency
- GPU deployment for lower latency
- Background task queue for high-volume requests
- Image caching
- Authentication
- Request rate limiting
- Monitoring and logging

---

## License

This project uses the open-source IDM-VTON model.

Please refer to the original repository for the model license and usage terms.

https://github.com/yisol/IDM-VTON