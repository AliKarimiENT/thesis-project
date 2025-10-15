"""
I/O utilities for reading and writing various file formats.
"""

import os
import json
import yaml
from typing import List, Dict, Any, Optional


def save_json(obj: Any, path: str):
    """
    Save object to JSON file.
    
    Args:
        obj: Object to save
        path: Output file path
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)


def load_json(path: str) -> Any:
    """
    Load object from JSON file.
    
    Args:
        path: Input file path
        
    Returns:
        Loaded object
    """
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_jsonl(data: List[Dict], path: str):
    """
    Save list of dictionaries to JSONL file (one JSON object per line).
    
    Args:
        data: List of dictionaries
        path: Output file path
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")


def load_jsonl(path: str) -> List[Dict]:
    """
    Load JSONL file into list of dictionaries.
    
    Args:
        path: Input file path
        
    Returns:
        List of dictionaries
    """
    data = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                data.append(json.loads(line))
    return data


def load_yaml(path: str) -> Dict[str, Any]:
    """
    Load YAML configuration file.
    
    Args:
        path: Input file path
        
    Returns:
        Configuration dictionary
    """
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def save_yaml(obj: Dict[str, Any], path: str):
    """
    Save dictionary to YAML file.
    
    Args:
        obj: Dictionary to save
        path: Output file path
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(obj, f, default_flow_style=False, sort_keys=False)


def ensure_dir(path: str):
    """
    Ensure directory exists, creating it if necessary.
    
    Args:
        path: Directory path
    """
    os.makedirs(path, exist_ok=True)


def list_files(directory: str, extension: Optional[str] = None) -> List[str]:
    """
    List all files in directory, optionally filtered by extension.
    
    Args:
        directory: Directory path
        extension: File extension filter (e.g., '.jsonl')
        
    Returns:
        List of file paths
    """
    if not os.path.exists(directory):
        return []
    
    files = []
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath):
            if extension is None or filename.endswith(extension):
                files.append(filepath)
    return sorted(files)
