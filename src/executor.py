import subprocess
import time
import re
from pydantic import BaseModel
from src.converter import ConversionResult

class ExecutionResult(BaseModel):
    stdout: str
    stderr: str
    exit_code: int
    execution_time_ms: float
    timed_out: bool

def is_safe_to_autorun(result: ConversionResult) -> bool:
    if result.is_destructive:
        return False
        
    blocklist_bash = ['rm -rf /', 'sudo', 'mkfs', 'dd if=', 'wget', 'curl']
    warning_bash = ['rm ', 'mv ', 'cp ', 'chmod ', 'kill ']
    
    if result.mode_used == "bash":
        cmd_lower = result.output.lower()
        for block in blocklist_bash:
            if block in cmd_lower:
                return False
        for warn in warning_bash:
            if warn in cmd_lower:
                return False
                
    if result.mode_used == "code" and result.language.lower() == "python":
        if "os.system" in result.output or "subprocess" in result.output:
            return False
            
    return True

def execute_python(code: str, timeout: int = 10) -> ExecutionResult:
    start_time = time.time()
    try:
        # Running via python -c
        proc = subprocess.Popen(
            ['python', '-c', code],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        try:
            out, err = proc.communicate(timeout=timeout)
            return ExecutionResult(
                stdout=out,
                stderr=err,
                exit_code=proc.returncode,
                execution_time_ms=(time.time() - start_time) * 1000,
                timed_out=False
            )
        except subprocess.TimeoutExpired:
            proc.kill()
            return ExecutionResult(
                stdout="",
                stderr="Execution timed out.",
                exit_code=-1,
                execution_time_ms=(time.time() - start_time) * 1000,
                timed_out=True
            )
    except Exception as e:
         return ExecutionResult(
             stdout="",
             stderr=str(e),
             exit_code=-1,
             execution_time_ms=(time.time() - start_time) * 1000,
             timed_out=False
         )

def execute_bash(command: str, timeout: int = 10) -> ExecutionResult:
    start_time = time.time()
    
    # Simple blocklist pre-check just in case
    cmd_lower = command.lower()
    if 'rm -rf /' in cmd_lower or 'mkfs' in cmd_lower:
        return ExecutionResult(
            stdout="",
            stderr="Command blocked by security sandbox.",
            exit_code=1,
            execution_time_ms=0,
            timed_out=False
        )

    try:
        proc = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        try:
            out, err = proc.communicate(timeout=timeout)
            return ExecutionResult(
                stdout=out,
                stderr=err,
                exit_code=proc.returncode,
                execution_time_ms=(time.time() - start_time) * 1000,
                timed_out=False
            )
        except subprocess.TimeoutExpired:
            proc.kill()
            return ExecutionResult(
                stdout="",
                stderr="Execution timed out.",
                exit_code=-1,
                execution_time_ms=(time.time() - start_time) * 1000,
                timed_out=True
            )
    except Exception as e:
         return ExecutionResult(
             stdout="",
             stderr=str(e),
             exit_code=-1,
             execution_time_ms=(time.time() - start_time) * 1000,
             timed_out=False
         )
