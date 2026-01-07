from fastapi import APIRouter, HTTPException, status
from typing import Dict
import os
import json
from app.core.config import settings
from app.services.ai_service import ai_service

router = APIRouter()

# API配置存储路径
API_CONFIG_FILE = "./ai_api_config.json"

# 获取AI配置
@router.get("/api/config/ai")
async def get_ai_config():
    """获取当前AI配置"""
    try:
        # 先尝试从文件读取配置
        if os.path.exists(API_CONFIG_FILE):
            with open(API_CONFIG_FILE, "r") as f:
                config = json.load(f)
            return config
        else:
            # 如果文件不存在，返回默认配置
            return {
                "provider": settings.AI_PROVIDER,
                "api_key": settings.OPENAI_API_KEY or settings.DASHSCOPE_API_KEY or "",
                "base_url": settings.DASHSCOPE_BASE_URL or "",
                "model": settings.OPENAI_MODEL or settings.DASHSCOPE_MODEL or ""
            }
    except Exception as e:
        print(f"Error getting AI config: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取AI配置失败"
        )

# 保存AI配置
@router.post("/api/config/ai")
async def save_ai_config(config: Dict):
    """保存AI配置"""
    try:
        # 保存到文件
        with open(API_CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)
        
        # 这里可以添加更多逻辑，比如重启AI服务等
        
        return {"message": "AI配置保存成功"}
    except Exception as e:
        print(f"Error saving AI config: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="保存AI配置失败"
        )

# AI对话API
@router.post("/api/config/ai/chat")
async def ai_chat(request: Dict):
    """AI对话接口，用于调试提示词"""
    try:
        message = request.get("message", "")
        if not message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message is required"
            )
        
        # 调用AI服务获取响应
        response = await ai_service.chat(message)
        
        return {"response": response}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in ai_chat: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )
