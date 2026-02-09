# AI 智能面试官 (Interview Agent)

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11-blue.svg" alt="Python 3.11">
  <img src="https://img.shields.io/badge/React-18.2-blue.svg" alt="React 18.2">
  <img src="https://img.shields.io/badge/FastAPI-0.104-green.svg" alt="FastAPI">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT">
</p>

基于大语言模型(GLM-4)的本地部署面试 Agent 系统，支持知识库构建、简历解析、智能面试模拟和实事求是的面试评估。

---

## 项目介绍

### 核心特性

**智能面试引擎**
- **海量题库**: **641+** 道大厂后端面试真题，涵盖 Go、MySQL、Redis、Docker、微服务、分布式系统等
- **动态题库系统**: 根据简历技能栈智能筛选相关技术题目，支持自定义启用/禁用分类
- **多维度评估**: 基于回答长度、技术术语、逻辑解释、代码示例等自动评分
- **实事求是评价**: 面试结束后提供客观、直接、有针对性的反馈，指出具体问题和改进方向
- **追问机制**: 50%概率触发深度追问，考察技术理解深度

**简历解析与编辑**
- **智能解析**: 自动提取姓名、联系方式、工作经验、技能栈等信息
- **可视化编辑**: 支持修改基本信息和工作经历(Markdown编辑器)
- **技能匹配**: 根据技能栈自动匹配相关面试题目

**多种面试模式**
- **预设面试类型**: 后端开发、Go专项、Java专项、考研复试、校招面试
- **DIY面试官**: 自定义面试官风格、考察领域、面试时长
- **系统流程**: 选择面试 → 上传简历 → 智能面试 → 查看报告

**完整导航体验**
- **面包屑导航**: 树状层级结构，清晰展示页面关系
- **URL路由**: 支持浏览器前进/后退，刷新页面不丢失状态
- **本地存储**: 自动保存页面状态，支持断点续面

### 技术架构

```
interview-agent/
├── backend/                    # FastAPI 后端
│   ├── app/
│   │   ├── api/               # API 路由层
│   │   ├── core/              # 核心配置
│   │   ├── models/            # 数据模型
│   │   ├── services/          # 业务逻辑
│   │   └── knowledge_base/    # 知识库模块
│   ├── data/                  # 数据文件
│   └── requirements.txt
├── frontend/                  # React 前端
│   ├── src/
│   │   └── pages/             # 页面组件
│   └── package.json
├── docker-compose.yml         # Docker 编排配置
└── README.md
```

---

## 快速开始

### 环境要求
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose (推荐)

### 方法一：Docker Compose 部署（推荐）

```bash
# 1. 克隆项目
git clone https://github.com/1708737115/Interview-agent.git
cd Interview-agent

# 2. 配置环境变量
cp backend/.env.example backend/.env
# 编辑 backend/.env 文件，填入必需的 API 密钥

# 3. 启动服务
docker-compose up -d

# 4. 选择题库配置（可选）
cp question_bank_light.json question_bank.json  # 轻量版（217题，推荐新手）
# 或
cp question_bank_config.json question_bank.json  # 完整版（641题，推荐生产）

# 5. 访问系统
# 前端: http://localhost:3000
# 后端API文档: http://localhost:8000/docs
```

### 方法二：本地开发环境

**后端启动**

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**前端启动**

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 访问 http://localhost:5173
```

---

## 配置说明

### 必需配置

在 `backend/.env` 文件中配置以下 API 密钥：

```bash
# 智谱 AI GLM-4 API Key (必需)
# 获取地址: https://open.bigmodel.cn/usercenter/apikeys
GLM4_API_KEY=your_glm4_api_key_here
GLM4_MODEL=glm-4-air
GLM4_EMBEDDING_MODEL=embedding-3
GLM4_BASE_URL=https://open.bigmodel.cn/api/paas/v4

# 数据库配置
DATABASE_URL=postgresql://interview_agent:interview_agent_pass@postgres:5432/interview_agent

# ChromaDB配置
CHROMA_DB_PATH=/app/chroma_db

# 应用配置
APP_NAME=Interview Agent
DEBUG=False
SECRET_KEY=your_secret_key_here
```

### 可选配置

```bash
# LlamaParse API Key (可选，用于PDF解析)
# 获取地址: https://cloud.llamaindex.ai/api-key
LLAMAPARSE_API_KEY=your_llamaparse_api_key_here

# LLM配置
MAX_TOKENS=4096
TEMPERATURE=0.7
TOP_K_RETRIEVAL=5
SIMILARITY_THRESHOLD=0.7

# 面试配置
INTERVIEW_DURATION=45
MAX_FOLLOWUPS=8

# 文件上传路径
UPLOAD_DIR=./uploads
```

---

## 部署指南

### Docker 部署架构

```
┌─────────────────┐
│     Nginx       │  ← 前端服务 (Port 3000)
│   (Frontend)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    FastAPI      │  ← 后端服务 (Port 8000)
│    (Backend)    │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌──────────┐
│PostgreSQL│ │ChromaDB │  ← 数据存储
│(Port 5432)│ │(Port 8001)│
└────────┘ └──────────┘
```

### 数据持久化

Docker Compose 配置了以下数据卷：

| 卷名 | 路径 | 说明 |
|------|------|------|
| `postgres_data` | `/var/lib/postgresql/data` | PostgreSQL数据 |
| `chroma_data` | `/chroma/chroma` | ChromaDB向量数据 |
| `./backend/data` | `/app/data` | 面试题知识库 |
| `./backend/uploads` | `/app/uploads` | 上传的简历文件 |

### 常用命令

```bash
# 启动所有服务
docker-compose up -d

# 停止所有服务
docker-compose down

# 重启服务
docker-compose restart

# 查看日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend

# 进入后端容器
docker-compose exec backend bash

# 进入数据库容器
docker-compose exec postgres psql -U interview_agent -d interview_agent
```

---

## 面试流程

1. **首页**: 选择预设面试类型或DIY面试官
2. **上传简历**: 拖拽PDF/DOCX文件，自动解析信息
3. **确认信息**: 查看解析结果，支持编辑修改
4. **智能面试**: 与AI面试官对话答题
5. **查看报告**: 查看详细评分和评价

---

**项目地址**: https://github.com/1708737115/Interview-agent
