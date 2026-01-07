from fastapi import APIRouter, HTTPException, status
from typing import List
from app.models import (
    AuditItem,
    AuditItemCreate,
    AuditItemUpdate
)
from datetime import datetime
from uuid import uuid4

router = APIRouter()

# 使用内存存储替代MongoDB
audit_items_db = {}

@router.post("/", response_model=AuditItem, status_code=status.HTTP_201_CREATED)
async def create_audit_item(item: AuditItemCreate):
    """创建新的审核项"""
    try:
        item_dict = item.model_dump()
        item_id = str(uuid4())
        item_dict["_id"] = item_id
        item_dict["created_at"] = datetime.utcnow()
        item_dict["updated_at"] = datetime.utcnow()
        
        audit_items_db[item_id] = item_dict
        
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
        return [AuditItem(**item) for item in audit_items_db.values()]
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
        return [AuditItem(**item) for item in audit_items_db.values() if item["rule_id"] == rule_id]
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
        item = audit_items_db.get(item_id)
        if item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Audit item not found"
            )
        return AuditItem(**item)
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
        item = audit_items_db.get(item_id)
        if item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Audit item not found"
            )
        
        update_data = item_update.model_dump(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow()
        
        updated_item = {**item, **update_data}
        audit_items_db[item_id] = updated_item
        
        return AuditItem(**updated_item)
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
        if item_id not in audit_items_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Audit item not found"
            )
        
        del audit_items_db[item_id]
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