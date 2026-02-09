# Interview Agent System

基于GLM-4的本地部署面试Agent系统，支持知识库构建和双模式面试。

## 技术栈

- **LLM引擎**: GLM-4-Air/Plus (智谱AI)
- **Embedding**: GLM-4-Embedding
- **PDF解析**: LlamaParse
- **后端**: FastAPI + Python 3.11
- **向量数据库**: ChromaDB
- **关系数据库**: PostgreSQL
- **前端**: React + TypeScript

## 快速开始

### 1. 环境准备

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入你的API密钥
# 必需: GLM4_API_KEY (从智谱AI控制台获取)
# 可选: LLAMAPARSE_API_KEY (如需PDF解析功能)
```

### 2. 本地启动

```bash
# 使用Docker Compose启动
docker-compose up -d

# 或者手动启动后端
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. 访问系统

- **后端API文档**: http://localhost:8000/docs
- **前端界面**: http://localhost:3000

## 功能特性

### 知识库管理
- 支持PDF、Word、Markdown、TXT文档上传
- 自动解析和向量化
- 支持复杂表格和图片内容

### 双模式面试
1. **结构化面试**: 基于知识库生成标准问题序列
2. **开放式面试**: 自由对话，深度追问

### 智能评估
- 多维度评分（准确性、完整性、逻辑性、深度）
- 实时反馈和建议
- 面试报告生成

## 项目结构

```
interview-agent/
├── backend/          # FastAPI后端
│   ├── app/
│   │   ├── api/     # API路由
│   │   ├── core/    # 核心配置
│   │   ├── models/  # 数据模型
│   │   └── services/# 业务逻辑
│   └── requirements.txt
├── frontend/        # React前端
│   └── src/
└── docker-compose.yml
```

## API Key获取

1. **GLM-4 API Key**: https://open.bigmodel.cn/usercenter/apikeys
2. **LlamaParse API Key**: https://cloud.llamaindex.ai/api-key

## 许可证

MIT
