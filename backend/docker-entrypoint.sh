#!/bin/bash
# 后端服务启动脚本
# 在启动服务前自动导入PDF题库

echo "=========================================="
echo "🚀 Interview Agent 启动脚本"
echo "=========================================="
echo ""

# 检查是否需要导入PDF
echo "📚 检查PDF题库..."

# 设置路径
PDF_DIR="${PDF_DIR:-/app/question_pdfs}"
BASE_BANK="${BASE_BANK:-/app/question_bank_config.json}"
OUTPUT_BANK="${OUTPUT_BANK:-/app/data/merged_question_bank.json}"

# 如果PDF目录存在且有PDF文件
if [ -d "$PDF_DIR" ] && [ "$(ls -A $PDF_DIR/*.pdf 2>/dev/null)" ]; then
    echo "📖 发现PDF文件，开始导入..."
    
    # 检查导入脚本是否存在
    if [ -f "/app/import_pdf_questions.py" ]; then
        python3 /app/import_pdf_questions.py \
            --pdf-dir "$PDF_DIR" \
            --base-bank "$BASE_BANK" \
            --output "$OUTPUT_BANK"
        
        echo "✅ PDF导入完成"
    else
        echo "⚠️  导入脚本不存在，跳过PDF导入"
    fi
else
    echo "ℹ️  未找到PDF文件，使用默认题库"
    
    # 如果没有合并题库，复制基础题库
    if [ ! -f "$OUTPUT_BANK" ]; then
        if [ -f "$BASE_BANK" ]; then
            cp "$BASE_BANK" "$OUTPUT_BANK"
            echo "✅ 已复制默认题库"
        fi
    fi
fi

echo ""
echo "=========================================="
echo "🎯 启动后端服务..."
echo "=========================================="
echo ""

# 启动后端服务
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
