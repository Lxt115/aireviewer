from fastapi import APIRouter, HTTPException, status
from typing import List
from app.models import (
    AuditItem,
    AuditItemCreate,
    AuditItemUpdate
)
from app.db.sqlite import query, insert, update, delete
from datetime import datetime
from uuid import uuid4

router = APIRouter()

@router.post("/", response_model=AuditItem, status_code=status.HTTP_201_CREATED)
async def create_audit_item(item: AuditItemCreate):
    """创建新的审核项"""
    try:
        item_dict = item.model_dump()
        item_id = str(uuid4())
        item_dict["_id"] = item_id
        item_dict["created_at"] = datetime.utcnow().isoformat()
        item_dict["updated_at"] = datetime.utcnow().isoformat()
        
        await insert("audit_items", item_dict)
        
        return AuditItem(**item_dict)
    except Exception as e:
        import traceback
        print(f"Error in create_audit_item: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/", response_model=List[AuditItem])
async def get_audit_items():
    """获取所有审核项"""
    try:
        # 从SQLite数据库查询所有审核项
        results = await query("SELECT * FROM audit_items")
        
        # 转换为AuditItem对象
        audit_items = []
        for result in results:
            audit_item_dict = {
                "_id": result[0],
                "name": result[1],
                "rule_id": result[2],
                "type": result[3],
                "criteria": result[4],
                "created_at": result[5],
                "updated_at": result[6]
            }
            audit_items.append(AuditItem(**audit_item_dict))
        
        return audit_items
    except Exception as e:
        import traceback
        print(f"Error in get_audit_items: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/rule/{rule_id}", response_model=List[AuditItem])
async def get_audit_items_by_rule(rule_id: str):
    """根据规则获取审核项"""
    try:
        # 从SQLite数据库查询指定规则的审核项
        results = await query("SELECT * FROM audit_items WHERE rule_id = ?", (rule_id,))
        
        # 转换为AuditItem对象
        audit_items = []
        for result in results:
            audit_item_dict = {
                "_id": result[0],
                "name": result[1],
                "rule_id": result[2],
                "type": result[3],
                "criteria": result[4],
                "created_at": result[5],
                "updated_at": result[6]
            }
            audit_items.append(AuditItem(**audit_item_dict))
        
        return audit_items
    except Exception as e:
        import traceback
        print(f"Error in get_audit_items_by_rule: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/{item_id}", response_model=AuditItem)
async def get_audit_item(item_id: str):
    """获取单个审核项"""
    try:
        # 从SQLite数据库查询单个审核项
        results = await query("SELECT * FROM audit_items WHERE _id = ?", (item_id,))
        
        if not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Audit item not found"
            )
        
        # 转换为AuditItem对象
        result = results[0]
        audit_item_dict = {
            "_id": result[0],
            "name": result[1],
            "rule_id": result[2],
            "type": result[3],
            "criteria": result[4],
            "created_at": result[5],
            "updated_at": result[6]
        }
        
        return AuditItem(**audit_item_dict)
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Error in get_audit_item: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.put("/{item_id}", response_model=AuditItem)
async def update_audit_item(item_id: str, item_update: AuditItemUpdate):
    """更新审核项"""
    try:
        # 检查审核项是否存在
        results = await query("SELECT * FROM audit_items WHERE _id = ?", (item_id,))
        if not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Audit item not found"
            )
        
        # 更新数据
        update_data = item_update.model_dump(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow().isoformat()
        
        # 更新SQLite数据库
        await update(
            "audit_items",
            update_data,
            "_id = ?",
            (item_id,)
        )
        
        # 查询更新后的审核项
        updated_results = await query("SELECT * FROM audit_items WHERE _id = ?", (item_id,))
        if not updated_results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Audit item not found after update"
            )
        
        # 转换为AuditItem对象
        result = updated_results[0]
        audit_item_dict = {
            "_id": result[0],
            "name": result[1],
            "rule_id": result[2],
            "type": result[3],
            "criteria": result[4],
            "created_at": result[5],
            "updated_at": result[6]
        }
        
        return AuditItem(**audit_item_dict)
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Error in update_audit_item: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_audit_item(item_id: str):
    """删除审核项"""
    try:
        # 检查审核项是否存在
        results = await query("SELECT * FROM audit_items WHERE _id = ?", (item_id,))
        if not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Audit item not found"
            )
        
        # 删除审核项
        await delete("audit_items", "_id = ?", (item_id,))
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Error in delete_audit_item: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )