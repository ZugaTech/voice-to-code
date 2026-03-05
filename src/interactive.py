import sys
import datetime
import typer
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.syntax import Syntax

from src.config import config
from src.recorder import record_until_silence
from src.transcriber import transcribe
from src.converter import converter, ConversionRequest, ConversionMode
from src.executor import execute_bash, execute_python, is_safe_to_autorun
from src.history import HistoryManager, HistoryEntry

console = Console()
app = typer.Typer(help="Voice-to-Code Assistant")
history = HistoryManager(config.HISTORY_FILE)

def interactive_loop(mode: str):
    console.print(f"[bold blue]Starting session in {mode.upper()} mode.[/]")
    console.print(f"Speak naturally. Silence for 1.5 seconds automatically stops recording. Press Ctrl+C to quit.")
    
    while True:
        try:
            # 1. Record
            audio = record_until_silence(device=config.MIC_DEVICE_INDEX)
            
            # 2. Transcribe
            with console.status("Transcribing..."):
                transcription = transcribe(audio)
            console.print(f"\n[bold magenta]You said:[/] {transcription.text}")
            
            # 3. Convert
            with console.status(f"Converting to {mode}..."):
                req = ConversionRequest(
                    text=transcription.text,
                    mode=getattr(ConversionMode, mode.lower(), ConversionMode.auto),
                    previous_commands=history.get_context()
                )
                result = converter.process(req)
                
            syntax = Syntax(result.output, result.language, theme="monokai", line_numbers=False)
            console.print(Panel(syntax, title=f"Generated {result.mode_used}"))
            
            if result.warnings:
                for w in result.warnings:
                    console.print(f"⚠️  [yellow]{w}[/]")
            
            # 4. Execute
            safe = is_safe_to_autorun(result)
            run_cmd = False
            
            if config.AUTORUN and safe:
                 console.print("[green]Auto-running...[/]")
                 run_cmd = True
            else:
                 if not safe:
                      console.print("[bold red]⚠️  WARNING: Potentially unsafe/destructive command.[/]")
                 
                 choice = Prompt.ask("[R]un / [S]kip", choices=["r", "s", "R", "S"], default="s").lower()
                 if choice == "r":
                     run_cmd = True
            
            exit_code = None
            if run_cmd:
                 with console.status("Executing..."):
                     if result.mode_used == "bash":
                         exec_res = execute_bash(result.output)
                     else:
                         exec_res = execute_python(result.output)
                 
                 exit_code = exec_res.exit_code
                 if exit_code == 0:
                      console.print(f"[bold green]Stdout:[/] {exec_res.stdout}")
                 else:
                      console.print(f"[bold red]Stderr:[/] {exec_res.stderr}")
                      
            # 5. Save History
            entry = HistoryEntry(
                 timestamp=str(datetime.datetime.now()),
                 transcription=transcription.text,
                 mode=result.mode_used,
                 output=result.output,
                 executed=run_cmd,
                 exit_code=exit_code
            )
            history.append(entry)

        except KeyboardInterrupt:
            console.print("\n[yellow]Exiting session...[/]")
            break
        except Exception as e:
            console.print(f"\n[red]Error: {e}[/]")

@app.command()
def interact(mode: str = typer.Option("auto", help="Conversion mode: auto, bash, code")):
    """Start the interactive voice loop."""
    interactive_loop(mode)

@app.command()
def show_history():
    """Show previous commands run."""
    history.show()

@app.command()
def clear_history():
    """Clear command history."""
    if Confirm.ask("Are you sure you want to delete all history?"):
         history.clear()

if __name__ == "__main__":
    app()
