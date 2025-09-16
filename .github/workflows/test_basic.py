# tests/test_basic.py

import os
from pathlib import Path

def test_project_structure():
    """Ensure essential folders exist"""
    for folder in ["src", "data", "outputs"]:
        assert Path(folder).exists(), f"Missing folder: {folder}"

def test_sample_pdf_exists():
    """Check that the sample PDF is present in data/sample/"""
    sample = Path("data/sample/sample.pdf")
    assert sample.exists(), "Sample PDF missing (expected at data/sample/sample.pdf)"

def test_env_vars_are_safe():
    """Ensure API key is not hardcoded in the repo"""
    env_file = Path(".env")
    if env_file.exists():
        text = env_file.read_text()
        assert "sk-" not in text, "API key should not be committed to .env"
