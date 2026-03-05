import sounddevice as sd
import numpy as np
import io
import time
import wave
from dataclasses import dataclass
from rich.console import Console

console = Console()

@dataclass
class AudioData:
    wav_bytes: bytes
    sample_rate: int
    channels: int
    duration_seconds: float

def list_microphones():
    devices = sd.query_devices()
    inputs = []
    for i, dev in enumerate(devices):
        if dev['max_input_channels'] > 0:
            inputs.append((i, dev['name']))
    return inputs

def generate_wav_bytes(audio_array: np.ndarray, sample_rate: int) -> bytes:
    # Scale float to int16
    audio_int16 = np.int16(audio_array * 32767)
    buffer = io.BytesIO()
    with wave.open(buffer, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio_int16.tobytes())
    return buffer.getvalue()

def record_fixed_duration(seconds: float, device=None, sample_rate=16000) -> AudioData:
    console.print(f"[bold red]Recording for {seconds} seconds...[/]")
    recording = sd.rec(int(seconds * sample_rate), samplerate=sample_rate, channels=1, device=device)
    sd.wait()
    console.print("[bold green]Recording complete.[/]")
    return AudioData(
        wav_bytes=generate_wav_bytes(recording, sample_rate),
        sample_rate=sample_rate,
        channels=1,
        duration_seconds=seconds
    )

def record_until_silence(silence_threshold_db=-40, min_duration=1.0, max_duration=30.0, device=None, sample_rate=16000) -> AudioData:
    console.print("[bold red]🎤 Listening... (speak now)[/]")
    
    chunk_duration = 0.1
    chunk_samples = int(sample_rate * chunk_duration)
    silence_limit_seconds = 1.5
    silence_chunks_limit = int(silence_limit_seconds / chunk_duration)
    
    recorded_chunks = []
    silent_chunks = 0
    total_time = 0.0
    
    # Pre-allocate reference arrays for speed
    def get_db(chunk):
        rms = np.sqrt(np.mean(chunk**2))
        if rms == 0: return -100
        return 20 * np.log10(rms)

    stream = sd.InputStream(samplerate=sample_rate, channels=1, device=device)
    with stream:
        while total_time < max_duration:
            chunk, overflowed = stream.read(chunk_samples)
            recorded_chunks.append(chunk)
            total_time += chunk_duration
            
            db = get_db(chunk)
            
            # Simple volume meter
            bars = int((db + 60) / 2) if db > -60 else 0
            meter = "|" * bars
            print(f"\rVolume: [{meter:<30}] {db:.1f} dB", end="")
            
            if db < silence_threshold_db:
                silent_chunks += 1
            else:
                silent_chunks = 0
                
            if total_time > min_duration and silent_chunks >= silence_chunks_limit:
                break
                
    print("\n[bold green]Recording stopped due to silence.[/]")
    audio_array = np.concatenate(recorded_chunks, axis=0)
    
    return AudioData(
        wav_bytes=generate_wav_bytes(audio_array, sample_rate),
        sample_rate=sample_rate,
        channels=1,
        duration_seconds=total_time
    )
