from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # 数据库配置
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "ai_reviewer"
    
    # 应用配置
    APP_NAME: str = "AI Reviewer"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # OpenAI配置
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    
    # 阿里云百炼配置
    DASHSCOPE_API_KEY: Optional[str] = None
    DASHSCOPE_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    DASHSCOPE_MODEL: str = "qwen-plus"
    
    # 默认使用的AI模型类型（openai或dashscope）
    AI_PROVIDER: str = "openai"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()