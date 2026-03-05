import json
import os
import datetime
from rich.table import Table
from rich.console import Console
from pydantic import BaseModel
from typing import Optional

console = Console()

class HistoryEntry(BaseModel):
    timestamp: str
    transcription: str
    mode: str
    output: str
    executed: bool
    exit_code: Optional[int]

class HistoryManager:
    def __init__(self, history_file: str):
        self.file_path = history_file

    def append(self, entry: HistoryEntry):
        with open(self.file_path, 'a', encoding='utf-8') as f:
            f.write(entry.json() + "\n")

    def show(self, limit: int = 20):
        if not os.path.exists(self.file_path):
            console.print("[yellow]No history available.[/]")
            return

        entries = []
        with open(self.file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    entries.append(HistoryEntry.parse_raw(line))
        
        table = Table(title=f"Last {limit} Commands")
        table.add_column("Time", style="cyan")
        table.add_column("Input", style="magenta")
        table.add_column("Mode", style="green")
        table.add_column("Executed", justify="right")

        for entry in entries[-limit:]:
             table.add_row(
                 entry.timestamp.split('.')[0],
                 entry.transcription[:50] + "..." if len(entry.transcription) > 50 else entry.transcription,
                 entry.mode,
                 f"{'✅' if entry.executed else '⏳'} code: {entry.exit_code if entry.exit_code is not None else '-'}"
             )
        
        console.print(table)

    def clear(self):
        if os.path.exists(self.file_path):
            os.remove(self.file_path)
            console.print("[green]History cleared.[/]")
            
    def get_context(self, limit: int = 5) -> list[str]:
        if not os.path.exists(self.file_path):
            return []
        
        lines = []
        with open(self.file_path, 'r', encoding='utf-8') as f:
            lines = [l for l in f if l.strip()]
        
        entries = [json.loads(line)["transcription"] for line in lines[-limit:]]
        return entries
