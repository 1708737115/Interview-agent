# PDF扩展题库使用指南

本系统支持通过PDF文件扩展面试题库，您可以将自己的面试题PDF放入指定目录，系统会自动解析并合并到题库中。

## 📁 目录结构

```
interview-agent/
├── question_pdfs/              # 存放PDF文件的目录
│   ├── 2022后端面试题.pdf
│   ├── java_interview.pdf
│   └── 自定义题目.pdf
├── question_bank_config.json   # 基础题库（JSON格式）
├── import_pdf_questions.py     # PDF导入脚本
└── backend/app/data/           # 合并后的题库输出目录
    └── merged_question_bank.json
```

## 🚀 使用方法

### 方法一：手动导入（开发环境）

```bash
# 1. 将PDF文件放入 question_pdfs/ 目录
cp /path/to/your/interview_questions.pdf question_pdfs/

# 2. 运行导入脚本
python3 import_pdf_questions.py

# 3. 脚本会自动解析PDF并合并到题库
# 输出文件: backend/app/data/merged_question_bank.json
```

### 方法二：部署时自动导入（推荐）

系统会在部署时自动执行导入：

```bash
# 1. 将PDF放入目录
cp your_questions.pdf question_pdfs/

# 2. 正常部署
docker-compose up -d

# 部署脚本会自动执行导入并加载合并后的题库
```

## 📄 PDF文件要求

### 支持的格式
- 纯文本PDF（文字可选中）
- 扫描版PDF（需要OCR，准确率可能降低）
- 中文/英文混合

### 最佳实践
1. **题目格式**: 每道题独占一行，以问号结尾
2. **分类清晰**: PDF文件名可以体现分类，如 `redis_interview.pdf`
3. **内容质量**: 避免过多冗余文字，专注于题目本身
4. **文件命名**: 使用有意义的文件名，如 `2024_后端面试宝典.pdf`

### 题目识别规则
系统会自动识别以下格式的题目：
- ✅ 包含问号/问号的句子：`什么是 goroutine？`
- ✅ 以编号开头：`1. 请解释...` 或 `A. 如何...`
- ✅ 包含关键词：`什么是`、`为什么`、`请解释`、`如何`

## ⚙️ 自动分类

导入的题目会自动分类到以下类别：

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
| 进程, 线程, 内存 | 操作系统 |
| 微服务, ddd | 微服务 |
| 分布式, cap | 分布式系统 |
| 设计, 秒杀, 短链接 | 系统设计 |

未识别的题目会放入"通用"分类。

## 🔧 高级配置

### 自定义导入参数

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

### 查看导入结果

```bash
# 查看合并后的题库统计
python3 -c "
import json
with open('backend/app/data/merged_question_bank.json') as f:
    data = json.load(f)
    total = sum(
        len(cat.get('questions', []))
        for g in data['groups'].values()
        for cat in g['categories'].values()
    )
    print(f'总计: {total} 道题目')
"
```

## 📝 题目去重

目前系统**不进行自动去重**，如果多次导入相同的PDF，题目会重复添加。

### 手动去重方法

```bash
# 在导入前清空之前的PDF（推荐）
rm question_pdfs/*.pdf
cp new_questions.pdf question_pdfs/
python3 import_pdf_questions.py
```

## 🔄 更新题库流程

```bash
# 1. 添加新的PDF
cp new_interview_questions.pdf question_pdfs/

# 2. 重新导入（会自动合并所有PDF）
python3 import_pdf_questions.py

# 3. 查看新增的题数
# 脚本会输出统计信息

# 4. 重启服务（如果使用Docker）
docker-compose restart backend
```

## 🎯 推荐PDF资源

### 开源项目
- [后端开发大厂面试题](https://github.com/xiaobaiTech/golangFamily)
- [Java面试题合集](https://github.com/Snailclimb/JavaGuide)
- [前端面试题](https://github.com/haizlin/fe-interview)

### 获取PDF的方法
1. 将Markdown/HTML面试题转换为PDF
2. 从在线面试题库网站导出
3. 公司内部面试题整理
4. 购买或下载技术书籍的面试题章节

## ⚠️ 注意事项

1. **版权问题**: 请确保您有权限使用导入的PDF内容
2. **题目质量**: 建议先预览PDF内容，确保题目质量
3. **文件大小**: 单个PDF建议不超过50MB，否则解析较慢
4. **编码问题**: 中文PDF使用UTF-8编码效果最佳
5. **备份**: 定期备份合并后的题库文件

## 💡 最佳实践

### 场景1：从零开始搭建题库

```bash
# 1. 使用轻量版作为基础
cp question_bank_light.json question_bank_config.json

# 2. 添加自己的PDF补充
cp company_questions.pdf question_pdfs/

# 3. 合并导入
python3 import_pdf_questions.py

# 4. 部署
docker-compose up -d
```

### 场景2：已有基础题库，只想添加少量PDF

```bash
# 1. 直接将PDF放入目录
cp supplement.pdf question_pdfs/

# 2. 重新导入（会自动合并）
python3 import_pdf_questions.py

# 3. 查看新增题目数
# 脚本会显示统计信息
```

### 场景3：完全使用自己的PDF题库

```bash
# 1. 清空默认PDF
rm -f question_pdfs/*.pdf

# 2. 放入自己的PDF
cp my_question_bank_*.pdf question_pdfs/

# 3. 创建空的基础题库
echo '{"version":"1.0","groups":{}}' > empty_bank.json

# 4. 导入（只使用PDF）
python3 import_pdf_questions.py --base-bank empty_bank.json
```

## 🐛 故障排查

### 问题1: 导入后题目数为0

**原因**: PDF可能是扫描版或文字不可选中

**解决**: 
- 使用OCR工具预处理PDF
- 确保PDF中的文字可以复制粘贴

### 问题2: 分类不准确

**原因**: 自动分类基于关键词匹配，可能有误判

**解决**:
- 手动修改 `merged_question_bank.json` 中的分类
- 或在PDF中使用更明确的关键词

### 问题3: 题目内容被截断

**原因**: 某些题目可能跨越多行

**解决**:
- 目前系统按行识别，建议每道题独占一行
- 或使用PDF编辑工具调整格式

### 问题4: 部署后没有加载新题目

**原因**: 服务没有重启或配置未更新

**解决**:
```bash
# 1. 确认合并文件存在
ls -lh backend/app/data/merged_question_bank.json

# 2. 重启服务
docker-compose restart backend

# 3. 检查日志
docker-compose logs backend
```

## 📞 获取帮助

如有问题，请：
1. 查看脚本帮助: `python3 import_pdf_questions.py --help`
2. 检查PDF格式是否符合要求
3. 查看后端日志排查问题

---

**提示**: PDF导入是增量式的，可以多次运行脚本，新的PDF题目会追加到已有题库中。
