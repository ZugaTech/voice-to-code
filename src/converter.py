import json
from enum import Enum
from pydantic import BaseModel
from typing import List, Optional
from openai import OpenAI
from src.config import config

client = OpenAI(api_key=config.OPENAI_API_KEY)

class ConversionMode(str, Enum):
    code = "code"
    bash = "bash"
    explain = "explain"
    auto = "auto"

class ConversionRequest(BaseModel):
    text: str
    mode: ConversionMode = ConversionMode.auto
    context: Optional[str] = None
    language_hint: Optional[str] = config.DEFAULT_LANGUAGE
    previous_commands: List[str] = []

class ConversionResult(BaseModel):
    mode_used: ConversionMode
    output: str
    language: str
    explanation: str
    warnings: List[str]
    is_destructive: bool

class Converter:
    def __init__(self):
        self.system_prompt = """You are a voice-to-code assistant. The user spoke a command. Convert it to executable code or a terminal command. Be concise. If the command is destructive (deletes files, modifies system settings, etc.), set is_destructive=true. Always return valid, runnable output.

Return your answer as a JSON object matching this schema:
{
  "mode_used": "one of: code, bash, explain",
  "output": "the actual code or terminal command",
  "language": "python, bash, javascript, etc.",
  "explanation": "short reasoning",
  "warnings": ["array of", "any warnings"],
  "is_destructive": true or false
}"""

    def _determine_mode(self, request: ConversionRequest) -> ConversionMode:
        return request.mode

    def process(self, request: ConversionRequest) -> ConversionResult:
        messages = [{"role": "system", "content": self.system_prompt}]
        
        # Build context
        if request.previous_commands:
             for cmd in request.previous_commands:
                  messages.append({"role": "user", "content": f"Previous context: {cmd}"})
                  
        if request.context:
             messages.append({"role": "user", "content": f"Selected code context:\n```\n{request.context}\n```"})
             
        user_message = f"Command: {request.text}"
        if request.mode != ConversionMode.auto:
             user_message += f"\nForce Mode: {request.mode.value}"
        if request.language_hint:
             user_message += f"\nLanguage Hint: {request.language_hint}"
             
        messages.append({"role": "user", "content": user_message})

        resp = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.1
        )
        
        return ConversionResult.parse_raw(resp.choices[0].message.content)

converter = Converter()
