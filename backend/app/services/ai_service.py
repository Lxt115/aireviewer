from typing import Optional
import os
import json
import re
import logging
from app.core.config import settings
from app.core.logging import sanitize_log_message

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.provider = settings.AI_PROVIDER
        self.api_key = None
        self.base_url = None
        self.model = None
        self.client = None
        
        self.load_config()
        
    def load_config(self):
        import os
        # 使用绝对路径，确保在任何工作目录下都能找到配置文件
        API_CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../ai_api_config.json")
        try:
            if os.path.exists(API_CONFIG_FILE):
                with open(API_CONFIG_FILE, "r") as f:
                    config = json.load(f)
                self.provider = config.get("provider", settings.AI_PROVIDER)
                self.api_key = config.get("api_key", "")
                self.base_url = config.get("base_url", "")
                self.model = config.get("model", "")
            else:
                self.provider = settings.AI_PROVIDER
                self.api_key = settings.OPENAI_API_KEY or settings.DASHSCOPE_API_KEY or ""
                self.base_url = settings.DASHSCOPE_BASE_URL or ""
                self.model = settings.OPENAI_MODEL or settings.DASHSCOPE_MODEL or ""
        except Exception as e:
            logger.error(f"Error loading AI config: {sanitize_log_message(str(e))}")
            self.provider = settings.AI_PROVIDER
            self.api_key = settings.OPENAI_API_KEY or settings.DASHSCOPE_API_KEY or ""
            self.base_url = settings.DASHSCOPE_BASE_URL or ""
            self.model = settings.OPENAI_MODEL or settings.DASHSCOPE_MODEL or ""
    
    async def _call_ai(self, prompt_name: str, system_role: str, prompt_params: dict, error_message: str, default_result: dict) -> dict:
        """
        核心AI调用函数，封装共同的AI调用逻辑
        :param prompt_name: 提示词名称
        :param system_role: 系统角色
        :param prompt_params: 提示词格式化参数
        :param error_message: 错误消息前缀
        :param default_result: 默认结果
        :return: AI响应结果
        """
        if not self.client:
            raise Exception("请配置AI API密钥以使用AI功能")
            
        try:
            # 加载提示词
            prompt_template = self.load_prompt(prompt_name)
            
            # 格式化提示词
            prompt = prompt_template.format(**prompt_params)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_role},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result = response.choices[0].message.content
            import json
            return json.loads(result)
        except Exception as e:
            print(f"{error_message}: {e}")
            return default_result
    
    async def generate_audit_result(self, content: str, criteria: str, item_type: str) -> dict:
        """
        生成审核结果
        :param content: 待审核内容
        :param criteria: 审核标准
        :param item_type: 审核项类型
        :return: 审核结果
        """
        return await self._call_ai(
            prompt_name='audit_result',
            system_role="你是一名专业的智能审核专家，能够根据给定的标准对各种内容进行准确审核。",
            prompt_params={
                'criteria': criteria,
                'item_type': item_type,
                'content': content
            },
            error_message="Error generating audit result",
            default_result={
                "result": "warning",
                "reason": "AI审核失败，建议人工复核",
                "confidence": 0.5
            }
        )
    
    async def validate_rule(self, rule: dict, example_content: dict, audit_items: list) -> dict:
        """
        规则校验
        :param rule: 规则信息
        :param example_content: 示例内容
        :param audit_items: 审核项列表
        :return: 校验结果
        """
        # 构建审核项描述
        items_desc = "\n".join([f"- {item['name']}（类型：{item['type']}）：{item['criteria']}" for item in audit_items])
        
        return await self._call_ai(
            prompt_name='rule_validation',
            system_role="你是一名专业的智能审核规则校验专家，能够根据给定的规则和审核项，对示例内容进行准确校验。",
            prompt_params={
                'rule_name': rule['name'],
                'rule_description': rule.get('description', '无'),
                'audit_items': items_desc,
                'example_content': example_content
            },
            error_message="Error validating rule",
            default_result={
                "validation_results": [
                    {
                        "audit_item_name": item['name'],
                        "result": "warning",
                        "reason": "AI校验失败，建议人工复核",
                        "suggestion": ""}
                    for item in audit_items
                ]
            }
        )
    
    def load_prompt(self, prompt_name: str) -> str:
        """
        从文件加载提示词
        :param prompt_name: 提示词名称
        :return: 提示词内容
        """
        prompt_path = os.path.join(os.path.dirname(__file__), '../prompts', f'{prompt_name}.txt')
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except Exception as e:
            logger.error(f"Error loading prompt {prompt_name}: {sanitize_log_message(str(e))}")
            # 返回默认提示词
            return "请根据要求优化执行逻辑。"
    
    async def optimize_prompt(self, original_prompt: str) -> str:
        """
        优化规则描述为更清晰、更准确的AI提示词
        :param original_prompt: 原始规则描述
        :return: 优化后的AI提示词
        """
        if not self.client:
            raise Exception("请配置AI API密钥以使用优化功能")
            
        try:
            # 加载执行逻辑优化提示词
            execution_optimization_prompt = self.load_prompt('execution_optimization')
            
            prompt = f"""
            {execution_optimization_prompt}
            
            原始执行逻辑：{original_prompt}
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一名专业的逻辑优化助手，擅长将模糊的执行目标转化为清晰、可操作、可分步骤执行的优化逻辑。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            result = response.choices[0].message.content
            return result
        except Exception as e:
            print(f"Error in optimize_prompt: {e}")
            # 返回原始提示词作为降级方案
            return original_prompt
    
    def init_client(self):
        """初始化大模型客户端"""
        try:
            if self.provider == "openai" and self.api_key:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key, base_url=self.base_url if self.base_url else None)
            elif self.provider == "dashscope" and self.api_key:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
            else:
                print(f"AI client not initialized. Provider: {self.provider}, API Key: {'Set' if self.api_key else 'Not Set'}")
        except Exception as e:
            print(f"Error initializing AI client: {e}")
            self.client = None

# 创建AI服务实例
ai_service = AIService()
ai_service.init_client()