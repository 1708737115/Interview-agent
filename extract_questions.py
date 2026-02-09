#!/usr/bin/env python3
"""Extract interview questions from PDF file."""

import json
import re
from PyPDF2 import PdfReader

pdf_path = "/home/fengxu/mylib/interview-agent/2022_后端开发大厂面试题.pdf"
output_path = "/home/fengxu/mylib/interview-agent/extracted_questions.json"

categories = {
    "Go语言": [],
    "MySQL": [],
    "Redis": [],
    "Linux": [],
    "Kafka/RocketMQ": [],
    "Docker": [],
    "Networks and OS": [],
    "Microservices": [],
    "Distributed systems": [],
    "MongoDB": [],
    "Nginx": [],
    "Elasticsearch": [],
    "System design": []
}

def is_question(text):
    """Check if text is likely an interview question."""
    text = text.strip()
    # Skip if too short
    if len(text) < 10:
        return False
    # Skip if too long (probably not a question)
    if len(text) > 200:
        return False
    # Check for question marks
    if text.endswith('?'):
        return True
    if '？' in text:
        return True
    # Check for question patterns in Chinese
    question_patterns = [
        r'什么是',
        r'什么是',
        r'为什么',
        r'如何实现',
        r'介绍一下',
        r'请简述',
        r'请说明',
        r'如何理解',
        r'有什么区别',
        r'有什么优缺点',
        r'如何解决',
        r'什么是.*的',
        r'如何处理',
        r'如何实现',
        r'^(\d+[\.．、])?\s*[^。]{10,50}[?？]',
        r'^\d+[\.\s]+',  # Numbered questions
    ]
    for pattern in question_patterns:
        if re.search(pattern, text):
            return True
    return False

def detect_category(text, current_category=None):
    """Detect category based on text content."""
    text_lower = text.lower()
    
    category_keywords = {
        "Go语言": ["go", "golang", "goroutine", "channel", "slice", "map", "defer", "panic", "recover", "gc", "内存管理", "goroutine", "并发"],
        "MySQL": ["mysql", "索引", "事务", "b+树", "innodb", "锁", "慢查询", "主从", "explain", "死锁"],
        "Redis": ["redis", "缓存", "rdb", "aof", "持久化", "cluster", "哨兵", "zset", "哈希", "过期"],
        "Linux": ["linux", "进程", "线程", "epoll", "select", "poll", "文件系统", "命令", "内核", "shell"],
        "Kafka/RocketMQ": ["kafka", "rocketmq", "消息队列", "mq", "topic", "partition", "消费者", "生产者", "消息"],
        "Docker": ["docker", "容器", "镜像", "kubernetes", "k8s", "dockerfile", "容器化"],
        "Networks and OS": ["tcp", "udp", "http", "https", "网络", "协议", "三次握手", "四次挥手", "滑动窗口", "os", "操作系统"],
        "Microservices": ["微服务", "服务发现", "注册中心", "网关", "熔断", "限流", "降级", "rpc"],
        "Distributed systems": ["分布式", "一致性", "raft", "paxos", "cap", "base", "分布式锁", "分布式事务", "zookeeper", "etcd"],
        "MongoDB": ["mongodb", "文档", "nosql", "副本集", "分片"],
        "Nginx": ["nginx", "反向代理", "负载均衡", "location", "upstream"],
        "Elasticsearch": ["elasticsearch", "es", "倒排索引", "分词", "搜索", "lucene"],
        "System design": ["设计", "架构", "系统", "高并发", "高可用", "秒杀", "短链", "设计题"]
    }
    
    scores = {}
    for cat, keywords in category_keywords.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        if score > 0:
            scores[cat] = score
    
    if scores:
        return max(scores.items(), key=lambda x: x[1])[0]
    return current_category

def clean_question(text):
    """Clean and format question text."""
    # Remove common prefixes
    text = re.sub(r'^\d+[\.\s\-]+', '', text)
    text = re.sub(r'^[（(]\d+[)）][\.\s]*', '', text)
    # Remove extra whitespace
    text = ' '.join(text.split())
    return text.strip()

# Read PDF
print("Reading PDF...")
reader = PdfReader(pdf_path)
print(f"Total pages: {len(reader.pages)}")

all_text = ""
for i, page in enumerate(reader.pages):
    if i % 10 == 0:
        print(f"Processing page {i+1}/{len(reader.pages)}...")
    text = page.extract_text()
    all_text += text + "\n"

# Save raw text for debugging
with open("/home/fengxu/mylib/interview-agent/raw_text.txt", "w", encoding="utf-8") as f:
    f.write(all_text)
print("Raw text saved to raw_text.txt")

# Split by lines and process
lines = all_text.split('\n')
current_category = None

# Category detection from section headers
category_headers = {
    "go": "Go语言",
    "golang": "Go语言",
    "mysql": "MySQL",
    "redis": "Redis",
    "linux": "Linux",
    "kafka": "Kafka/RocketMQ",
    "rocketmq": "Kafka/RocketMQ",
    "mq": "Kafka/RocketMQ",
    "docker": "Docker",
    "network": "Networks and OS",
    "networks": "Networks and OS",
    "os": "Networks and OS",
    "operating": "Networks and OS",
    "microservice": "Microservices",
    "distributed": "Distributed systems",
    "mongodb": "MongoDB",
    "nginx": "Nginx",
    "elasticsearch": "Elasticsearch",
    "es": "Elasticsearch",
    "system design": "System design",
    "设计": "System design"
}

# First pass: identify sections
for line in lines:
    line_stripped = line.strip()
    if not line_stripped:
        continue
    
    # Check for section headers
    line_lower = line_stripped.lower()
    for keyword, cat in category_headers.items():
        if keyword in line_lower and len(line_stripped) < 50:
            current_category = cat
            print(f"Found section: {cat} - {line_stripped[:50]}")
            break

# Second pass: extract questions
current_category = None
potential_questions = []

for line in lines:
    line_stripped = line.strip()
    if not line_stripped:
        continue
    
    # Check for section headers
    line_lower = line_stripped.lower()
    for keyword, cat in category_headers.items():
        if keyword in line_lower and len(line_stripped) < 50:
            current_category = cat
            break
    
    # Try to identify questions
    if is_question(line_stripped):
        cleaned = clean_question(line_stripped)
        if cleaned:
            cat = current_category or detect_category(cleaned)
            if cat:
                potential_questions.append((cat, cleaned))

# Deduplicate and filter
seen = set()
for cat, q in potential_questions:
    key = q.lower().replace(' ', '')
    if key not in seen and len(q) >= 10:
        seen.add(key)
        categories[cat].append(q)

# Also try to find numbered questions with regex
numbered_pattern = re.compile(r'(?:^|\n)\s*(?:\d+|\(\d+\)|（\d+）)[\.、\s]+([^\n]{10,150}?)(?:\n|$)')
matches = numbered_pattern.findall(all_text)

for match in matches:
    if is_question(match):
        cleaned = clean_question(match)
        if cleaned:
            cat = detect_category(cleaned)
            if cat:
                key = cleaned.lower().replace(' ', '')
                if key not in seen:
                    seen.add(key)
                    categories[cat].append(cleaned)

# Save results
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(categories, f, ensure_ascii=False, indent=2)

# Print summary
print("\n" + "="*50)
print("Extraction Summary:")
print("="*50)
total = 0
for cat, questions in categories.items():
    print(f"{cat}: {len(questions)} questions")
    total += len(questions)
print(f"\nTotal: {total} questions")
print(f"\nOutput saved to: {output_path}")
