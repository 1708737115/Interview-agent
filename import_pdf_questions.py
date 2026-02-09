#!/usr/bin/env python3
"""
PDF题库导入脚本
用于解析用户上传的PDF文件并提取面试题目，合并到现有题库中

使用方法:
    python import_pdf_questions.py [--pdf-dir PDF_DIR] [--output OUTPUT]

参数:
    --pdf-dir: PDF文件存放目录 (默认: question_pdfs/)
    --output: 输出合并后的题库文件 (默认: backend/app/data/merged_question_bank.json)
    --base-bank: 基础题库文件 (默认: question_bank_config.json)
"""

import os
import sys
import json
import argparse
import re
from pathlib import Path
from typing import List, Dict, Any

# 添加backend到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    import PyPDF2
except ImportError:
    print("❌ 错误: 需要安装PyPDF2")
    print("   pip install PyPDF2")
    sys.exit(1)


def clean_text(text: str) -> str:
    """清洗文本，去除乱码和多余内容"""
    if not text or len(text) < 10:
        return ""
    
    # 去除乱码字符（保留常见中文字符、英文字母、数字和标点）
    text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s\n\r.,;:!?，。；：！？、""''（）()-]', '', text)
    
    # 去除URL
    text = re.sub(r'https?://\S+', '', text)
    
    # 去除邮箱
    text = re.sub(r'[\w\-]+@[\w\-]+\.\w+', '', text)
    
    # 去除多余空格
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


def extract_questions_from_pdf(pdf_path: str) -> List[Dict[str, Any]]:
    """从PDF中提取面试题目"""
    questions = []
    
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            print(f"📖 正在解析: {os.path.basename(pdf_path)} ({len(pdf_reader.pages)} 页)")
            
            # 提取所有文本
            full_text = ""
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    text = page.extract_text()
                    if text:
                        full_text += text + "\n"
                except Exception as e:
                    print(f"   ⚠️  第 {page_num + 1} 页解析失败: {e}")
                    continue
            
            # 清洗文本
            full_text = clean_text(full_text)
            
            # 识别题目模式
            # 模式1: 包含问号/问号的行
            # 模式2: 以数字/字母编号开头的问题
            # 模式3: 包含特定关键词的问题
            
            lines = full_text.split('\n')
            
            for i, line in enumerate(lines):
                line = line.strip()
                if not line:
                    continue
                
                # 识别题目
                is_question = False
                
                # 模式1: 包含问号
                if '?' in line or '？' in line:
                    if 15 <= len(line) <= 200:
                        is_question = True
                
                # 模式2: 以数字/字母编号开头
                elif re.match(r'^(\d+[.．、]|[(（]?\d+[)）]?|[A-Za-z][.．、])', line):
                    if 15 <= len(line) <= 200 and ('是' in line or '什么' in line or '怎么' in line or '如何' in line):
                        is_question = True
                
                # 模式3: 包含面试题关键词
                elif re.search(r'(什么是|为什么|请解释|请描述|如何|怎么|介绍)', line):
                    if 15 <= len(line) <= 200:
                        is_question = True
                
                if is_question:
                    # 尝试分类
                    category = classify_question(line)
                    
                    # 生成题目对象
                    question = {
                        'id': f"pdf_{len(questions)}",
                        'text': line[:150],
                        'category': category,
                        'difficulty': 3,  # 默认中等难度
                        'type': 'technical',
                        'source': os.path.basename(pdf_path)
                    }
                    
                    questions.append(question)
    
    except Exception as e:
        print(f"❌ 解析失败 {pdf_path}: {e}")
        return []
    
    return questions


def classify_question(text: str) -> str:
    """根据内容自动分类题目"""
    text_lower = text.lower()
    
    # Go语言
    if any(kw in text_lower for kw in ['go', 'golang', 'goroutine', 'channel', 'slice', 'map', 'defer', 'gc']):
        return 'language_go'
    
    # Java
    elif any(kw in text_lower for kw in ['java', 'jvm', 'spring', 'hashmap', 'concurrenthashmap']):
        return 'language_java'
    
    # MySQL
    elif any(kw in text_lower for kw in ['mysql', 'sql', '索引', '事务', 'innodb', 'b+树', '锁']):
        return 'database_mysql'
    
    # Redis
    elif any(kw in text_lower for kw in ['redis', '缓存', '持久化', 'rdb', 'aof', '穿透', '击穿']):
        return 'database_redis'
    
    # Kafka
    elif any(kw in text_lower for kw in ['kafka', '消息队列', 'partition', 'topic', 'consumer']):
        return 'mq_kafka'
    
    # Docker
    elif any(kw in text_lower for kw in ['docker', '容器', '镜像', 'container']):
        return 'backend_docker'
    
    # Linux
    elif any(kw in text_lower for kw in ['linux', '命令', '进程', '线程', 'shell']):
        return 'basics_linux'
    
    # 网络
    elif any(kw in text_lower for kw in ['tcp', 'http', 'udp', '网络', '三次握手', '四次挥手']):
        return 'basics_network'
    
    # 操作系统
    elif any(kw in text_lower for kw in ['进程', '线程', '内存', '调度', '死锁', '虚拟内存']):
        return 'basics_os'
    
    # 微服务
    elif any(kw in text_lower for kw in ['微服务', 'ddd', '服务拆分', '治理']):
        return 'architecture_microservices'
    
    # 分布式
    elif any(kw in text_lower for kw in ['分布式', 'cap', 'base', '分布式锁', '分布式事务']):
        return 'architecture_distributed'
    
    # 系统设计
    elif any(kw in text_lower for kw in ['设计', '秒杀', '短链接', '推送', '排行榜', '计数器']):
        return 'system_design'
    
    # 默认
    return 'general'


def load_base_question_bank(base_path: str) -> Dict[str, Any]:
    """加载基础题库"""
    try:
        with open(base_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"⚠️  基础题库不存在: {base_path}")
        print("   将创建新的题库结构")
        return create_empty_bank()
    except Exception as e:
        print(f"❌ 加载基础题库失败: {e}")
        sys.exit(1)


def create_empty_bank() -> Dict[str, Any]:
    """创建空的题库结构"""
    return {
        'version': '1.0',
        'description': 'AI面试系统题库',
        'groups': {
            'languages': {
                'name': '编程语言',
                'description': 'Go、Java、Python等编程语言',
                'enabled': True,
                'categories': {
                    'language_go': {'name': 'Go语言', 'enabled': True, 'questions': []},
                    'language_java': {'name': 'Java', 'enabled': True, 'questions': []},
                }
            },
            'databases': {
                'name': '数据库',
                'description': 'MySQL、Redis等数据库',
                'enabled': True,
                'categories': {
                    'database_mysql': {'name': 'MySQL', 'enabled': True, 'questions': []},
                    'database_redis': {'name': 'Redis', 'enabled': True, 'questions': []},
                }
            },
            'general': {
                'name': '其他',
                'description': '其他题目',
                'enabled': True,
                'categories': {
                    'general': {'name': '通用', 'enabled': True, 'questions': []}
                }
            }
        }
    }


def merge_questions(base_bank: Dict[str, Any], new_questions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """合并新题目到基础题库"""
    added_count = 0
    
    for question in new_questions:
        category = question['category']
        
        # 查找对应的分类
        found = False
        for group in base_bank['groups'].values():
            if category in group['categories']:
                group['categories'][category]['questions'].append(question)
                group['categories'][category]['count'] = group['categories'][category].get('count', 0) + 1
                added_count += 1
                found = True
                break
        
        # 如果没找到对应分类，放入general
        if not found:
            if 'general' not in base_bank['groups']:
                base_bank['groups']['general'] = {
                    'name': '其他',
                    'description': '其他题目',
                    'enabled': True,
                    'categories': {}
                }
            if 'general' not in base_bank['groups']['general']['categories']:
                base_bank['groups']['general']['categories']['general'] = {
                    'name': '通用',
                    'enabled': True,
                    'questions': []
                }
            
            base_bank['groups']['general']['categories']['general']['questions'].append(question)
            base_bank['groups']['general']['categories']['general']['count'] = \
                base_bank['groups']['general']['categories']['general'].get('count', 0) + 1
            added_count += 1
    
    return base_bank, added_count


def save_merged_bank(bank: Dict[str, Any], output_path: str):
    """保存合并后的题库"""
    # 确保目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(bank, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 已保存合并题库: {output_path}")


def print_statistics(bank: Dict[str, Any]):
    """打印题库统计信息"""
    print("\n" + "=" * 60)
    print("📊 题库统计")
    print("=" * 60)
    
    total = 0
    for group_name, group in bank['groups'].items():
        group_total = sum(cat.get('count', len(cat.get('questions', []))) 
                         for cat in group['categories'].values())
        if group_total > 0:
            print(f"\n【{group['name']}】- {group_total}题")
            for cat_name, cat in group['categories'].items():
                count = cat.get('count', len(cat.get('questions', [])))
                if count > 0:
                    print(f"  ├─ {cat['name']}: {count}题")
            total += group_total
    
    print("\n" + "-" * 60)
    print(f"总计: {total} 道题目")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description='导入PDF题库')
    parser.add_argument('--pdf-dir', default='question_pdfs', 
                       help='PDF文件存放目录 (默认: question_pdfs/)')
    parser.add_argument('--output', default='backend/app/data/merged_question_bank.json',
                       help='输出文件路径')
    parser.add_argument('--base-bank', default='question_bank_config.json',
                       help='基础题库文件')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("📚 PDF题库导入工具")
    print("=" * 60)
    print()
    
    # 1. 加载基础题库
    print(f"1️⃣  加载基础题库: {args.base_bank}")
    base_bank = load_base_question_bank(args.base_bank)
    
    # 统计基础题库数量
    base_count = sum(
        cat.get('count', len(cat.get('questions', [])))
        for group in base_bank['groups'].values()
        for cat in group['categories'].values()
    )
    print(f"   基础题库: {base_count} 道题目")
    print()
    
    # 2. 扫描PDF文件
    print(f"2️⃣  扫描PDF目录: {args.pdf_dir}")
    
    if not os.path.exists(args.pdf_dir):
        print(f"   ⚠️  目录不存在，创建: {args.pdf_dir}")
        os.makedirs(args.pdf_dir, exist_ok=True)
    
    pdf_files = list(Path(args.pdf_dir).glob('*.pdf'))
    
    if not pdf_files:
        print("   ⚠️  未找到PDF文件")
        print("   💡 提示: 将PDF文件放入此目录即可自动导入")
        print()
        # 没有PDF时也保存基础题库
        save_merged_bank(base_bank, args.output)
        print_statistics(base_bank)
        return
    
    print(f"   发现 {len(pdf_files)} 个PDF文件")
    for pdf_file in pdf_files:
        print(f"   - {pdf_file.name}")
    print()
    
    # 3. 解析PDF文件
    print("3️⃣  解析PDF文件...")
    all_new_questions = []
    
    for pdf_file in pdf_files:
        questions = extract_questions_from_pdf(str(pdf_file))
        all_new_questions.extend(questions)
        print(f"   ✅ {pdf_file.name}: 提取 {len(questions)} 题")
    
    print(f"\n   共提取 {len(all_new_questions)} 道新题目")
    print()
    
    # 4. 合并题库
    print("4️⃣  合并题库...")
    merged_bank, added_count = merge_questions(base_bank, all_new_questions)
    print(f"   新增题目: {added_count} 道")
    print()
    
    # 5. 保存合并后的题库
    print("5️⃣  保存合并题库...")
    save_merged_bank(merged_bank, args.output)
    print()
    
    # 6. 打印统计
    print_statistics(merged_bank)
    
    print("\n✅ 导入完成！")
    print(f"   合并题库已保存到: {args.output}")
    print()
    print("💡 使用提示:")
    print("   1. 将更多PDF放入 question_pdfs/ 目录")
    print("   2. 重新运行此脚本可继续导入")
    print("   3. 部署时系统会自动加载合并后的题库")


if __name__ == '__main__':
    main()
