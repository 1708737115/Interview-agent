# Docker 部署指南

## 🐳 快速开始

### 1. 环境准备

确保已安装：
- Docker Engine 20.10+
- Docker Compose 2.0+

```bash
# 检查版本
docker --version
docker-compose --version
```

### 2. 配置环境变量

复制环境变量模板并配置：

```bash
cd /home/fengxu/mylib/interview-agent/backend
cp .env.example .env
```

编辑 `.env` 文件：
```env
# GLM-4 API Configuration (必需)
GLM4_API_KEY=your_api_key_here
GLM4_MODEL=glm-4-air
GLM4_EMBEDDING_MODEL=embedding-3
GLM4_BASE_URL=https://open.bigmodel.cn/api/paas/v4

# Database Configuration
DATABASE_URL=postgresql://interview_agent:interview_agent_pass@postgres:5432/interview_agent

# ChromaDB Configuration
CHROMA_DB_PATH=/app/chroma_db

# App Settings
APP_NAME=Interview Agent
DEBUG=False
SECRET_KEY=your_secret_key_here

# LLM Configuration
MAX_TOKENS=4096
TEMPERATURE=0.7
```

### 3. 准备数据

确保知识库数据已生成：

```bash
# 检查知识库文件是否存在
ls -lh backend/data/processed/enhanced_questions.json

# 如果不存在，运行构建脚本
cd backend
python3 build_kb.py
```

### 4. 启动服务

使用 Docker Compose 一键启动：

```bash
cd /home/fengxu/mylib/interview-agent

# 构建并启动所有服务
docker-compose up -d --build

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 5. 访问应用

- **前端界面**: http://localhost:3000
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs

---

## 🏗️ 服务架构

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

---

## 📁 数据持久化

Docker Compose 配置了以下数据卷：

| 卷名 | 路径 | 说明 |
|------|------|------|
| `postgres_data` | `/var/lib/postgresql/data` | PostgreSQL数据 |
| `chroma_data` | `/chroma/chroma` | ChromaDB向量数据 |
| `./backend/data` | `/app/data` | 面试题知识库 |
| `./backend/uploads` | `/app/uploads` | 上传的简历文件 |

---

## 🔧 常用命令

### 启动/停止服务

```bash
# 启动所有服务
docker-compose up -d

# 停止所有服务
docker-compose down

# 停止并删除数据卷（谨慎使用！）
docker-compose down -v

# 重启服务
docker-compose restart

# 重启单个服务
docker-compose restart backend
```

### 查看日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend

# 查看最近100行日志
docker-compose logs --tail=100 backend
```

### 进入容器

```bash
# 进入后端容器
docker-compose exec backend bash

# 进入前端容器
docker-compose exec frontend sh

# 进入数据库容器
docker-compose exec postgres psql -U interview_agent -d interview_agent
```

### 更新部署

```bash
# 拉取最新代码后重新构建
docker-compose down
docker-compose up -d --build

# 仅更新代码（不重新构建镜像）
docker-compose restart
```

---

## 🌐 生产环境部署

### 1. 使用外部数据库

修改 `docker-compose.yml`，使用外部PostgreSQL：

```yaml
services:
  backend:
    environment:
      - DATABASE_URL=postgresql://user:password@your-db-host:5432/interview_agent
    # 移除 depends_on postgres
```

### 2. 配置HTTPS

使用 Traefik 或 Nginx Proxy Manager：

```yaml
services:
  traefik:
    image: traefik:v2.10
    command:
      - "--api.insecure=true"
      - "--providers.docker=true"
      - "--entrypoints.websecure.address=:443"
      - "--certificatesresolvers.letsencrypt.acme.tlschallenge=true"
      - "--certificatesresolvers.letsencrypt.acme.email=your@email.com"
      - "--certificatesresolvers.letsencrypt.acme.storage=/letsencrypt/acme.json"
    ports:
      - "443:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ./letsencrypt:/letsencrypt

  frontend:
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.frontend.rule=Host(`your-domain.com`)"
      - "traefik.http.routers.frontend.tls.certresolver=letsencrypt"
      - "traefik.http.routers.frontend.entrypoints=websecure"
```

### 3. 配置环境变量

创建 `.env.production`：

```env
# 生产环境配置
DEBUG=False
SECRET_KEY=your_strong_secret_key
GLM4_API_KEY=your_production_api_key

# 数据库（使用外部数据库）
DATABASE_URL=postgresql://user:pass@db.example.com:5432/interview_agent

# 日志级别
LOG_LEVEL=INFO
```

### 4. 使用 Docker Swarm

```bash
# 初始化 Swarm
docker swarm init

# 部署 Stack
docker stack deploy -c docker-compose.yml interview-agent

# 查看服务
docker stack ps interview-agent
```

---

## 🐛 故障排查

### 问题1: 端口冲突

**现象**: `bind: address already in use`

**解决**:
```bash
# 查找占用端口的进程
lsof -i :3000
lsof -i :8000
lsof -i :5432

# 停止占用端口的进程
kill -9 <PID>

# 或修改 docker-compose.yml 使用其他端口
```

### 问题2: 数据库连接失败

**现象**: `Connection refused` 或 `Database connection failed`

**解决**:
```bash
# 检查数据库容器状态
docker-compose ps postgres

# 查看数据库日志
docker-compose logs postgres

# 检查网络连接
docker-compose exec backend ping postgres

# 重新初始化数据库
docker-compose down -v
docker-compose up -d postgres
sleep 10  # 等待数据库启动
docker-compose up -d backend
```

### 问题3: 前端无法连接后端

**现象**: API 请求 404 或 502

**解决**:
```bash
# 检查后端服务状态
docker-compose ps backend

# 查看后端日志
docker-compose logs backend

# 测试后端API
curl http://localhost:8000/api/health

# 进入前端容器检查网络
docker-compose exec frontend wget -O- http://backend:8000/api/health
```

### 问题4: 知识库数据缺失

**现象**: 面试时没有题目

**解决**:
```bash
# 检查数据文件是否存在
docker-compose exec backend ls -lh /app/data/processed/

# 从宿主机复制数据
docker cp backend/data/processed/enhanced_questions.json interview-agent-backend:/app/data/processed/

# 或重新构建数据
docker-compose exec backend python3 build_kb.py
```

### 问题5: GLM-4 API 调用失败

**现象**: `API call failed` 或超时

**解决**:
```bash
# 检查API Key
docker-compose exec backend cat /app/.env | grep GLM4

# 测试API连通性
docker-compose exec backend python3 -c "
import requests
response = requests.get('https://open.bigmodel.cn/api/paas/v4/models')
print(response.status_code)
"

# 检查日志
docker-compose logs backend | grep -i error
```

---

## 📊 监控和维护

### 查看资源使用

```bash
# 查看容器资源使用
docker stats

# 查看磁盘使用
docker system df

# 清理未使用的数据
docker system prune -a
```

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

### 自动重启策略

所有服务已配置 `restart: unless-stopped`，系统重启后会自动启动。

如需在系统启动时自动运行：

```bash
# 启用 Docker 服务自启动
sudo systemctl enable docker

# 或使用 systemd 管理
cat > /etc/systemd/system/interview-agent.service << EOF
[Unit]
Description=Interview Agent
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/fengxu/mylib/interview-agent
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable interview-agent
sudo systemctl start interview-agent
```

---

## 📝 配置参考

### 环境变量完整列表

```env
# === API 配置 ===
GLM4_API_KEY=your_api_key
GLM4_MODEL=glm-4-air
GLM4_EMBEDDING_MODEL=embedding-3
GLM4_BASE_URL=https://open.bigmodel.cn/api/paas/v4

# === 数据库配置 ===
DATABASE_URL=postgresql://user:password@host:5432/db_name

# === 应用配置 ===
APP_NAME=Interview Agent
APP_VERSION=1.0.0
DEBUG=False
SECRET_KEY=your_secret_key
LOG_LEVEL=INFO

# === LLM 配置 ===
MAX_TOKENS=4096
TEMPERATURE=0.7
TOP_K_RETRIEVAL=5
SIMILARITY_THRESHOLD=0.7

# === 面试配置 ===
INTERVIEW_DURATION=45
MAX_FOLLOWUPS=8
```

---

## ✅ 部署检查清单

- [ ] Docker 和 Docker Compose 已安装
- [ ] `.env` 文件已配置并包含 GLM4_API_KEY
- [ ] 知识库数据文件已存在
- [ ] 端口 3000, 8000, 5432, 8001 未被占用
- [ ] 有足够的磁盘空间 (>2GB)
- [ ] 网络可以访问 GLM-4 API
- [ ] 防火墙允许外部访问 (生产环境)

---

**完成部署后，访问 http://localhost:3000 开始使用！**
