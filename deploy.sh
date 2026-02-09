#!/bin/bash
# Docker 快速部署脚本

set -e

echo "========================================"
echo "  Interview Agent Docker 部署脚本"
echo "========================================"
echo ""

# 检查 Docker 和 Docker Compose
echo "[1/5] 检查 Docker 环境..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose 未安装"
    exit 1
fi

echo "✅ Docker 版本: $(docker --version)"
echo "✅ Docker Compose 版本: $(docker-compose --version)"
echo ""

# 检查环境变量
echo "[2/5] 检查环境变量..."
if [ ! -f backend/.env ]; then
    echo "⚠️  未找到 backend/.env 文件"
    echo "请创建 .env 文件并配置 GLM4_API_KEY"
    echo ""
    echo "示例配置:"
    cat > backend/.env.example << 'EOF'
# GLM-4 API Configuration
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
APP_VERSION=1.0.0
DEBUG=False
SECRET_KEY=your_secret_key_here

# LLM Configuration
MAX_TOKENS=4096
TEMPERATURE=0.7
EOF
    echo ""
    echo "已创建 backend/.env.example 模板文件"
    echo "请运行: cp backend/.env.example backend/.env"
    echo "然后编辑 backend/.env 添加你的 GLM4_API_KEY"
    exit 1
fi

if ! grep -q "GLM4_API_KEY" backend/.env; then
    echo "❌ .env 文件缺少 GLM4_API_KEY"
    exit 1
fi

echo "✅ 环境变量已配置"
echo ""

# 检查知识库数据
echo "[3/5] 检查知识库数据..."
if [ ! -f "backend/data/processed/enhanced_questions.json" ]; then
    echo "⚠️  未找到知识库数据文件"
    echo "请先构建知识库:"
    echo "  cd backend"
    echo "  pip install -r requirements.txt"
    echo "  python3 build_kb.py"
    exit 1
fi

QUESTION_COUNT=$(wc -l < backend/data/processed/enhanced_questions.json)
echo "✅ 知识库数据已准备 ($QUESTION_COUNT 行数据)"
echo ""

# 检查端口
echo "[4/5] 检查端口占用..."
PORTS=("3000" "8000" "5432" "8001")
PORT_AVAILABLE=true

for PORT in "${PORTS[@]}"; do
    if lsof -i :$PORT > /dev/null 2>&1; then
        echo "⚠️  端口 $PORT 已被占用"
        PORT_AVAILABLE=false
    else
        echo "✅ 端口 $PORT 可用"
    fi
done

if [ "$PORT_AVAILABLE" = false ]; then
    echo ""
    echo "请释放被占用的端口，或修改 docker-compose.yml 使用其他端口"
    exit 1
fi
echo ""

# 构建和启动服务
echo "[5/5] 构建并启动服务..."
echo "这可能需要几分钟时间，请耐心等待..."
echo ""

docker-compose down --remove-orphans 2>/dev/null || true
docker-compose build --no-cache
docker-compose up -d

echo ""
echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
echo ""
echo "========================================"
echo "  服务状态检查"
echo "========================================"
echo ""

docker-compose ps

echo ""
echo "========================================"
echo "  部署完成！"
echo "========================================"
echo ""
echo "🎉 Interview Agent 已成功启动！"
echo ""
echo "访问地址:"
echo "  🌐 前端界面: http://localhost:3000"
echo "  📚 API文档:  http://localhost:8000/docs"
echo "  🔧 后端API:  http://localhost:8000"
echo ""
echo "查看日志:"
echo "  docker-compose logs -f"
echo ""
echo "停止服务:"
echo "  docker-compose down"
echo ""
