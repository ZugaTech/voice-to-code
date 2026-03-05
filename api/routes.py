import io
import base64
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from src.recorder import AudioData
from src.transcriber import transcribe
from src.converter import converter, ConversionRequest, ConversionMode

router = APIRouter()

class AudioPayload(BaseModel):
    audio_base64: str

@router.post("/transcribe-convert")
async def handle_audio(payload: AudioPayload):
    try:
        # Decode blob
        wav_bytes = base64.b64decode(payload.audio_base64)
        audio = AudioData(wav_bytes=wav_bytes, sample_rate=16000, channels=1, duration_seconds=0.0)
        
        # 1. Transcribe
        transcription = transcribe(audio)
        
        # 2. Convert
        req = ConversionRequest(
            text=transcription.text,
            mode=ConversionMode.auto
        )
        result = converter.process(req)
        
        return {
            "status": "success",
            "transcription": transcription.text,
            "mode": result.mode_used,
            "language": result.language,
            "code": result.output,
            "warnings": result.warnings
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    # Simple streaming shell endpoint could go here
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        pass
