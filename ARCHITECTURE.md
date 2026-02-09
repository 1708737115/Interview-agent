# 智能面试官系统架构文档

## 📋 项目概览

基于知识库+LLM的后端面试模拟系统，支持简历解析、个性化面试、智能追问、综合评估。

---

## 🏗️ 系统架构

```
用户层                    API层                  服务层                    数据层
┌─────────┐             ┌─────────────┐        ┌─────────────────┐     ┌──────────────┐
│  前端    │ ─────────── │  FastAPI    │ ────── │ InterviewerAgent │ ── │  面试题知识库  │
│ (React) │             │   Routes    │        │    (核心Agent)   │     │  (ChromaDB)  │
└─────────┘             └─────────────┘        └─────────────────┘     └──────────────┘
                              │                           │
                              │                    ┌──────┴───────┐
                              │                    │              │
                              ▼                    ▼              ▼
                        ┌──────────────┐    ┌────────────┐  ┌────────────┐
                        │ ResumeParser │    │ 风格配置器  │  │ 简历解析器  │
                        │ (简历上传)   │    │(牛客风格)  │  │(LLM解析)   │
                        └──────────────┘    └────────────┘  └────────────┘
```

---

## 📁 项目结构

```
interview-agent/
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI入口
│   │   ├── core/
│   │   │   └── config.py             # 配置管理
│   │   ├── api/
│   │   │   └── routes/
│   │   │       └── interview.py      # API路由
│   │   ├── services/                 # 核心服务
│   │   │   ├── llm_service.py        # GLM-4服务封装
│   │   │   ├── interview_service.py  # 面试引擎（旧）
│   │   │   ├── resume_analyzer.py    # 简历解析器 ✅ NEW
│   │   │   └── document_service.py   # 文档处理
│   │   ├── knowledge_base/           # 知识库模块 ✅ NEW
│   │   │   ├── github_sync.py        # GitHub数据同步
│   │   │   ├── markdown_parser.py    # Markdown解析
│   │   │   ├── llm_enhancer.py       # LLM增强处理
│   │   │   ├── vector_store.py       # 向量数据库存储
│   │   │   ├── build_knowledge_base.py # 主构建流程
│   │   │   ├── nowcoder_style_learning.py # 牛客风格学习 ✅ NEW
│   │   │   └── style_config_loader.py # 风格配置加载 ✅ NEW
│   │   └── models/                   # 数据模型
│   │       ├── schemas.py
│   │       └── database.py
│   ├── data/                         # 数据存储
│   │   ├── repos/                    # GitHub仓库镜像
│   │   │   ├── backend-interview/
│   │   │   ├── go-interview/
│   │   │   └── gopher/
│   │   ├── processed/                # 处理后数据
│   │   │   └── enhanced_questions.json  # 面试题知识库
│   │   ├── nowcoder/                 # 牛客数据 ✅ NEW
│   │   │   └── interviewer_style_config.json # 风格配置
│   │   ├── chroma_db/                # 向量数据库
│   │   └── cache/                    # LLM缓存
│   └── build_kb.py                   # 简化版构建脚本 ✅ NEW
├── frontend/                         # React前端
└── docker-compose.yml
```

---

## 🎯 核心模块详解

### 1️⃣ 知识库模块 (knowledge_base/)

| 文件 | 功能 | 状态 |
|------|------|------|
| `github_sync.py` | 自动同步GitHub面试题仓库 | ✅ |
| `markdown_parser.py` | 解析Markdown提取问答对 | ✅ |
| `llm_enhancer.py` | LLM增强（标签/难度/追问点） | ✅ |
| `vector_store.py` | ChromaDB向量存储和检索 | ✅ |
| `build_knowledge_base.py` | 完整构建流程 | ✅ |
| `nowcoder_style_learning.py` | 牛客风格学习和分析 | ✅ |
| `style_config_loader.py` | 风格配置管理 | ✅ |

**数据流:**
```
GitHub仓库 → Markdown解析 → LLM增强 → 向量存储 → ChromaDB
```

**当前数据:**
- 已同步仓库: backend-interview, go-interview, gopher
- 面试题数量: ~749题（构建中）
- 增强字段: 标签、难度(1-5)、追问点
- 分类: Go, MySQL, Redis, Network, System

---

### 2️⃣ 简历解析服务 (services/resume_analyzer.py)

**功能:**
1. **文本提取**: 支持PDF/DOCX/TXT
2. **结构化提取**: 使用LLM提取关键信息
3. **能力评估**: 评估等级/年限/优势/缺口
4. **策略生成**: 生成个性化面试方案

**输出示例:**
```json
{
  "name": "张三",
  "education": [{"school": "北京大学", "major": "计算机"}],
  "work_experience": [{"company": "字节跳动", "position": "后端开发"}],
  "skills": {
    "programming_languages": ["Go", "Java"],
    "databases": ["MySQL", "Redis"]
  },
  "estimated_level": "中级",
  "years_of_experience": 3.5,
  "interview_strategy": {
    "focus_areas": ["Go语言", "MySQL", "Redis"],
    "difficulty_adjustment": "正常"
  }
}
```

---

### 3️⃣ 面试官风格配置 (data/nowcoder/)

**配置文件:** `interviewer_style_config.json`

**面试流程:**
```
开场破冰(3分钟) → 技术基础(20分钟) → 项目深挖(12分钟) → 场景设计(8分钟) → 总结反馈(2分钟)
```

**追问策略:**
- 最大追问: 8次
- 深度追问(35%): 考察原理和机制
- 补充追问(30%): 完善回答内容
- 纠错追问(20%): 温和纠正错误
- 场景追问(15%): 实际应用考察

**提问风格:**
- 直接式(60%): "介绍一下X的原理"
- 引导式(40%): "你怎么看X的设计？"

---

## 🔄 面试流程架构

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
┌─────────────────┐
│ InterviewerAgent │
│ - 加载候选人信息 │
│ - 加载风格配置  │
│ - 初始化知识库  │
└─────────────────┘
    │
    ▼
开始面试 (45分钟)
    │
    ├── 开场破冰 (3分钟)
    │
    ├── 技术基础面试 (20分钟)
    │   ├── 根据策略选择知识点
    │   ├── 生成个性化问题
    │   ├── 评估回答质量
    │   └── 智能追问 (最多8次)
    │
    ├── 项目深挖 (12分钟)
    │   ├── 选择核心项目
    │   ├── 技术选型追问
    │   └── 架构设计讨论
    │
    ├── 场景设计 (8分钟)
    │   ├── 固定题库 或 动态生成
    │   └── 开放讨论
    │
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

## 💾 数据存储

### 1. 面试题知识库
- **位置:** `data/processed/enhanced_questions.json`
- **格式:** JSON
- **内容:** 749+面试题，包含标签、难度、追问点

### 2. 向量数据库
- **位置:** `data/chroma_db/`
- **技术:** ChromaDB
- **用途:** 语义检索、相似问题推荐

### 3. 风格配置
- **位置:** `data/nowcoder/interviewer_style_config.json`
- **用途:** 面试官人设、话术模板、追问策略

### 4. LLM缓存
- **位置:** `data/cache/`
- **用途:** 避免重复调用API，降低成本

---

## 🚀 部署和使用

### 1. 环境配置
```bash
# 创建.env文件
GLM4_API_KEY=your_api_key
GLM4_MODEL=glm-4-air
GLM4_EMBEDDING_MODEL=embedding-3
```

### 2. 构建知识库
```bash
cd backend
python3 build_kb.py --limit 50   # 快速测试
python3 build_kb.py              # 完整构建
```

### 3. 启动服务
```bash
# 启动后端
cd backend
uvicorn app.main:app --reload

# 启动前端
cd frontend
npm run dev
```

---

## 📊 当前进度

| 模块 | 状态 | 完成度 |
|------|------|--------|
| 知识库构建 | ✅ | 749题构建中(36%) |
| 简历解析 | ✅ | 100% |
| 风格配置 | ✅ | 100% |
| InterviewerAgent | ⏳ | 待开发 |
| 前端界面 | ⏳ | 待改造 |
| API接口 | ⏳ | 待更新 |

---

## 🎯 下一步计划

1. **InterviewerAgent核心**
   - 45分钟流程控制器
   - 混合追问策略引擎
   - 实时评估打分
   - 对话状态管理

2. **前端界面**
   - 简历上传页面
   - 面试对话界面
   - 面试报告展示

3. **API接口**
   - 面试会话管理
   - 简历解析接口
   - 评估报告接口

---

## 💡 关键设计决策

1. **混合追问策略**
   - 前15分钟：保守策略（建立信心）
   - 中间20分钟：根据表现动态切换
   - 后10分钟：保守策略（平稳收尾）

2. **知识库来源**
   - GitHub开源面试题（核心）
   - 每周自动同步更新
   - LLM增强处理

3. **简历解析**
   - LLM深度解析（而非规则）
   - 缓存机制降低成本
   - 生成个性化面试策略

4. **评估体系**
   - 多维度：技术深度、广度、问题解决、沟通、项目经验
   - 实时打分 + 最终报告
   - 对标大厂面试标准

---

这个架构设计满足你的需求吗？有什么需要调整的地方？
