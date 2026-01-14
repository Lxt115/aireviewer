from fastapi import APIRouter, HTTPException, status
from typing import List
from app.models import (
    Rule,
    RuleCreate,
    RuleUpdate,
    ValidateRequest,
    PromptOptimizeRequest,
    PromptOptimizeResponse,
    ExecutionLogicSaveRequest
)
from app.services.ai_service import ai_service
from app.db.sqlite import query, insert, update, delete
from datetime import datetime
from uuid import uuid4

router = APIRouter()

@router.post("/", response_model=Rule, status_code=status.HTTP_201_CREATED)
async def create_rule(rule: RuleCreate):
    """创建新的规则"""
    try:
        rule_dict = rule.model_dump()
        rule_id = str(uuid4())
        rule_dict["_id"] = rule_id
        rule_dict["created_at"] = datetime.utcnow().isoformat()
        rule_dict["updated_at"] = datetime.utcnow().isoformat()
        
        # 移除数据库表中不存在的字段
        if "reference_materials" in rule_dict:
            del rule_dict["reference_materials"]
        
        # 保存到SQLite数据库
        await insert("rules", rule_dict)
        
        return Rule(**rule_dict)
    except Exception as e:
        import traceback
        print(f"Error in create_rule: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/", response_model=List[Rule])
async def get_rules():
    """获取所有规则"""
    try:
        # 从SQLite数据库查询所有规则
        results = await query("SELECT * FROM rules")
        
        # 转换为Rule对象
        rules = []
        for result in results:
            rule_dict = {
                "_id": result[0],
                "name": result[1],
                "scene_id": result[2],
                "description": result[3],
                "reference_materials": [],  # 暂时返回空列表，后续可以从文件系统或数据库中获取
                "created_at": result[4],
                "updated_at": result[5]
            }
            rules.append(Rule(**rule_dict))
        
        return rules
    except Exception as e:
        import traceback
        print(f"Error in get_rules: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/validate")
async def validate_rule(request: ValidateRequest):
    """使用规则进行校验"""
    try:
        # 这里可以添加实际的校验逻辑，包括使用AI服务
        # 目前返回模拟结果
        results = []
        
        for file in request.files:
            results.append({
                "uid": file["uid"],
                "fileName": file["name"],
                "ruleName": f"规则_{request.rule_id}",
                "result": "通过",
                "reason": "符合规则要求",
                "aiGenerated": True,
                "reference_files": [ref_file["name"] for ref_file in request.reference_files]
            })
        
        return {
            "message": "规则校验完成",
            "results": results
        }
    except Exception as e:
        import traceback
        print(f"Error in validate_rule: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/scene/{scene_id}", response_model=List[Rule])
async def get_rules_by_scene(scene_id: str):
    """根据业务场景获取规则"""
    try:
        # 从SQLite数据库查询指定场景的规则
        results = await query("SELECT * FROM rules WHERE scene_id = ?", (scene_id,))
        
        # 转换为Rule对象
        rules = []
        for result in results:
            rule_dict = {
                "_id": result[0],
                "name": result[1],
                "scene_id": result[2],
                "description": result[3],
                "reference_materials": [],  # 暂时返回空列表，后续可以从文件系统或数据库中获取
                "created_at": result[4],
                "updated_at": result[5]
            }
            rules.append(Rule(**rule_dict))
        
        return rules
    except Exception as e:
        import traceback
        print(f"Error in get_rules_by_scene: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/{rule_id}", response_model=Rule)
async def get_rule(rule_id: str):
    """获取单个规则"""
    try:
        # 从SQLite数据库查询单个规则
        results = await query("SELECT * FROM rules WHERE _id = ?", (rule_id,))
        
        if not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rule not found"
            )
        
        # 转换为Rule对象
        result = results[0]
        rule_dict = {
            "_id": result[0],
            "name": result[1],
            "scene_id": result[2],
            "description": result[3],
            "reference_materials": [],  # 暂时返回空列表，后续可以从文件系统或数据库中获取
            "created_at": result[4],
            "updated_at": result[5]
        }
        
        return Rule(**rule_dict)
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Error in get_rule: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.put("/{rule_id}", response_model=Rule)
async def update_rule(rule_id: str, rule_update: RuleUpdate):
    """更新规则"""
    try:
        # 检查规则是否存在
        results = await query("SELECT * FROM rules WHERE _id = ?", (rule_id,))
        if not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rule not found"
            )
        
        # 更新数据
        update_data = rule_update.model_dump(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow().isoformat()
        
        # 移除数据库表中不存在的字段
        if "reference_materials" in update_data:
            del update_data["reference_materials"]
        
        # 更新SQLite数据库
        await update(
            "rules",
            update_data,
            "_id = ?",
            (rule_id,)
        )
        
        # 查询更新后的规则
        updated_results = await query("SELECT * FROM rules WHERE _id = ?", (rule_id,))
        if not updated_results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rule not found after update"
            )
        
        # 转换为Rule对象
        result = updated_results[0]
        rule_dict = {
            "_id": result[0],
            "name": result[1],
            "scene_id": result[2],
            "description": result[3],
            "created_at": result[4],
            "updated_at": result[5]
        }
        
        return Rule(**rule_dict)
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Error in update_rule: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rule(rule_id: str):
    """删除规则，同时删除该规则下的所有审核项"""
    try:
        # 检查规则是否存在
        results = await query("SELECT * FROM rules WHERE _id = ?", (rule_id,))
        if not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rule not found"
            )
        
        # 先删除该规则下的所有审核项
        await delete("audit_items", "rule_id = ?", (rule_id,))
        
        # 然后删除规则本身
        await delete("rules", "_id = ?", (rule_id,))
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Error in delete_rule: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/optimize", response_model=PromptOptimizeResponse)
async def optimize_rule_description(request: PromptOptimizeRequest):
    """AI优化规则描述"""
    try:
        if not request.description:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Description is required"
            )
        
        # 调用AI服务优化规则描述
        optimized_prompt = await ai_service.optimize_prompt(request.description)
        
        return PromptOptimizeResponse(
            original_description=request.description,
            optimized_prompt=optimized_prompt
        )
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Error in optimize_rule_description: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/save-execution-logic")
async def save_execution_logic(request: ExecutionLogicSaveRequest):
    """保存执行逻辑"""
    try:
        if not request.rule_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Rule ID is required"
            )
        
        if not request.description:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Description is required"
            )
        
        # 检查规则是否存在
        results = await query("SELECT * FROM rules WHERE _id = ?", (request.rule_id,))
        if not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rule not found"
            )
        
        # 更新规则描述
        await update(
            "rules",
            {"description": request.description, "updated_at": datetime.utcnow().isoformat()},
            "_id = ?",
            (request.rule_id,)
        )
        
        return {
            "message": "Execution logic saved successfully",
            "rule_id": request.rule_id,
            "saved_description": request.description
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Error in save_execution_logic: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )



@router.post("/{rule_id}/validate")
async def validate_rule(rule_id: str, example_content: dict):
    """规则校验"""
    try:
        # 从数据库获取规则
        results = await query("SELECT * FROM rules WHERE _id = ?", (rule_id,))
        if not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rule not found"
            )
        
        result = results[0]
        rule = {
            "_id": result[0],
            "name": result[1],
            "scene_id": result[2],
            "description": result[3],
            "created_at": result[4],
            "updated_at": result[5]
        }
        
        # 获取关联的审核项
        audit_items_results = await query("SELECT * FROM audit_items WHERE rule_id = ?", (rule_id,))
        audit_items = [{"_id": item[0], "name": item[1], "rule_id": item[2], "type": item[3], "criteria": item[4], "created_at": item[5], "updated_at": item[6]} for item in audit_items_results]
        
        # 调用AI服务进行规则校验
        validation_results = await ai_service.validate_rule(rule, example_content, audit_items)
        
        return {
            "rule_id": rule_id,
            "example_content": example_content,
            "audit_items": audit_items,
            "validation_results": validation_results.get("validation_results", [])
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Error in validate_rule: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )