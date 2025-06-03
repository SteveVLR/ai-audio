import streamlit as st
import requests
import tempfile
import os
import ffmpeg
from transformers import Wav2Vec2ForSequenceClassification, Wav2Vec2FeatureExtractor
import torch
import numpy as np
import soundfile as sf

# Title
st.title("English Accent Detection Tool")

# --- Shared logic for audio extraction and accent analysis ---
def download_video(url):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_video:
            for chunk in response.iter_content(chunk_size=8192):
                tmp_video.write(chunk)
            return tmp_video.name
    except Exception as e:
        raise RuntimeError(f"Failed to download video: {e}")

def extract_audio(video_path):
    try:
        # Check for audio stream using ffprobe
        probe = ffmpeg.probe(video_path)
        audio_streams = [stream for stream in probe['streams'] if stream['codec_type'] == 'audio']
        if not audio_streams:
            raise RuntimeError("No audio stream found in the video file.")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_audio:
            audio_path = tmp_audio.name
        process = (
            ffmpeg
            .input(video_path)
            .output(audio_path, format='wav', acodec='pcm_s16le', ac=1, ar='16k')
            .overwrite_output()
            .run_async(pipe_stderr=True, quiet=True)
        )
        _, stderr = process.communicate()
        if process.returncode != 0:
            raise RuntimeError(f"ffmpeg error: {stderr.decode('utf-8')}")
        return audio_path
    except Exception as e:
        raise RuntimeError(f"Failed to extract audio: {e}")

# Load model and feature extractor once
def load_accent_model():
    model_name = "dima806/english_accents_classification"
    model = Wav2Vec2ForSequenceClassification.from_pretrained(model_name)
    extractor = Wav2Vec2FeatureExtractor.from_pretrained(model_name)
    return model, extractor

accent_model, accent_extractor = load_accent_model()
accent_labels = [
    'african', 'australia', 'bermuda', 'canada', 'england', 'hongkong', 'indian',
    'ireland', 'malaysia', 'newzealand', 'philippines', 'scotland', 'singapore',
    'southatlandtic', 'us', 'wales'
]

def analyze_accent(audio_path):
    try:
        # Load audio
        speech, sr = sf.read(audio_path)
        if len(speech.shape) > 1:
            speech = np.mean(speech, axis=1)  # Convert to mono if stereo
        # Preprocess
        inputs = accent_extractor(speech, sampling_rate=sr, return_tensors="pt", padding=True)
        with torch.no_grad():
            logits = accent_model(**inputs).logits
        scores = torch.softmax(logits, dim=1).detach().cpu().numpy()[0]
        best_idx = int(np.argmax(scores))
        accent = accent_labels[best_idx]
        confidence = float(scores[best_idx]) * 100
        summary = f"Detected accent: {accent.capitalize()} (Confidence: {confidence:.1f}%)"
        return {"accent": accent.capitalize(), "confidence": round(confidence, 1), "summary": summary}
    except Exception as e:
        raise RuntimeError(f"Failed to analyze accent: {e}")

# --- Streamlit UI ---
video_url = st.text_input("Enter a public video URL (MP4, Loom, etc.):")

if video_url and st.button("Analyze Accent"):
    with st.spinner("Processing..."):
        try:
            video_path = download_video(video_url)
            audio_path = extract_audio(video_path)
            result = analyze_accent(audio_path)
            os.remove(video_path)
            os.remove(audio_path)
            # Display the results
            st.subheader("Results:")
            st.write(f"**Accent:** {result['accent']}")
            st.write(f"**Confidence:** {result['confidence']}%")
            st.write(f"**Summary:** {result['summary']}")
        except Exception as e:
            st.error(f"Error: {e}")

st.info("Paste a public video URL and press Enter to start.")
