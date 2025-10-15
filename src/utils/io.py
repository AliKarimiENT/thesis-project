"""
I/O utilities - compatibility wrapper.
For main implementation, see io_utils.py
"""

# Import all functions from io_utils for compatibility
from src.utils.io_utils import (
    save_json,
    load_json,
    save_jsonl,
    load_jsonl,
    load_yaml,
    save_yaml,
    ensure_dir,
    list_files
)

__all__ = [
    'save_json',
    'load_json',
    'save_jsonl',
    'load_jsonl',
    'load_yaml',
    'save_yaml',
    'ensure_dir',
    'list_files'
]

