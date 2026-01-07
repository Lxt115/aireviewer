from fastapi import APIRouter, UploadFile, File, HTTPException, status
import os
import shutil
import uuid
import re

router = APIRouter()

UPLOAD_DIR = "uploads"
ALLOWED_EXTENSIONS = {'.txt', '.xls', '.xlsx', '.doc', '.docx', '.pdf', '.png', '.jpg', '.jpeg', '.gif'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

os.makedirs(UPLOAD_DIR, exist_ok=True)

def sanitize_filename(filename: str) -> str:
    filename = os.path.basename(filename)
    filename = re.sub(r'[^\w\s.-]', '', filename)
    filename = re.sub(r'\s+', '_', filename)
    return filename

def validate_file_extension(filename: str) -> bool:
    ext = os.path.splitext(filename)[1].lower()
    return ext in ALLOWED_EXTENSIONS

async def validate_upload_file(file: UploadFile) -> None:
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="文件名不能为空")
    
    if not validate_file_extension(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"不支持的文件类型。允许的类型: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    file_size = 0
    content = await file.read(1024)
    file_size += len(content)
    await file.seek(0)
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"文件大小超过限制。最大允许: {MAX_FILE_SIZE // 1024 // 1024}MB"
        )

@router.post("/upload")
async def upload_files(
    file: list[UploadFile] = File(...)
):
    """上传文件API，支持单个文件和多个文件上传"""
    uploaded_files = []
    for f in file:
        await validate_upload_file(f)
        
        sanitized_filename = sanitize_filename(f.filename)
        file_extension = os.path.splitext(sanitized_filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(f.file, buffer)
        
        uploaded_files.append({
            "filename": sanitized_filename,
            "unique_filename": unique_filename,
            "file_path": file_path,
            "content_type": f.content_type
        })
    
    if len(uploaded_files) == 1:
        return {
            "message": "文件上传成功",
            "file": uploaded_files[0]
        }
    else:
        return {
            "message": "文件上传成功",
            "files": uploaded_files
        }
