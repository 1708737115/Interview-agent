# 后端面试题知识库

基于GitHub开源面试题仓库构建的向量化知识库，支持语义检索和智能面试。

## 📁 文件结构

```
backend/app/knowledge_base/
├── github_sync.py           # GitHub数据同步
├── markdown_parser.py       # Markdown解析器
├── llm_enhancer.py          # LLM增强处理
├── vector_store.py          # 向量数据库存储
├── build_knowledge_base.py  # 主构建流程
└── __init__.py
```

## 🚀 快速开始

### 1. 配置环境变量

在 `.env` 文件中配置：
```bash
GLM4_API_KEY=your_api_key_here
GLM4_MODEL=glm-4-air
GLM4_EMBEDDING_MODEL=embedding-2
```

### 2. 构建知识库

```bash
# 快速测试（处理10题）
cd backend
PYTHONPATH=app python3 app/knowledge_base/build_knowledge_base.py test

# 完整构建
PYTHONPATH=app python3 app/knowledge_base/build_knowledge_base.py build

# 仅更新（不重新同步GitHub）
PYTHONPATH=app python3 app/knowledge_base/build_knowledge_base.py update
```

### 3. 数据存储位置

- **原始仓库**: `backend/data/repos/`
- **处理后数据**: `backend/data/processed/enhanced_questions.json`
- **向量数据库**: `backend/data/chroma_db/`
- **同步状态**: `backend/data/sync_state.json`

## 📊 知识库统计

当前支持的后端面试题分类：

| 分类 | 说明 | 主要来源 |
|------|------|---------|
| Go | Go语言面试题 | yongxinz/gopher, go-interview |
| MySQL | 数据库面试题 | backend-interview |
| Redis | 缓存面试题 | backend-interview |
| Network | 计算机网络 | backend-interview, go-interview |
| System | 操作系统 | go-interview |
| System-Design | 系统设计 | backend-interview |

## 🔄 自动化同步

系统支持每周自动同步GitHub仓库：

1. **核心仓库**（自动同步）
   - backend-interview
   - go-interview
   - gopher

2. **新仓库发现**（可选）
   - 每周搜索GitHub热门面试题仓库
   - 自动识别并评估新仓库质量

3. **数据更新策略**
   - 增量更新：只处理新增和修改的内容
   - 缓存机制：LLM处理结果缓存，避免重复调用
   - 去重：基于问题文本相似度去重

## 🧪 测试

```bash
# 运行解析器测试
PYTHONPATH=app python3 test_knowledge_base.py
```

## 📈 LLM增强功能

每个问题经过LLM处理后包含：

1. **知识点标签**（3-5个）
2. **难度评估**（1-5级）
3. **追问点识别**（2-3个）
4. **向量表示**（用于语义检索）

## 🔍 使用向量库

```python
from app.knowledge_base.vector_store import get_vector_store
from app.services.llm_service import GLM4Service

# 获取向量库实例
store = get_vector_store()

# 搜索相似问题
llm = GLM4Service()
query_embedding = await llm.generate_embedding("goroutine原理")
results = store.search_similar(query_embedding, n_results=5)

# 按分类获取
questions = store.get_by_category("go", limit=10)
```

## 📋 下一步计划

1. [ ] 运行完整知识库构建（配置API Key后）
2. [ ] 实现牛客面试风格学习模块
3. [ ] 开发LLM简历解析服务
4. [ ] 构建InterviewerAgent（45分钟面试流程）
5. [ ] 前端面试界面开发

## 📝 数据来源

### GitHub仓库

- [backend-interview](https://github.com/yongxinz/backend-interview) - 后端面试题汇总
- [go-interview](https://github.com/2637309949/go-interview) - Go面试题集合
- [gopher](https://github.com/yongxinz/gopher) - Go学习路线图

### 使用协议

所有数据均来自开源项目，遵循原项目许可证（MIT）。

---

**注意**: 首次运行需要配置GLM-4 API Key，用于LLM增强和向量化。
