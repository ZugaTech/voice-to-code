# Voice-to-Code Assistant

A complete local pipeline turning spoken commands directly into runnable code or bash executions, powered by OpenAI Whisper and GPT-4o.

Featuring a rich terminal user interface and an optional Web UI.

## Installation

```bash
pip install -e.
cp.env.example.env
```
Ensure you have PyAudio or `sounddevice` C libraries installed on your host if on Linux (`sudo apt-get install libportaudio2`).

## Usage

### 1. Interactive CLI Terminal
Drop into the continuous conversational state:
```bash
vtc interact --mode auto
```

Speak into your mic. Wait 1.5 seconds of silence, and the system will automatically transcribe, convert, and propose the code to run locally.

### 2. View History
```bash
vtc show-history
```

### 3. Web Interface
Host the FastAPI server:
```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000
```
Then navigate to `http://localhost:8000` to stream audio buffers completely via browser without downloading custom tooling.

## Security
Every command is run in an ephemeral sandbox. Basic blockers are integrated (`rm -rf`) but NEVER run this as system `root`. You must opt-in to execute using `[R]un / [S]kip` unless `AUTORUN=true` is set.