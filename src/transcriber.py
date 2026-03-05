import io
from openai import OpenAI
from dataclasses import dataclass
from typing import Optional, List
from src.config import config
from src.recorder import AudioData
from rich.console import Console

console = Console()
client = OpenAI(api_key=config.OPENAI_API_KEY)

@dataclass
class WordTiming:
    word: str
    start: float
    end: float
    confidence: float

@dataclass
class TranscriptionResult:
    text: str
    language_detected: str
    duration_seconds: float
    words: Optional[List[WordTiming]] = None

def transcribe(audio: AudioData, language: Optional[str] = None) -> TranscriptionResult:
    if not config.OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is not set.")
    
    buffer = io.BytesIO(audio.wav_bytes)
    buffer.name = "audio.wav"
    
    kwargs = {
        "model": "whisper-1",
        "file": buffer,
        "response_format": "verbose_json",
        "timestamp_granularities": ["word"]
    }
    if language:
        kwargs["language"] = language

    resp = client.audio.transcriptions.create(**kwargs)
    
    result = TranscriptionResult(
        text=resp.text,
        language_detected=resp.language,
        duration_seconds=resp.duration
    )
    
    if hasattr(resp, 'words') and resp.words:
        result.words = [
            WordTiming(w.word, w.start, w.end, getattr(w, 'probability', 1.0)) 
            for w in resp.words
        ]
        
        # Check confidences
        avg_conf = sum([w.confidence for w in result.words]) / len(result.words)
        if avg_conf < 0.7:
             console.print("[bold yellow]Warning: Transcription confidence is low. Background noise?[/]")
             
    return result

def transcribe_file(filepath: str, language: Optional[str] = None) -> TranscriptionResult:
    with open(filepath, "rb") as f:
        wav_bytes = f.read()
    
    # Mock some AudioData props just to reuse transcribe() cleanly
    audio = AudioData(wav_bytes=wav_bytes, sample_rate=16000, channels=1, duration_seconds=0.0)
    return transcribe(audio, language)
