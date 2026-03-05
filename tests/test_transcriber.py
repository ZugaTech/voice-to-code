import pytest
import io
import wave
import numpy as np
import base64
from src.recorder import generate_wav_bytes, AudioData

def test_generate_wav_bytes():
    # 1 second of 440Hz sine wave
    sample_rate = 16000
    t = np.linspace(0, 1, sample_rate)
    audio_array = 0.5 * np.sin(2 * np.pi * 440 * t)
    
    wav_data = generate_wav_bytes(audio_array, sample_rate)
    
    # Check simple chunk integrity
    assert wav_data.startswith(b"RIFF")
    
    obj = io.BytesIO(wav_data)
    with wave.open(obj, "rb") as wf:
        assert wf.getnchannels() == 1
        assert wf.getsampwidth() == 2
        assert wf.getframerate() == 16000
        assert wf.getnframes() == 16000

def test_audio_data_model():
    data = AudioData(wav_bytes=b"dummy", sample_rate=16000, channels=1, duration_seconds=1.5)
    assert data.duration_seconds == 1.5
