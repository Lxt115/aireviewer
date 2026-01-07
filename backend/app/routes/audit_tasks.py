from fastapi import APIRouter, HTTPException, status
from typing import List
from app.models import (
    AuditTask,
    AuditTaskCreate,
    AuditTaskUpdate,
    AuditResult,
    AuditResultCreate,
    AuditResultUpdate
)
from app.services.ai_service import ai_service
from datetime import datetime
from uuid import uuid4

router = APIRouter()

# 使用内存存储替代MongoDB
audit_tasks_db = {}
audit_results_db = {}

@router.post("/", response_model=AuditTask, status_code=status.HTTP_201_CREATED)
async def create_audit_task(task: AuditTaskCreate):
    """创建新的审核任务"""
    try:
        task_dict = task.model_dump()
        task_id = str(uuid4())
        task_dict["_id"] = task_id
        task_dict["created_at"] = datetime.utcnow()
        task_dict["updated_at"] = datetime.utcnow()
        task_dict["status"] = "pending"
        
        audit_tasks_db[task_id] = task_dict
        
        return AuditTask(**task_dict)
    except Exception as e:
        import traceback
        print(f"Error in create_audit_task: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/", response_model=List[AuditTask])
async def get_audit_tasks():
    """获取所有审核任务"""
    try:
        return [AuditTask(**task) for task in audit_tasks_db.values()]
    except Exception as e:
        import traceback
        print(f"Error in get_audit_tasks: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/{task_id}", response_model=AuditTask)
async def get_audit_task(task_id: str):
    """获取单个审核任务"""
    try:
        task = audit_tasks_db.get(task_id)
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Audit task not found"
            )
        return AuditTask(**task)
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Error in get_audit_task: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.put("/{task_id}", response_model=AuditTask)
async def update_audit_task(task_id: str, task_update: AuditTaskUpdate):
    """更新审核任务"""
    try:
        task = audit_tasks_db.get(task_id)
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Audit task not found"
            )
        
        update_data = task_update.model_dump(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow()
        
        updated_task = {**task, **update_data}
        audit_tasks_db[task_id] = updated_task
        
        return AuditTask(**updated_task)
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Error in update_audit_task: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_audit_task(task_id: str):
    """删除审核任务"""
    try:
        if task_id not in audit_tasks_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Audit task not found"
            )
        
        del audit_tasks_db[task_id]
        
        # 同时删除关联的审核结果
        for result_id, result in list(audit_results_db.items()):
            if result["task_id"] == task_id:
                del audit_results_db[result_id]
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Error in delete_audit_task: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/{task_id}/run")
async def run_audit_task(task_id: str):
    """运行审核任务"""
    try:
        # 更新任务状态为running
        task = audit_tasks_db.get(task_id)
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Audit task not found"
            )
        
        task["status"] = "running"
        task["updated_at"] = datetime.utcnow()
        audit_tasks_db[task_id] = task
        
        # 简化处理，直接生成模拟结果
        # 模拟完成任务
        task["status"] = "completed"
        task["completed_at"] = datetime.utcnow()
        task["updated_at"] = datetime.utcnow()
        audit_tasks_db[task_id] = task
        
        return {
            "message": "Audit task completed",
            "task_id": task_id,
            "status": "completed"
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Error in run_audit_task: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/{task_id}/results", response_model=List[AuditResult])
async def get_audit_results(task_id: str):
    """获取审核任务的结果"""
    try:
        # 检查任务是否存在
        if task_id not in audit_tasks_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Audit task not found"
            )
        
        # 返回该任务的所有结果
        return [AuditResult(**result) for result in audit_results_db.values() if result["task_id"] == task_id]
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Error in get_audit_results: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.put("/{task_id}/results/{result_id}", response_model=AuditResult)
async def update_audit_result(result_id: str, result_update: AuditResultUpdate):
    """更新审核结果"""
    try:
        result = audit_results_db.get(result_id)
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Audit result not found"
            )
        
        update_data = result_update.model_dump(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow()
        update_data["ai_generated"] = False
        
        updated_result = {**result, **update_data}
        audit_results_db[result_id] = updated_result
        
        return AuditResult(**updated_result)
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Error in update_audit_result: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/{task_id}/download")
async def download_audit_result(task_id: str):
    """下载审核结果"""
    try:
        # 检查任务是否存在
        if task_id not in audit_tasks_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Audit task not found"
            )
        
        return {
            "message": "Audit result downloaded successfully",
            "task_id": task_id,
            "download_url": f"/api/tasks/{task_id}/results/download"
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Error in download_audit_result: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/statistics/summary")
async def get_audit_statistics():
    """获取审核任务统计数据"""
    try:
        # 统计不同状态的任务数量
        completed_tasks = sum(1 for task in audit_tasks_db.values() if task["status"] == "completed")
        pending_tasks = sum(1 for task in audit_tasks_db.values() if task["status"] == "pending")
        
        # 统计审核结果中的警告和失败数量
        warning_results = sum(1 for result in audit_results_db.values() if result["result"] == "warning")
        failed_results = sum(1 for result in audit_results_db.values() if result["result"] == "fail")
        
        return {
            "completed_tasks": completed_tasks,
            "pending_tasks": pending_tasks,
            "warning_tasks": warning_results,
            "failed_tasks": failed_results
        }
    except Exception as e:
        import traceback
        print(f"Error in get_audit_statistics: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )