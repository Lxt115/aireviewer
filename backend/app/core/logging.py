import logging
import sys
from typing import Optional
import re

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("ai_reviewer")

SENSITIVE_PATTERNS = [
    (r'sk-[a-zA-Z0-9]{20,}', lambda m: '*' * len(m.group(0))),
    (r'sk-proj-[a-zA-Z0-9]{20,}', lambda m: '*' * len(m.group(0))),
    (r'api[_-]?key["\']?\s*[:=]\s*["\']?[a-zA-Z0-9_-]{20,}["\']?', lambda m: '***'),
    (r'DASHSCOPE_API_KEY["\']?\s*[:=]\s*["\']?[a-zA-Z0-9_-]{20,}["\']?', lambda m: '***'),
    (r'OPENAI_API_KEY["\']?\s*[:=]\s*["\']?[a-zA-Z0-9_-]{20,}["\']?', lambda m: '***'),
]

def sanitize_log_message(message: str) -> str:
    if not isinstance(message, str):
        return str(message)
    
    sanitized = message
    for pattern, replacement in SENSITIVE_PATTERNS:
        sanitized = re.sub(pattern, replacement, sanitized)
    
    return sanitized

def log_error(operation: str, error: Exception) -> None:
    sanitized_error = sanitize_log_message(str(error))
    logger.error(f"Error in {operation}: {sanitized_error}")

def log_info(message: str) -> None:
    sanitized_message = sanitize_log_message(message)
    logger.info(sanitized_message)

def log_warning(message: str) -> None:
    sanitized_message = sanitize_log_message(message)
    logger.warning(sanitized_message)

def log_debug(message: str) -> None:
    sanitized_message = sanitize_log_message(message)
    logger.debug(sanitized_message)
