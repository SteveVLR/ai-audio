# English Accent Detection Tool

This project provides a simple web UI (Streamlit) and a REST API (FastAPI) to analyze the accent from a public video URL. It extracts audio from the video, analyzes the speaker’s accent, and returns a classification and confidence score.

## Features
- Accepts a public video URL (MP4, Loom, etc.)
- Extracts audio from the video
- Analyzes the speaker’s accent (English/Non-English)
- Provides a confidence score
- Web UI (Streamlit) and REST API (FastAPI)

## Prerequisites
- [Docker](https://www.docker.com/products/docker-desktop) installed on your system
- I would reccomend a NVIDIA GPU with 12+ GB of VRAM for this
- I used a 5090 but something like a 3090 or a 4070 should work.

## Build the Docker Image
```powershell
# In the project directory (where Dockerfile is located):
docker build -t accent-detector .
```

## Run the Docker Container
```powershell
docker run -p 8501:8501 -p 8000:8000 accent-detector
```

- The Streamlit web UI will be available at: http://localhost:8501

## Using the REST API
Send a POST request to `/analyze` with a JSON body:
```json
{
  "video_url": "https://example.com/video.mp4"
}
```

Example using `curl`:
```powershell
curl -X POST http://localhost:8000/analyze -H "Content-Type: application/json" -d '{"video_url": "https://example.com/video.mp4"}'
```

## Notes
- Both the web UI and API run in the same container.
- Make sure the video URL is publicly accessible.
