from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from bson import ObjectId

# Pydantic v2 doesn't support ObjectId directly, so we use string representation
# and validate it manually

# 基础模型
class BaseDBModel(BaseModel):
    id: Optional[str] = Field(alias="_id", default=None)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True

# 1. 业务场景模型
class BusinessSceneBase(BaseModel):
    name: str
    description: Optional[str] = None

class BusinessSceneCreate(BusinessSceneBase):
    pass

class BusinessSceneUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class BusinessScene(BusinessSceneBase, BaseDBModel):
    class Config(BaseDBModel.Config):
        pass

# 2. 规则模型
class RuleBase(BaseModel):
    name: str
    scene_id: str
    description: Optional[str] = None
    reference_materials: Optional[List[str]] = Field(default_factory=list, description="参考材料文件路径列表")

class RuleCreate(RuleBase):
    pass

class RuleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    reference_materials: Optional[List[str]] = None

class Rule(RuleBase, BaseDBModel):
    class Config(BaseDBModel.Config):
        pass

# 6. 规则校验请求模型
class ValidateRequest(BaseModel):
    rule_id: str
    files: List[dict]
    reference_files: Optional[List[dict]] = Field(default_factory=list)

# 3. 审核项模型
class AuditItemBase(BaseModel):
    name: str
    rule_id: str
    type: str  # text, image, video, etc.
    criteria: str

class AuditItemCreate(AuditItemBase):
    pass

class AuditItemUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    criteria: Optional[str] = None

class AuditItem(AuditItemBase, BaseDBModel):
    class Config(BaseDBModel.Config):
        pass

# 4. 审核任务模型
class AuditTaskBase(BaseModel):
    name: str
    scene_id: str
    use_knowledge_base: bool = False

class AuditTaskCreate(AuditTaskBase):
    pass

class AuditTaskUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None  # pending, running, completed, failed

class AuditTask(AuditTaskBase, BaseDBModel):
    status: str = "pending"
    completed_at: Optional[datetime] = None
    
    class Config(BaseDBModel.Config):
        pass

# 5. 审核结果模型
class AuditResultBase(BaseModel):
    task_id: str
    audit_item_id: str
    rule_id: str
    content: str
    result: str  # pass, fail, warning
    reason: str
    ai_generated: bool = True
    edited_by: Optional[str] = None

class AuditResultCreate(AuditResultBase):
    pass

class AuditResultUpdate(BaseModel):
    result: Optional[str] = None
    reason: Optional[str] = None
    edited_by: Optional[str] = None

class AuditResult(AuditResultBase, BaseDBModel):
    class Config(BaseDBModel.Config):
        pass

# 6. 版式库模型
class TemplateVariable(BaseModel):
    name: str
    type: str
    format: Optional[str] = None

class TemplateBase(BaseModel):
    name: str
    variables: List[TemplateVariable]

class TemplateCreate(TemplateBase):
    pass

class TemplateUpdate(BaseModel):
    name: Optional[str] = None
    variables: Optional[List[TemplateVariable]] = None

class Template(TemplateBase, BaseDBModel):
    class Config(BaseDBModel.Config):
        pass

# 7. 提示词优化模型
class PromptOptimizeRequest(BaseModel):
    description: str = Field(..., description="需要优化的原始规则描述")
    
class PromptOptimizeResponse(BaseModel):
    original_description: str
    optimized_prompt: str

# 8. 执行逻辑保存请求模型
class ExecutionLogicSaveRequest(BaseModel):
    rule_id: str
    description: str