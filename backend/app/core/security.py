import re
import html
from typing import Any, Optional

class InputValidator:
    SQL_INJECTION_PATTERN = re.compile(
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|ALTER|CREATE|TRUNCATE)\b)|"
        r"(')|(--)|(\/\*)|(\*\/)|(;)|(\|)|(&&)|(\bOR\b.*=.*\bOR\b)"
    , re.IGNORECASE)
    
    XSS_PATTERN = re.compile(
        r"<script.*?>|</script>|<iframe.*?>|</iframe>|<object.*?>|</object>|"
        r"<embed.*?>|on\w+\s*=|javascript:|data:text/html"
    , re.IGNORECASE | re.DOTALL)
    
    PATH_TRAVERSAL_PATTERN = re.compile(r"(\.\./)|(\.\.\\)|(%2e%2e)|(\0)")

    @staticmethod
    def sanitize_string(value: str, max_length: Optional[int] = None) -> str:
        if not isinstance(value, str):
            value = str(value)
        
        value = html.escape(value)
        
        value = value.strip()
        
        if max_length and len(value) > max_length:
            value = value[:max_length]
        
        return value

    @staticmethod
    def check_sql_injection(value: str) -> bool:
        if not isinstance(value, str):
            return False
        return bool(InputValidator.SQL_INJECTION_PATTERN.search(value))

    @staticmethod
    def check_xss(value: str) -> bool:
        if not isinstance(value, str):
            return False
        return bool(InputValidator.XSS_PATTERN.search(value))

    @staticmethod
    def check_path_traversal(value: str) -> bool:
        if not isinstance(value, str):
            return False
        return bool(InputValidator.PATH_TRAVERSAL_PATTERN.search(value))

    @staticmethod
    def sanitize_id(value: str) -> str:
        if InputValidator.check_sql_injection(value):
            raise ValueError("Invalid ID: potential SQL injection detected")
        if InputValidator.check_path_traversal(value):
            raise ValueError("Invalid ID: potential path traversal detected")
        return InputValidator.sanitize_string(value, max_length=64)

    @staticmethod
    def validate_name(value: str, field_name: str = "name", max_length: int = 100) -> str:
        if not value or not value.strip():
            raise ValueError(f"{field_name}不能为空")
        
        if InputValidator.check_sql_injection(value):
            raise ValueError(f"Invalid {field_name}: potential SQL injection detected")
        
        if InputValidator.check_xss(value):
            raise ValueError(f"Invalid {field_name}: potential XSS detected")
        
        sanitized = InputValidator.sanitize_string(value, max_length)
        
        if not sanitized:
            raise ValueError(f"{field_name}不能为空")
        
        return sanitized

    @staticmethod
    def validate_description(value: Optional[str], max_length: int = 1000) -> Optional[str]:
        if value is None:
            return None
        
        if InputValidator.check_sql_injection(value):
            raise ValueError("Invalid description: potential SQL injection detected")
        
        if InputValidator.check_xss(value):
            raise ValueError("Invalid description: potential XSS detected")
        
        return InputValidator.sanitize_string(value, max_length)

input_validator = InputValidator()
