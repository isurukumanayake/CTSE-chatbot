import time
from functools import wraps
from typing import Callable, Any
import streamlit as st

def timer(func: Callable) -> Callable:
    """Decorator to time function execution"""
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        logger = get_logger("timer")
        logger.debug(f"{func.__name__} executed in {end_time - start_time:.2f}s")
        
        return result
    return wrapper

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"

def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to specified length"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def safe_filename(filename: str) -> str:
    """Create safe filename by removing invalid characters"""
    import re
    return re.sub(r'[<>:"/\\|?*]', '_', filename)