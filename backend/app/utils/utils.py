"""工具函数"""

import os
import json
from typing import Dict, Any
from datetime import datetime


def ensure_directory(path: str) -> None:
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)


def generate_output_filename(base_name: str = "presentation") -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{base_name}_{timestamp}.pptx"


def load_json_file(path: str) -> Dict[str, Any]:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json_file(data: Dict[str, Any], path: str) -> None:
    ensure_directory(path)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


__all__ = ['ensure_directory', 'generate_output_filename', 'load_json_file', 'save_json_file']