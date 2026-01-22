import re
from typing import Optional

SENSITIVE_PATTERNS = [
    (r'sk-[a-zA-Z0-9]{20,}', lambda m: '*' * len(m.group(0))),
    (r'sk-proj-[a-zA-Z0-9]{20,}', lambda m: '*' * len(m.group(0))),
    (r'api[_-]?key["\']?\s*[:=]\s*["\']?[a-zA-Z0-9_-]{20,}["\']?', lambda m: '***'),
    (r'DASHSCOPE_API_KEY["\']?\s*[:=]\s*["\']?[a-zA-Z0-9_-]{20,}["\']?', lambda m: '***'),
    (r'OPENAI_API_KEY["\']?\s*[:=]\s*["\']?[a-zA-Z0-9_-]{20,}["\']?', lambda m: '***'),
]

def sanitize_log_message(message: str) -> str:
    """
    屏蔽敏感信息，如API Key、密码等
    :param message: 原始消息
    :return: 屏蔽敏感信息后的消息
    """
    if not isinstance(message, str):
        return str(message)
    
    sanitized = message
    for pattern, replacement in SENSITIVE_PATTERNS:
        sanitized = re.sub(pattern, replacement, sanitized)
    
    return sanitized
