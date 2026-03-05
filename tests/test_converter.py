import pytest
from src.converter import converter, ConversionRequest, ConversionMode

def test_determine_mode():
    req = ConversionRequest(text="List all files in directory", mode=ConversionMode.bash)
    assert converter._determine_mode(req) == ConversionMode.bash
    
    req_auto = ConversionRequest(text="write a python script to parse logs")
    assert converter._determine_mode(req_auto) == ConversionMode.auto

# Due to OpenAI requirements we don't mock the full process in unit tests without API keys.
# We test just the class constraints.
def test_request_structure():
    req = ConversionRequest(text="remove config file", language_hint="bash")
    assert "remove config file" in req.text
    assert req.mode == ConversionMode.auto
