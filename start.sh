#!/bin/bash
# Interview Agent 快速启动脚本

set -e

cd "$(dirname "$0")"

echo "🚀 启动 Interview Agent..."

# 检查 .env 文件
if [ ! -f "backend/.env" ]; then
    echo "⚠️  创建默认配置文件..."
    cp backend/.env.example backend/.env 2>/dev/null || echo "GLM4_API_KEY=your_api_key_here" > backend/.env
    echo "⚠️  请编辑 backend/.env 文件，添加你的 GLM4_API_KEY"
    exit 1
fi

# 停止旧服务
echo "🛑 停止旧服务..."
docker-compose down --remove-orphans 2>/dev/null || true

# 清理旧镜像（可选）
if [ "$1" == "--clean" ]; then
    echo "🧹 清理旧镜像..."
    docker rmi interview-agent-backend interview-agent-frontend 2>/dev/null || true
fi

# 构建镜像（使用缓存加速）
echo "🔨 构建镜像..."
docker-compose build

# 启动服务
echo "🚀 启动服务..."
docker-compose up -d

# 等待服务启动
sleep 3

echo ""
echo "✅ 启动成功！"
echo ""
echo "📱 访问地址:"
echo "   前端: http://localhost:3000"
echo "   API:  http://localhost:8000/docs"
echo ""
docker-compose ps
