# 面试题库配置选择

本系统提供多种题库配置，您可以根据实际需求选择合适的版本。

## 📦 可用配置文件

### 1. question_bank_light.json (推荐新手)
- **题目数量**: 217 道
- **文件大小**: 约 80KB
- **适用场景**: 快速体验、测试部署、资源受限环境
- **包含内容**: 
  - 计算机基础（Linux、网络）
  - Go语言（精选高频题目）
  - 数据库（MySQL、Redis核心题目）
  - 后端组件（Docker、Nginx）
  - 系统设计（经典场景）

### 2. question_bank_config.json (推荐生产)
- **题目数量**: 641 道
- **文件大小**: 约 300KB
- **适用场景**: 生产环境、正式面试
- **特点**: 
  - 题目覆盖面广
  - 包含追问题目
  - 难度分级完整

### 3. question_bank_index.json (高级)
- **题目数量**: 无（仅索引）
- **适用场景**: 大规模部署、自定义题库管理
- **特点**: 
  - 需要配合分文件存储使用
  - 可按需加载分类
  - 便于团队协作维护

## 🔧 使用方法

### 快速开始（使用轻量版）

```bash
# 1. 复制轻量版配置为默认配置
cp question_bank_light.json question_bank.json

# 2. 启动服务
docker-compose up -d
```

### 自定义配置

1. 选择基础配置文件：
   ```bash
   # 使用完整版
   cp question_bank_config.json question_bank.json
   
   # 或使用轻量版
   cp question_bank_light.json question_bank.json
   ```

2. 编辑 `question_bank.json`，根据需要启用/禁用分类：
   ```json
   {
     "groups": {
       "languages": {
         "enabled": true,  // 启用编程语言类
         "categories": {
           "language_go": {
             "enabled": true   // 启用Go语言题目
           }
         }
       }
     }
   }
   ```

3. 重启服务生效：
   ```bash
   docker-compose restart
   ```

## 📊 分类说明

### 计算机基础 (50题)
- **Linux**: 常用命令、进程管理、文件系统
- **计算机网络**: TCP/IP、HTTP、网络模型
- **操作系统**: 进程线程、内存管理、调度算法

### 编程语言 (85题)
- **Go语言**: goroutine、channel、GC、并发模型

### 数据库 (153题)
- **MySQL**: 索引、事务、锁、优化、主从复制
- **Redis**: 数据类型、持久化、集群、缓存策略
- **MongoDB**: 文档存储、索引、分片

### 消息队列 (40题)
- **Kafka**: 架构、分区、消费顺序、消息不丢失

### 后端组件 (81题)
- **Docker**: 容器、镜像、Dockerfile、编排
- **Nginx**: 负载均衡、反向代理、高并发
- **Elasticsearch**: 搜索引擎、分词、集群

### 架构设计 (229题)
- **微服务**: 服务拆分、治理、DDD
- **分布式系统**: CAP理论、分布式锁、事务
- **系统设计**: 秒杀、短链接、IM、排行榜等

### 项目经历 (3题)
- 项目深挖、性能优化、故障处理

## 🎯 推荐配置方案

### 方案一：后端开发标准版
适用：中级后端工程师面试

启用的分类：
- ✅ Go语言
- ✅ MySQL、Redis
- ✅ Kafka
- ✅ Docker、Nginx
- ✅ Linux、网络
- ✅ 微服务、分布式系统
- ✅ 系统设计

预计题目：400-450道

### 方案二：校招/初级版
适用：应届生、初级工程师

启用的分类：
- ✅ Go语言
- ✅ MySQL、Redis（基础题）
- ✅ Linux、网络、操作系统
- ⏭️ 跳过：架构设计（难度较高，建议有工作经验后再学）
- ⏭️ 跳过：系统设计（需要实际项目经验支撑）

预计题目：200-250道

> 💡 **说明**：校招/初级面试通常重点考察基础知识和编程能力，架构设计和系统 design 类题目难度较高，建议暂不启用。当然，如果你有余力，也可以开启学习。

### 方案三：架构师高级版
适用：高级工程师、架构师

启用的分类：
- ✅ 全部启用
- ✅ 重点：系统设计、分布式系统、微服务

预计题目：600+道

## 📝 自定义题库

### 添加新题目

在对应分类的 `questions` 数组中添加：

```json
{
  "id": "custom-001",
  "text": "你的自定义题目",
  "category": "database_mysql",
  "difficulty": 3,
  "type": "technical"
}
```

### 添加新分类

1. 在 `groups` 中添加新大类：
   ```json
   "machine_learning": {
     "name": "机器学习",
     "description": "机器学习算法和应用",
     "enabled": true,
     "categories": {
       "ml_basic": {
         "name": "机器学习基础",
         "enabled": true,
         "count": 0,
         "questions": []
       }
     }
   }
   ```

2. 在 `skillKeywords` 中添加技能关键词映射（如果使用自动筛选）

## ⚙️ 配置项说明

### Group（大类）配置

```json
{
  "name": "显示名称",
  "description": "描述说明",
  "enabled": true,  // 是否启用整个大类
  "categories": { ... }  // 子分类
}
```

### Category（分类）配置

```json
{
  "name": "显示名称",
  "enabled": true,  // 是否启用该分类
  "count": 50,      // 题目数量
  "questions": [    // 题目列表
    {
      "id": "唯一标识",
      "text": "题目内容",
      "category": "分类标识",
      "difficulty": 3,  // 难度 1-5
      "type": "technical"  // 类型：technical/design/project
    }
  ]
}
```

### Question（题目）配置

- **id**: 唯一标识符，格式建议 `分类-序号`
- **text**: 题目文本，建议长度 20-150 字符
- **category**: 所属分类标识
- **difficulty**: 难度等级
  - 1-2: 简单（基础概念）
  - 3: 中等（原理理解）
  - 4-5: 困难（深入分析/设计）
- **type**: 题目类型
  - `technical`: 技术问答
  - `design`: 系统设计
  - `project`: 项目深挖

## 🔍 常见问题

### Q: 如何知道某个分类有多少题目？
查看配置文件中的 `count` 字段，或使用以下命令：
```bash
python3 -c "import json; d=json.load(open('question_bank.json')); print(sum(c.get('count',0) for g in d['groups'].values() for c in g['categories'].values()))"
```

### Q: 修改配置后需要重启吗？
是的，修改 `question_bank.json` 后需要重启后端服务：
```bash
docker-compose restart backend
```

### Q: 可以多个配置文件切换吗？
可以，建议保留多个配置文件，需要时复制为 `question_bank.json`：
```bash
cp question_bank_config.json question_bank.json
docker-compose restart
```

### Q: 题目太多会影响性能吗？
不会，系统会按需加载。但配置文件过大可能影响启动速度，建议使用轻量版或索引版。

## 📚 相关文档

- [QUESTION_BANK_GUIDE.md](QUESTION_BANK_GUIDE.md) - 详细配置指南
- [README.md](README.md) - 项目主文档

---

**提示**: 首次部署建议选择 `question_bank_light.json`，确认系统正常运行后再根据需要切换到完整版。
