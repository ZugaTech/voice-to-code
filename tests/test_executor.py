import pytest
from src.executor import is_safe_to_autorun, execute_python, execute_bash
from src.converter import ConversionResult, ConversionMode

def test_executor_safeguards():
    res = ConversionResult(
        mode_used=ConversionMode.bash,
        output="rm -rf /",
        language="bash",
        explanation="Deletes root",
        warnings=[],
        is_destructive=True
    )
    assert is_safe_to_autorun(res) == False

def test_executor_safeguards_heuristic():
    res = ConversionResult(
        mode_used=ConversionMode.bash,
        output="chmod 777 secret.key", # Caught by warn list
        language="bash",
        explanation="Change permissions",
        warnings=[],
        is_destructive=False # AI missed it
    )
    assert is_safe_to_autorun(res) == False

def test_execute_python_basic():
    res = execute_python("print('hello')")
    assert res.exit_code == 0
    assert "hello" in res.stdout

def test_execute_python_timeout():
    res = execute_python("import time; time.sleep(10)", timeout=1)
    assert res.timed_out == True
    assert res.exit_code == -1
