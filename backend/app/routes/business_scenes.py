from fastapi import APIRouter, HTTPException, status
from typing import List
from app.models import (
    BusinessScene,
    BusinessSceneCreate,
    BusinessSceneUpdate
)
from app.db.sqlite import query, insert, update, delete
from app.core.security import input_validator
from datetime import datetime
from uuid import uuid4

router = APIRouter()

@router.post("/", response_model=BusinessScene, status_code=status.HTTP_201_CREATED)
async def create_business_scene(scene: BusinessSceneCreate):
    """创建新的业务场景"""
    try:
        scene_dict = scene.model_dump()
        scene_dict["name"] = input_validator.validate_name(scene_dict.get("name", ""), "name")
        if scene_dict.get("description"):
            scene_dict["description"] = input_validator.validate_description(scene_dict["description"])
        
        scene_id = str(uuid4())
        scene_dict["_id"] = scene_id
        scene_dict["created_at"] = datetime.utcnow().isoformat()
        scene_dict["updated_at"] = datetime.utcnow().isoformat()
        
        await insert("business_scenes", scene_dict)
        
        return BusinessScene(**scene_dict)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        import traceback
        print(f"Error in create_business_scene: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/", response_model=List[BusinessScene])
async def get_business_scenes():
    """获取所有业务场景"""
    try:
        # 从SQLite数据库查询所有业务场景
        results = await query("SELECT * FROM business_scenes")
        
        # 转换为BusinessScene对象
        scenes = []
        for result in results:
            scene_dict = {
                "_id": result[0],
                "name": result[1],
                "description": result[2],
                "created_at": result[3],
                "updated_at": result[4]
            }
            scenes.append(BusinessScene(**scene_dict))
        
        return scenes
    except Exception as e:
        import traceback
        print(f"Error in get_business_scenes: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/{scene_id}", response_model=BusinessScene)
async def get_business_scene(scene_id: str):
    """获取单个业务场景"""
    try:
        # 从SQLite数据库查询单个业务场景
        results = await query("SELECT * FROM business_scenes WHERE _id = ?", (scene_id,))
        
        if not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Business scene not found"
            )
        
        # 转换为BusinessScene对象
        result = results[0]
        scene_dict = {
            "_id": result[0],
            "name": result[1],
            "description": result[2],
            "created_at": result[3],
            "updated_at": result[4]
        }
        
        return BusinessScene(**scene_dict)
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Error in get_business_scene: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.put("/{scene_id}", response_model=BusinessScene)
async def update_business_scene(scene_id: str, scene_update: BusinessSceneUpdate):
    """更新业务场景"""
    try:
        # 检查业务场景是否存在
        results = await query("SELECT * FROM business_scenes WHERE _id = ?", (scene_id,))
        if not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Business scene not found"
            )
        
        # 更新数据
        update_data = scene_update.model_dump(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow().isoformat()
        
        # 更新SQLite数据库
        await update(
            "business_scenes",
            update_data,
            "_id = ?",
            (scene_id,)
        )
        
        # 查询更新后的业务场景
        updated_results = await query("SELECT * FROM business_scenes WHERE _id = ?", (scene_id,))
        if not updated_results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Business scene not found after update"
            )
        
        # 转换为BusinessScene对象
        result = updated_results[0]
        scene_dict = {
            "_id": result[0],
            "name": result[1],
            "description": result[2],
            "created_at": result[3],
            "updated_at": result[4]
        }
        
        return BusinessScene(**scene_dict)
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Error in update_business_scene: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.delete("/{scene_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_business_scene(scene_id: str):
    """删除业务场景，同时删除该场景下的所有关联数据"""
    try:
        # 检查业务场景是否存在
        results = await query("SELECT * FROM business_scenes WHERE _id = ?", (scene_id,))
        if not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Business scene not found"
            )
        
        # 先获取该场景下的所有规则
        rules = await query("SELECT _id FROM rules WHERE scene_id = ?", (scene_id,))
        
        # 删除每个规则及其关联的审核项
        for rule in rules:
            rule_id = rule[0]
            # 删除关联的审核项
            await delete("audit_items", "rule_id = ?", (rule_id,))
            # 删除审核结果
            await delete("audit_results", "rule_id = ?", (rule_id,))
            # 删除规则
            await delete("rules", "_id = ?", (rule_id,))
        
        # 获取该场景下的所有审核任务
        tasks = await query("SELECT _id FROM audit_tasks WHERE scene_id = ?", (scene_id,))
        
        # 删除每个审核任务及其关联的审核结果
        for task in tasks:
            task_id = task[0]
            # 删除关联的审核结果
            await delete("audit_results", "task_id = ?", (task_id,))
            # 删除审核任务
            await delete("audit_tasks", "_id = ?", (task_id,))
        
        # 最后删除业务场景
        await delete("business_scenes", "_id = ?", (scene_id,))
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Error in delete_business_scene: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )