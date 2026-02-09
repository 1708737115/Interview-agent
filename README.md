# AI 智能面试官 (Interview Agent)

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11-blue.svg" alt="Python 3.11">
  <img src="https://img.shields.io/badge/React-18.2-blue.svg" alt="React 18.2">
  <img src="https://img.shields.io/badge/FastAPI-0.104-green.svg" alt="FastAPI">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT">
</p>

基于大语言模型(GLM-4)的本地部署面试 Agent 系统，支持知识库构建、简历解析、智能面试模拟和实事求是的面试评估。

## ✨ 核心特性

### 🤖 智能面试引擎
- **海量题库**: **641+** 道大厂后端面试真题，涵盖 Go、MySQL、Redis、Docker、微服务、分布式系统等
- **动态题库系统**: 根据简历技能栈智能筛选相关技术题目，支持自定义启用/禁用分类
- **多维度评估**: 基于回答长度、技术术语、逻辑解释、代码示例等自动评分
- **实事求是评价**: 面试结束后提供客观、直接、有针对性的反馈，指出具体问题和改进方向
- **追问机制**: 50%概率触发深度追问，考察技术理解深度

### 📝 简历解析与编辑
- **智能解析**: 自动提取姓名、联系方式、工作经验、技能栈等信息
- **可视化编辑**: 支持修改基本信息和工作经历(Markdown编辑器)
- **技能匹配**: 根据技能栈自动匹配相关面试题目

### 🎯 多种面试模式
- **预设面试类型**: 后端开发、Go专项、Java专项、考研复试、校招面试
- **DIY面试官**: 自定义面试官风格、考察领域、面试时长
- **系统流程**: 选择面试 → 上传简历 → 智能面试 → 查看报告

### 🔄 完整导航体验
- **面包屑导航**: 树状层级结构，清晰展示页面关系
- **URL路由**: 支持浏览器前进/后退，刷新页面不丢失状态
- **本地存储**: 自动保存页面状态，支持断点续面

## 🚀 快速开始

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
cp .env.example .env
# 编辑 .env 文件，填入必需的 API 密钥

# 3. 启动服务
docker-compose up -d

# 4. 选择题库配置（可选）
# 我们提供多种题库配置，根据需求选择：
cp question_bank_light.json question_bank.json  # 轻量版（217题，推荐新手）
# 或
cp question_bank_config.json question_bank.json  # 完整版（641题，推荐生产）

# 5. 访问系统
# 前端: http://localhost:3000
# 后端API文档: http://localhost:8000/docs
```

### 方法二：本地开发环境

#### 后端启动

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

#### 前端启动

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 访问 http://localhost:5173
```

## 📋 配置说明

### 必需配置
在 `.env` 文件中配置以下 API 密钥：

```bash
# 智谱 AI GLM-4 API Key (必需)
# 获取地址: https://open.bigmodel.cn/usercenter/apikeys
GLM4_API_KEY=your_glm4_api_key_here

# LlamaParse API Key (可选，用于PDF解析)
# 获取地址: https://cloud.llamaindex.ai/api-key
LLAMAPARSE_API_KEY=your_llamaparse_api_key_here
```

### 可选配置

```bash
# 数据库配置
DATABASE_URL=postgresql://user:password@localhost:5432/interview_db

# 向量数据库
CHROMA_DB_PATH=./chroma_db

# 文件上传路径
UPLOAD_DIR=./uploads
```

## 🏗️ 项目架构

```
interview-agent/
├── backend/                    # FastAPI 后端
│   ├── app/
│   │   ├── api/               # API 路由层
│   │   │   └── routes/
│   │   │       ├── interview.py
│   │   │       └── knowledge_base.py
│   │   ├── core/              # 核心配置
│   │   ├── models/            # 数据模型
│   │   ├── services/          # 业务逻辑
│   │   │   ├── interviewer_agent.py    # 面试官Agent
│   │   │   ├── llm_service.py          # LLM服务
│   │   │   ├── resume_analyzer.py      # 简历解析
│   │   │   └── interview_service.py    # 面试服务
│   │   └── knowledge_base/    # 知识库模块
│   ├── data/                  # 数据文件
│   ├── chroma_db/            # 向量数据库
│   └── requirements.txt
├── frontend/                  # React 前端
│   ├── src/
│   │   ├── pages/            # 页面组件
│   │   │   ├── Home.tsx
│   │   │   ├── InterviewSetup.tsx
│   │   │   ├── Interview.tsx
│   │   │   └── Report.tsx
│   │   └── App.tsx
│   └── package.json
├── docker-compose.yml        # Docker 编排配置
├── deploy.sh                 # 部署脚本
└── README.md
```

## 🎨 功能详细介绍

### 1. 动态题库系统
- **题目库**: 30+ 道技术面试题，涵盖 Go、MySQL、Redis、系统设计等
- **智能筛选**: 根据简历技能栈自动筛选相关题目
- **随机抽取**: 每次面试题目顺序和组合都不同
- **难度匹配**: 根据工作年限自动匹配系统设计题难度

### 2. 实事求是评价机制
- **即时评估**: 根据回答长度、技术术语、逻辑性自动评分(0-100分)
- **问题诊断**: 
  - 回答过短 → 指出具体哪个问题
  - 缺少技术术语 → 说明缺少哪些关键词
  - 深度不够 → 建议从哪些角度补充
- **综合评价**: 直接指出技术能力是否达标，是否需要继续准备
- **具体建议**: 针对不同技术领域给出学习资料推荐

### 3. 面试流程
1. **首页**: 选择预设面试类型或DIY面试官
2. **上传简历**: 拖拽PDF/DOCX文件，自动解析信息
3. **确认信息**: 查看解析结果，支持编辑修改
4. **智能面试**: 与AI面试官对话答题
5. **查看报告**: 查看详细评分和评价

### 4. 技术亮点
- **URL路由**: 使用 React Router 实现前端路由，支持浏览器前进后退
- **状态持久化**: localStorage 自动保存页面状态
- **动态评分**: 多维度算法评估回答质量
- **Markdown编辑**: 支持富文本编辑工作经历
- **响应式设计**: 适配桌面和移动端

## 🔧 开发计划

- [x] 动态题库系统
- [x] 实事求是的评价机制
- [x] URL路由和面包屑导航
- [x] 本地状态持久化
- [ ] 接入真实 LLM API
- [ ] 支持更多编程语言
- [ ] 面试记录历史查询
- [ ] 视频面试模式

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目基于 [MIT](LICENSE) 许可证开源。

## 🙏 致谢

- [智谱 AI](https://open.bigmodel.cn/) - 提供 GLM-4 大语言模型
- [FastAPI](https://fastapi.tiangolo.com/) - 高性能 Web 框架
- [React](https://react.dev/) - 前端 UI 框架
- [ChromaDB](https://www.trychroma.com/) - 向量数据库

## 📞 联系方式

- GitHub: [@1708737115](https://github.com/1708737115)
- 项目地址: https://github.com/1708737115/Interview-agent

---

<p align="center">Made with ❤️ for better technical interviews</p>
