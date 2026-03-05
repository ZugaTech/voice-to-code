import os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class Config(BaseModel):
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    DEFAULT_MODE: str = os.getenv("DEFAULT_MODE", "auto")
    DEFAULT_LANGUAGE: str = os.getenv("DEFAULT_LANGUAGE", "python")
    AUTORUN: bool = os.getenv("AUTORUN", "false").lower() == "true"
    MIC_DEVICE_INDEX: int = int(os.getenv("MIC_DEVICE_INDEX", 0))
    HISTORY_FILE: str = os.path.expanduser("~/.voice-to-code/history.jsonl")

    def __init__(self, **data):
        super().__init__(**data)
        os.makedirs(os.path.dirname(self.HISTORY_FILE), exist_ok=True)

config = Config()
