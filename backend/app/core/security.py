import re
import html
from typing import Any, Optional

class InputValidator:
    SQL_INJECTION_PATTERN = re.compile(
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|ALTER|CREATE|TRUNCATE)\b)|"
        r"(')|(--)|(\/\*)|(\*\/)|(;)|(\|)|(&&)|(\bOR\b.*=.*\bOR\b)"
    , re.IGNORECASE)
    
    XSS_PATTERN = re.compile(
        r"<script.*?>|<\/script>|<iframe.*?>|<\/iframe>|<object.*?>|<\/object>|", re.IGNORECASE | re.DOTALL)

    @staticmethod
    def sanitize_string(value: str, max_length: Optional[int] = None) -> str:
        """
        清理字符串，防止XSS攻击
        :param value: 原始字符串
        :param max_length: 最大长度
        :return: 清理后的字符串
        """
        if not isinstance(value, str):
            value = str(value)
        
        value = html.escape(value)
        
        value = value.strip()
        
        if max_length and len(value) > max_length:
            value = value[:max_length]
        
        return value

    @staticmethod
    def check_sql_injection(value: str) -> bool:
        """
        检查字符串是否包含SQL注入攻击
        :param value: 原始字符串
        :return: 是否包含SQL注入攻击
        """
        if not isinstance(value, str):
            return False
        return bool(InputValidator.SQL_INJECTION_PATTERN.search(value))

    @staticmethod
    def check_xss(value: str) -> bool:
        """
        检查字符串是否包含XSS攻击
        :param value: 原始字符串
        :return: 是否包含XSS攻击
        """
        if not isinstance(value, str):
            return False
        return bool(InputValidator.XSS_PATTERN.search(value))

    @staticmethod
    def validate_name(value: str, field_name: str = "name", max_length: int = 100) -> str:
        """
        验证名称
        :param value: 原始名称
        :param field_name: 字段名称
        :param max_length: 最大长度
        :return: 验证后的名称
        """
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
        """
        验证描述
        :param value: 原始描述
        :param max_length: 最大长度
        :return: 验证后的描述
        """
        if value is None:
            return None
        
        if InputValidator.check_sql_injection(value):
            raise ValueError("Invalid description: potential SQL injection detected")
        
        if InputValidator.check_xss(value):
            raise ValueError("Invalid description: potential XSS detected")
        
        return InputValidator.sanitize_string(value, max_length)

input_validator = InputValidator()
