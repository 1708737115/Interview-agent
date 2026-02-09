# AI 智能面试官 (Interview Agent)

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11-blue.svg" alt="Python 3.11">
  <img src="https://img.shields.io/badge/React-18.2-blue.svg" alt="React 18.2">
  <img src="https://img.shields.io/badge/FastAPI-0.104-green.svg" alt="FastAPI">
  <img src="https://img.shields.io/badge/ChromaDB-向量数据库-purple.svg" alt="ChromaDB">
  <img src="https://img.shields.io/badge/PostgreSQL-15-blue.svg" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT">
</p>

基于大语言模型(GLM-4)的本地部署面试 Agent 系统，支持知识库构建、简历解析、智能面试模拟和实事求是的面试评估。

---

## ✨ Features/Overview

### 核心特性

**智能面试引擎**
- **海量题库**: **641+** 道大厂后端面试真题，涵盖 Go、MySQL、Redis、Docker、微服务、分布式系统等
- **动态题库系统**: 根据简历技能栈智能筛选相关技术题目，支持自定义启用/禁用分类
- **多维度评估**: 基于回答长度、技术术语、逻辑解释、代码示例等自动评分
- **实事求是评价**: 面试结束后提供客观、直接、有针对性的反馈
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

---

## 🏗️ Architecture

### 系统架构

```
用户层                    API层                  服务层                    数据层
┌─────────┐             ┌─────────────┐        ┌─────────────────┐     ┌──────────────┐
│  前端    │ ─────────── │  FastAPI    │ ────── │ InterviewerAgent │ ── │  面试题知识库  │
│ (React) │             │   Routes    │        │    (核心Agent)   │     │  (ChromaDB)  │
└─────────┘             └─────────────┘        └─────────────────┘     └──────────────┘
                              │                           │
                              ▼                    ┌──────┴───────┐
                        ┌──────────────┐    ┌────────────┐  ┌────────────┐
                        │ ResumeParser │    │ 风格配置器  │  │ 简历解析器  │
                        │ (简历上传)   │    │(牛客风格)  │  │(LLM解析)   │
                        └──────────────┘    └────────────┘  └────────────┘
```

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

### 面试流程

```
候选人上传简历
    │
    ▼
┌─────────────────┐
│ 简历解析服务    │
│ - 文本提取     │
│ - 结构化分析   │
│ - 能力评估     │
│ - 策略生成     │
└─────────────────┘
    │
    ▼
生成简历画像 + 面试策略
    │
    ▼
开始面试 (45分钟)
    │
    ├── 开场破冰 (3分钟)
    ├── 技术基础面试 (20分钟)
    │   ├── 根据策略选择知识点
    │   ├── 生成个性化问题
    │   ├── 评估回答质量
    │   └── 智能追问 (最多8次)
    ├── 项目深挖 (12分钟)
    ├── 场景设计 (8分钟)
    └── 总结反馈 (2分钟)
            │
            ▼
    ┌─────────────────┐
    │ 面试报告生成    │
    │ - 多维度评分   │
    │ - 能力画像     │
    │ - 改进建议     │
    └─────────────────┘
```

---

## 🚀 Quick Start

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

# 3. 选择题库配置（可选）
cp question_bank_light.json question_bank.json  # 轻量版（217题，推荐新手）
# 或
cp question_bank_config.json question_bank.json  # 完整版（641题，推荐生产）

# 4. 启动服务
docker-compose up -d

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

## ⚙️ Configuration

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

## 📚 Question Bank

本系统提供多种题库配置，您可以根据实际需求选择合适的版本。

### 可用配置文件

| 文件 | 题目数 | 用途 | 推荐场景 |
|------|--------|------|----------|
| `question_bank_light.json` | 217题 | 轻量版 | 快速体验、测试部署 |
| `question_bank_config.json` | 641题 | 完整版 | 生产环境、正式面试 |
| `question_bank_index.json` | 仅索引 | 索引版 | 大规模部署、自定义题库 |

### 快速开始（使用轻量版）

```bash
# 复制轻量版配置为默认配置
cp question_bank_light.json question_bank.json

# 启动服务
docker-compose up -d
```

### 题库分类统计

当前题库共包含 **641** 道题目：

| 分类 | 题目数 | 子分类 |
|------|--------|--------|
| **计算机基础** | 50题 | Linux (41题)、计算机网络 (7题)、操作系统 (2题) |
| **编程语言** | 85题 | Go语言 (85题) |
| **数据库** | 153题 | MySQL (55题)、Redis (94题)、MongoDB (4题) |
| **消息队列** | 40题 | Kafka (40题) |
| **后端组件** | 81题 | Docker (59题)、Nginx (10题)、Elasticsearch (12题) |
| **架构设计** | 229题 | 系统设计 (189题)、分布式系统 (21题)、微服务 (19题) |
| **项目经历** | 3题 | 项目深挖 (3题) |

### 自定义题库

#### 启用/禁用分类

```json
{
  "groups": {
    "languages": {
      "enabled": true,
      "categories": {
        "language_go": {
          "enabled": true
        }
      }
    }
  }
}
```

#### 添加自定义题目

```json
{
  "id": "custom-001",
  "text": "你的自定义题目",
  "category": "database_mysql",
  "difficulty": 3,
  "type": "technical"
}
```

字段说明：
- `id`: 唯一标识符
- `text`: 题目内容
- `category`: 分类标识
- `difficulty`: 难度等级（1-5，1最简单，5最难）
- `type`: 题目类型（`technical`技术题/`design`设计题/`project`项目题）

### 推荐配置方案

**后端开发标准版**（400-450题）
- ✅ Go语言、MySQL、Redis、Kafka
- ✅ Docker、Nginx、Linux、网络
- ✅ 微服务、分布式系统、系统设计

**校招/初级版**（200-250题）
- ✅ Go语言、MySQL、Redis（基础题）
- ✅ Linux、网络、操作系统
- ⏭️ 跳过：架构设计、系统设计（难度较高）

**高级/架构师版**（600+题）
- ✅ 所有分类全部启用
- ✅ 重点：系统设计、分布式系统、微服务

### 修改配置后重启

```bash
docker-compose restart backend
```

---

## 📄 PDF Import

本系统支持通过PDF文件扩展面试题库。

### 目录结构

```
interview-agent/
├── question_pdfs/              # 存放PDF文件的目录
├── question_bank_config.json   # 基础题库（JSON格式）
├── import_pdf_questions.py     # PDF导入脚本
└── backend/app/data/           # 合并后的题库输出目录
    └── merged_question_bank.json
```

### 使用方法

**方法一：手动导入（开发环境）**

```bash
# 1. 将PDF文件放入 question_pdfs/ 目录
cp /path/to/your/interview_questions.pdf question_pdfs/

# 2. 运行导入脚本
python3 import_pdf_questions.py

# 输出文件: backend/app/data/merged_question_bank.json
```

**方法二：部署时自动导入（推荐）**

```bash
# 1. 将PDF放入目录
cp your_questions.pdf question_pdfs/

# 2. 正常部署
docker-compose up -d

# 部署脚本会自动执行导入并加载合并后的题库
```

### 高级配置

```bash
# 指定PDF目录
python3 import_pdf_questions.py --pdf-dir /custom/pdf/path

# 指定输出文件
python3 import_pdf_questions.py --output /custom/output.json

# 指定基础题库
python3 import_pdf_questions.py --base-bank question_bank_light.json

# 组合使用
python3 import_pdf_questions.py \
  --pdf-dir my_pdfs/ \
  --output backend/app/data/my_bank.json \
  --base-bank question_bank_config.json
```

### 自动分类规则

| 关键词 | 分类 |
|-------|------|
| go, goroutine, channel | Go语言 |
| java, jvm, spring | Java |
| mysql, sql, 索引 | MySQL |
| redis, 缓存 | Redis |
| kafka, 消息队列 | Kafka |
| docker, 容器 | Docker |
| linux, 命令 | Linux |
| tcp, http, 网络 | 计算机网络 |
| 微服务, ddd | 微服务 |
| 分布式, cap | 分布式系统 |
| 设计, 秒杀, 短链接 | 系统设计 |

### 更新题库流程

```bash
# 1. 添加新的PDF
cp new_interview_questions.pdf question_pdfs/

# 2. 重新导入（会自动合并所有PDF）
python3 import_pdf_questions.py

# 3. 重启服务（如果使用Docker）
docker-compose restart backend
```

---

## 🐳 Deployment

### 环境准备

确保已安装：
- Docker Engine 20.10+
- Docker Compose 2.0+

```bash
# 检查版本
docker --version
docker-compose --version
```

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

### 数据持久化

Docker Compose 配置了以下数据卷：

| 卷名 | 路径 | 说明 |
|------|------|------|
| `postgres_data` | `/var/lib/postgresql/data` | PostgreSQL数据 |
| `chroma_data` | `/chroma/chroma` | ChromaDB向量数据 |
| `./backend/data` | `/app/data` | 面试题知识库 |
| `./backend/uploads` | `/app/uploads` | 上传的简历文件 |

### 生产环境部署

**使用外部数据库**

修改 `docker-compose.yml`：
```yaml
services:
  backend:
    environment:
      - DATABASE_URL=postgresql://user:password@your-db-host:5432/interview_agent
```

**配置HTTPS**

使用 Traefik 或 Nginx Proxy Manager 配置 SSL 证书。

**自动重启策略**

所有服务已配置 `restart: unless-stopped`，系统重启后会自动启动。

### 备份数据

```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)

# 备份PostgreSQL
docker-compose exec postgres pg_dump -U interview_agent interview_agent > backup_${DATE}.sql

# 备份知识库
cp backend/data/processed/enhanced_questions.json backup_questions_${DATE}.json

# 备份向量数据库
tar czf backup_chroma_${DATE}.tar.gz chroma_db/

echo "备份完成: ${DATE}"
```

---

## 📁 Project Structure

```
interview-agent/
├── .gitignore                      # Git忽略文件配置
├── docker-compose.yml              # Docker编排配置
├── deploy.sh                       # 部署脚本
├── start.sh                        # 启动脚本
├── README.md                       # 项目主文档
├── LICENSE                         # MIT许可证
│
├── backend/                        # FastAPI后端
│   ├── Dockerfile                  # 后端容器镜像配置
│   ├── docker-entrypoint.sh        # 容器启动入口脚本
│   ├── requirements.txt            # Python依赖
│   ├── .env.example                # 环境变量模板
│   ├── app/                        # 应用代码
│   │   ├── api/                    # API路由
│   │   │   └── routes/
│   │   │       └── interview.py    # 面试API路由
│   │   ├── core/                   # 核心配置
│   │   │   └── config.py           # 配置管理
│   │   ├── models/                 # 数据模型
│   │   │   ├── schemas.py          # Pydantic模型
│   │   │   └── database.py         # 数据库模型
│   │   ├── services/               # 业务逻辑
│   │   │   ├── llm_service.py      # GLM-4服务封装
│   │   │   ├── interview_service.py # 面试引擎
│   │   │   ├── resume_analyzer.py  # 简历解析器
│   │   │   └── document_service.py # 文档处理
│   │   └── knowledge_base/         # 知识库模块
│   │       ├── github_sync.py      # GitHub数据同步
│   │       ├── markdown_parser.py  # Markdown解析
│   │       ├── llm_enhancer.py     # LLM增强处理
│   │       ├── vector_store.py     # 向量数据库存储
│   │       └── build_knowledge_base.py # 主构建流程
│   └── data/                       # 数据文件
│       ├── repos/                  # GitHub仓库镜像
│       ├── processed/              # 处理后数据
│       └── chroma_db/              # 向量数据库
│
├── frontend/                       # React前端
│   ├── Dockerfile                  # 前端容器镜像配置
│   ├── package.json                # Node依赖
│   ├── nginx.conf                  # Nginx配置
│   └── src/                        # 源代码
│       └── pages/                  # 页面组件
│
├── question_pdfs/                  # 扩展题库PDF目录
│   └── (用户可放入自己的PDF题库)
│
├── uploads/                        # 上传文件目录
├── chroma_db/                      # 向量数据库
│
├── question_bank_config.json       # 基础题库配置（641题）
├── question_bank_light.json        # 轻量版题库（217题）
├── question_bank_index.json        # 题库分类索引
│
├── import_pdf_questions.py         # PDF题库导入工具
└── uploads_lifecycle.py            # 上传文件生命周期管理
```

### 核心脚本

**import_pdf_questions.py**
- 解析PDF文件并提取面试题目，合并到题库中
- 自动执行：部署时通过 `docker-entrypoint.sh` 自动执行

**uploads_lifecycle.py**
- 上传文件生命周期管理（7天压缩，30天删除）
- 定时任务：可添加到 crontab 每天执行

---

## 🤝 Contributing

欢迎提交 Issue 和 Pull Request！

1. Fork 本项目
2. 创建您的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开一个 Pull Request

---

## 📄 License

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

---

**项目地址**: https://github.com/1708737115/Interview-agent
