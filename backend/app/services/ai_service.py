from typing import Optional
import os
import json
import re
from app.core.config import settings

def mask_sensitive_data(text: str, sensitive_keys: list = None) -> str:
    if not isinstance(text, str):
        return text
    
    if sensitive_keys is None:
        sensitive_keys = ['api_key', 'apikey', 'api-key', 'password', 'secret', 'token']
    
    masked_text = text
    for key in sensitive_keys:
        # 使用普通字符串格式而不是rf''来避免语法错误
        key_pattern = r'("?{key}"?\s*[:=]\s*["\']?)([^"\'\s\}]+)(["\']?)'.format(key=key)
        masked_text = re.sub(
            key_pattern,
            lambda m: m.group(1) + '*' * min(len(m.group(2)), 8) + m.group(3),
            masked_text,
            flags=re.IGNORECASE
        )
    
    api_key_patterns = [
        r'sk-[a-zA-Z0-9]{20,}',
        r'sk-proj-[a-zA-Z0-9]{20,}',
        r'[a-zA-Z0-9]{20,}',
    ]
    for pattern in api_key_patterns:
        masked_text = re.sub(pattern, lambda m: '*' * len(m.group(0)), masked_text)
    
    return masked_text

def safe_log(level: str, message: str, *args, **kwargs) -> None:
    import logging
    logger = logging.getLogger(__name__)
    
    safe_message = mask_sensitive_data(message)
    safe_args = tuple(mask_sensitive_data(str(arg)) for arg in args)
    
    safe_kwargs = {}
    for key, value in kwargs.items():
        safe_key = mask_sensitive_data(str(key))
        safe_value = mask_sensitive_data(str(value))
        safe_kwargs[safe_key] = safe_value
    
    log_method = getattr(logger, level.lower(), logger.info)
    log_method(safe_message, *safe_args, **safe_kwargs)

class AIService:
    def __init__(self):
        self.provider = settings.AI_PROVIDER
        self.api_key = None
        self.base_url = None
        self.model = None
        self.client = None
        
        self.load_config()
        
    def load_config(self):
        API_CONFIG_FILE = "./ai_api_config.json"
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
            safe_log("error", f"Error loading AI config: {e}")
            self.provider = settings.AI_PROVIDER
            self.api_key = settings.OPENAI_API_KEY or settings.DASHSCOPE_API_KEY or ""
            self.base_url = settings.DASHSCOPE_BASE_URL or ""
            self.model = settings.OPENAI_MODEL or settings.DASHSCOPE_MODEL or ""
    
    async def generate_audit_result(self, content: str, criteria: str, item_type: str) -> dict:
        if not self.client:
            return {
                "result": "pass",
                "reason": "模拟审核：内容符合审核标准",
                "confidence": 0.8
            }
            
        try:
            prompt = f"""
            作为一名智能审核专家，请根据以下审核标准对提供的内容进行审核：
            
            审核标准：{criteria}
            内容类型：{item_type}
            待审核内容：{content}
            
            请输出以下格式的JSON结果：
            {
                "result": "pass/fail/warning",
                "reason": "详细的审核理由",
                "confidence": 0.0-1.0
            }
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一名专业的智能审核专家，能够根据给定的标准对各种内容进行准确审核。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result = response.choices[0].message.content
            import json
            return json.loads(result)
        except Exception as e:
            print(f"Error generating audit result: {e}")
            # 返回默认结果
            return {
                "result": "warning",
                "reason": "AI审核失败，建议人工复核",
                "confidence": 0.5
            }
    
    async def optimize_rule(self, rule: dict, audit_items: list) -> dict:
        """
        优化规则
        :param rule: 原始规则
        :param audit_items: 审核项列表
        :return: 优化建议
        """
        # 如果客户端未初始化（API密钥未设置），返回模拟结果
        if not self.client:
            return {
                "optimized_rule_name": rule['name'],
                "optimized_description": rule.get('description', '') + "（模拟优化）",
                "audit_items_suggestions": [
                    {
                        "original_item": item['name'],
                        "suggestion": f"模拟优化建议：完善{item['name']}的审核标准"
                    } for item in audit_items[:2]
                ],
                "general_suggestions": ["模拟优化：建议增加更多审核场景示例", "模拟优化：建议调整审核标准的阈值"]
            }
            
        try:
            # 构建审核项描述
            items_desc = "\n".join([f"- {item['name']}（类型：{item['type']}）：{item['criteria']}" for item in audit_items])
            
            prompt = f"""
            作为一名智能审核规则专家，请根据以下原始规则和审核项，生成优化建议：
            
            原始规则：
            名称：{rule['name']}
            描述：{rule.get('description', '无')}
            
            审核项：
            {items_desc}
            
            请从以下几个方面给出优化建议：
            1. 规则的完整性和准确性
            2. 审核项的描述清晰度
            3. 审核标准的可操作性
            4. 可能的漏洞和改进点
            
            输出格式：
            {
                "optimized_rule_name": "优化后的规则名称",
                "optimized_description": "优化后的规则描述",
                "audit_items_suggestions": [
                    {
                        "original_item": "原始审核项名称",
                        "suggestion": "具体优化建议"
                    }
                ],
                "general_suggestions": ["总体优化建议1", "总体优化建议2"]
            }
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一名专业的智能审核规则专家，能够根据给定的规则和审核项，提供准确的优化建议。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result = response.choices[0].message.content
            import json
            return json.loads(result)
        except Exception as e:
            print(f"Error optimizing rule: {e}")
            # 返回默认建议
            return {
                "optimized_rule_name": rule['name'],
                "optimized_description": rule.get('description', ''),
                "audit_items_suggestions": [],
                "general_suggestions": ["AI优化失败，建议人工优化"]
            }
    
    async def validate_rule(self, rule: dict, example_content: dict, audit_items: list) -> dict:
        """
        规则校验
        :param rule: 规则信息
        :param example_content: 示例内容
        :param audit_items: 审核项列表
        :return: 校验结果
        """
        # 如果客户端未初始化（API密钥未设置），返回模拟结果
        if not self.client:
            return {
                "validation_results": [
                    {
                        "audit_item_name": item['name'],
                        "result": "pass",
                        "reason": f"模拟校验：{item['name']}符合审核标准",
                        "suggestion": "模拟建议：无需修改"
                    } for item in audit_items
                ]
            }
            
        try:
            # 构建审核项描述
            items_desc = "\n".join([f"- {item['name']}（类型：{item['type']}）：{item['criteria']}" for item in audit_items])
            
            prompt = f"""
            作为一名智能审核规则校验专家，请根据以下规则和审核项，对提供的示例内容进行校验：
            
            规则：
            名称：{rule['name']}
            描述：{rule.get('description', '无')}
            
            审核项：
            {items_desc}
            
            示例内容：
            {example_content}
            
            请为每个审核项输出校验结果，格式如下：
            {
                "validation_results": [
                    {
                        "audit_item_name": "审核项名称",
                        "result": "pass/fail/warning",
                        "reason": "详细的校验理由",
                        "suggestion": "改进建议（如果有）"
                    }
                ]
            }
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一名专业的智能审核规则校验专家，能够根据给定的规则和审核项，对示例内容进行准确校验。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result = response.choices[0].message.content
            import json
            return json.loads(result)
        except Exception as e:
            print(f"Error validating rule: {e}")
            # 返回默认校验结果
            return {
                "validation_results": [
                    {
                        "audit_item_name": item['name'],
                        "result": "warning",
                        "reason": "AI校验失败，建议人工复核",
                        "suggestion": ""}
                    for item in audit_items
                ]
            }
    
    async def chat(self, message: str) -> str:
        """
        处理对话请求
        :param message: 用户输入的消息
        :return: AI响应
        """
        # 如果客户端未初始化（API密钥未设置），返回模拟响应
        if not self.client:
            return "模拟响应：这是一个模拟的AI响应。您的输入是：" + message
            
        try:
            prompt = f"""
            作为一名智能审核专家，请回答以下问题：
            {message}
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一名专业的智能审核专家，能够回答关于审核规则、提示词优化等方面的问题。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5
            )
            
            result = response.choices[0].message.content
            return result
        except Exception as e:
            print(f"Error in chat: {e}")
            # 返回错误响应
            return "抱歉，处理您的请求时发生错误，请稍后重试。"
    
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
            safe_log("error", f"Error loading prompt {prompt_name}: {e}")
            # 返回默认提示词
            return "请根据要求优化执行逻辑。"
    
    async def optimize_prompt(self, original_prompt: str) -> str:
        """
        优化规则描述为更清晰、更准确的AI提示词
        :param original_prompt: 原始规则描述
        :return: 优化后的AI提示词
        """
        # 如果客户端未初始化（API密钥未设置），返回模拟优化结果
        if not self.client:
            return f"{original_prompt}（模拟优化：建议增加更详细的审核标准和示例）"
            
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