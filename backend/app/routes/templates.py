from fastapi import APIRouter, HTTPException, status
from typing import List
from app.models import (
    Template,
    TemplateCreate,
    TemplateUpdate
)
from datetime import datetime
from uuid import uuid4

router = APIRouter()

# 使用内存存储替代MongoDB
templates_db = {}

@router.post("/", response_model=Template, status_code=status.HTTP_201_CREATED)
async def create_template(template: TemplateCreate):
    """创建新的版式模板"""
    try:
        template_dict = template.model_dump()
        template_id = str(uuid4())
        template_dict["_id"] = template_id
        template_dict["created_at"] = datetime.utcnow()
        template_dict["updated_at"] = datetime.utcnow()
        
        templates_db[template_id] = template_dict
        
        return Template(**template_dict)
    except Exception as e:
        import traceback
        print(f"Error in create_template: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/", response_model=List[Template])
async def get_templates():
    """获取所有版式模板"""
    try:
        return [Template(**template) for template in templates_db.values()]
    except Exception as e:
        import traceback
        print(f"Error in get_templates: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/{template_id}", response_model=Template)
async def get_template(template_id: str):
    """获取单个版式模板"""
    try:
        template = templates_db.get(template_id)
        if template is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )
        return Template(**template)
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Error in get_template: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.put("/{template_id}", response_model=Template)
async def update_template(template_id: str, template_update: TemplateUpdate):
    """更新版式模板"""
    try:
        template = templates_db.get(template_id)
        if template is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )
        
        update_data = template_update.model_dump(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow()
        
        updated_template = {**template, **update_data}
        templates_db[template_id] = updated_template
        
        return Template(**updated_template)
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Error in update_template: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template(template_id: str):
    """删除版式模板"""
    try:
        if template_id not in templates_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )
        
        del templates_db[template_id]
        return None
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Error in delete_template: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )