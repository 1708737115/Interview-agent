# 项目结构说明

## 📁 目录结构

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
│   ├── app/                        # 应用代码
│   │   ├── api/                    # API路由
│   │   ├── core/                   # 核心配置
│   │   ├── models/                 # 数据模型
│   │   └── services/               # 业务逻辑
│   └── data/                       # 数据文件
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
│   └── .gitkeep                    # 保持目录存在
│
├── chroma_db/                      # 向量数据库
├── backend/app/data/               # 后端数据目录
│
├── question_bank_config.json       # 基础题库配置（641题）
├── question_bank_light.json        # 轻量版题库（217题）
├── question_bank_index.json        # 题库分类索引
│
├── import_pdf_questions.py         # PDF题库导入工具
└── uploads_lifecycle.py            # 上传文件生命周期管理
```

## 📚 文档索引

| 文档 | 说明 |
|------|------|
| [README.md](README.md) | 项目主文档，快速开始指南 |
| [QUESTION_BANK_CONFIG.md](QUESTION_BANK_CONFIG.md) | 题库配置选择指南 |
| [QUESTION_BANK_GUIDE.md](QUESTION_BANK_GUIDE.md) | 题库详细配置说明 |
| [QUESTION_PDF_GUIDE.md](QUESTION_PDF_GUIDE.md) | PDF扩展题库使用指南 |
| [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) | Docker部署详细说明 |
| [ARCHITECTURE.md](ARCHITECTURE.md) | 系统架构设计文档 |

## 🔧 核心脚本

### import_pdf_questions.py
**功能**: 解析PDF文件并提取面试题目，合并到题库中

**使用**:
```bash
# 基础使用
python3 import_pdf_questions.py

# 自定义参数
python3 import_pdf_questions.py \
  --pdf-dir question_pdfs/ \
  --base-bank question_bank_config.json \
  --output backend/app/data/merged_question_bank.json
```

**自动执行**: 部署时通过 `docker-entrypoint.sh` 自动执行

### uploads_lifecycle.py
**功能**: 上传文件生命周期管理（7天压缩，30天删除）

**使用**:
```bash
# 模拟运行（不实际执行）
python3 uploads_lifecycle.py --dry-run

# 实际执行
python3 uploads_lifecycle.py

# 自定义目录
python3 uploads_lifecycle.py --uploads-dir /custom/path
```

**定时任务** (添加到crontab):
```bash
# 每天凌晨2点执行
0 2 * * * cd /path/to/interview-agent && python3 uploads_lifecycle.py
```

## 📦 题库文件

### 配置文件说明

| 文件 | 题目数 | 用途 | 推荐场景 |
|------|--------|------|----------|
| `question_bank_config.json` | 641题 | 完整版 | 生产环境 |
| `question_bank_light.json` | 217题 | 轻量版 | 快速体验/测试 |
| `question_bank_index.json` | 仅索引 | 索引版 | 动态加载 |

### 题库分类

**计算机基础** (50题)
- Linux (41题)
- 计算机网络 (7题)
- 操作系统 (2题)

**编程语言** (85题)
- Go语言 (85题)

**数据库** (153题)
- MySQL (55题)
- Redis (94题)
- MongoDB (4题)

**消息队列** (40题)
- Kafka (40题)

**后端组件** (81题)
- Docker (59题)
- Nginx (10题)
- Elasticsearch (12题)

**架构设计** (229题)
- 系统设计 (189题)
- 分布式系统 (21题)
- 微服务 (19题)

**项目经历** (3题)

## 🚀 快速开始

```bash
# 1. 克隆项目
git clone https://github.com/1708737115/Interview-agent.git
cd Interview-agent

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 填入 GLM4_API_KEY

# 3. 选择题库配置
cp question_bank_light.json question_bank.json

# 4. 启动服务
docker-compose up -d

# 5. 访问
# 前端: http://localhost:3000
# API文档: http://localhost:8000/docs
```

## 📝 配置文件

### .env (必需)
```bash
GLM4_API_KEY=your_api_key_here
```

### docker-compose.yml
- 服务: backend, frontend, postgres, chromadb
- 端口: 3000(前端), 8000(后端), 5432(数据库), 8001(向量库)

### 环境变量
- `DATABASE_URL`: 数据库连接
- `CHROMA_DB_PATH`: 向量数据库路径
- `UPLOAD_DIR`: 上传文件目录

## 🧹 清理的文件

本次清理删除了以下不必要的文件：
- ❌ `extract_questions*.py` (4个临时提取脚本)
- ❌ `raw_text.txt` (临时文本)
- ❌ `extracted_questions.json` (中间产物)
- ❌ `__pycache__/` 和 `*.pyc` (Python缓存)
- ❌ `*.log` 文件 (日志文件)
- ❌ `backend/test_*.py` (测试文件)
- ❌ `uploads/*` (测试上传文件)

## 📊 项目统计

- **代码文件**: 30+ 个
- **题库题目**: 641+ 道
- **支持分类**: 7大类, 15+子类
- **Docker服务**: 4个
- **文档**: 6篇

## 🔗 相关链接

- GitHub: https://github.com/1708737115/Interview-agent
- Docker Hub: (待添加)
- 问题反馈: GitHub Issues
