# 基于规则的大模型多模态智能审核平台

## 技术栈

- **后端**: FastAPI + Python
- **前端**: React + TypeScript + Vite
- **UI组件库**: Ant Design

## 快速启动

### 后端启动

1. 进入后端目录
   ```bash
   cd backend
   ```

2. 安装依赖
   ```bash
   pip install -r requirements.txt
   ```

3. 启动服务
   ```bash
   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

4. 访问地址
   - API文档: http://localhost:8000/docs
   - 健康检查: http://localhost:8000/health

### 前端启动

1. 进入前端目录
   ```bash
   cd frontend
   ```

2. 安装依赖
   ```bash
   npm install
   ```

3. 启动开发服务器
   ```bash
   npm run dev
   ```

4. 访问地址
   - 应用地址: http://localhost:5173

## 项目结构

```
AIReviewer/
├── backend/          # 后端代码
│   ├── app/          # 应用核心代码
│   ├── uploads/      # 文件上传目录
│   └── main.py       # 后端入口
└── frontend/         # 前端代码
    ├── public/       # 静态资源
    └── src/          # 源代码
```