#!/usr/bin/env python3
"""Extract interview questions from PDF - Final refined version."""

import json
import re

# Read raw text
with open("/home/fengxu/mylib/interview-agent/raw_text.txt", "r", encoding="utf-8") as f:
    raw_text = f.read()

# Define categories
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

def detect_category(text):
    """Detect category based on keywords in text."""
    text_lower = text.lower()
    
    # Strong category indicators (check these first)
    strong_indicators = {
        "Go语言": [r'\bgo\s', r'golang', r'goroutine', r'channel\b', r'\bslice\b', r'\bmap\b', r'\bdefer\b', r'\bpanic\b', r'\bgc\b', r'gmp', r'协程', r'csp', r'context'],
        "MySQL": [r'mysql', r'innodb', r'myisam', r'binlog', r'b\+树', r'事务', r'索引.*mysql', r'mysql.*索引'],
        "Redis": [r'redis', r'缓存', r'rdb', r'aof', r'zset', r'sorted set', r'缓存穿透', r'缓存雪崩', r'缓存击穿'],
        "Linux": [r'linux(?!.*redis)', r'\blinux\b', r'\bbash\b', r'\bshell\b', r'epoll', r'select', r'poll', r'内核', r'文件描述符'],
        "Kafka/RocketMQ": [r'kafka', r'rocketmq', r'rabbitmq', r'topic', r'partition', r'broker', r'消息队列', r'mq', r'生产者', r'消费者'],
        "Docker": [r'docker', r'容器', r'镜像', r'dockerfile', r'k8s', r'kubernetes', r'pod', r'swarm'],
        "Networks and OS": [r'tcp', r'udp', r'http', r'https', r'三次握手', r'四次挥手', r'滑动窗口', r'操作系统.*区别', r'\bos\b', r'socket'],
        "Microservices": [r'微服务', r'领域驱动', r'ddd', r'soa', r'服务发现', r'注册中心', r'网关', r'熔断', r'限流'],
        "Distributed systems": [r'分布式', r'cap', r'base', r'raft', r'paxos', r'分布式锁', r'分布式事务', r'zookeeper', r'etcd', r'幂等'],
        "MongoDB": [r'mongodb', r'mongo\b', r'文档数据库', r'nosql.*mongo'],
        "Nginx": [r'nginx', r'反向代理', r'upstream', r'location.*nginx', r'worker.*process'],
        "Elasticsearch": [r'elasticsearch', r'\bes\b', r'倒排索引', r'lucene'],
        "System design": [r'秒杀', r'短链', r'高并发.*设计', r'架构设计', r'系统设计']
    }
    
    scores = {}
    for cat, patterns in strong_indicators.items():
        score = sum(2 for p in patterns if re.search(p, text_lower))
        if score > 0:
            scores[cat] = score
    
    if scores:
        return max(scores.items(), key=lambda x: x[1])[0]
    return None

def clean_question(text):
    """Clean question text by removing noise."""
    # Remove URLs
    text = re.sub(r'https?://\S+', '', text)
    # Remove code blocks and function definitions
    text = re.sub(r'package\s+\w+', '', text)
    text = re.sub(r'func\s+\w+\s*\([^)]*\)', '', text)
    text = re.sub(r'import\s*\([^)]*\)', '', text)
    text = re.sub(r'type\s+\w+\s+struct', '', text)
    # Remove file extensions and random strings
    text = re.sub(r'\b[a-zA-Z0-9]{20,}\b', '', text)
    # Remove output markers
    text = re.sub(r'//\s*output', '', text)
    text = re.sub(r'command-line-arguments', '', text)
    # Remove common prefixes
    text = re.sub(r'^\d+[\.\s\-）\)]+', '', text)
    text = re.sub(r'^[（(]\d+[)）][\.\s]*', '', text)
    text = re.sub(r'^golang⾯试题[：:]', '', text)
    text = re.sub(r'^Go.*⾯试', '', text)
    # Remove extra whitespace
    text = ' '.join(text.split())
    return text.strip()

def is_valid_question(text):
    """Validate if text is a proper question."""
    if len(text) < 10 or len(text) > 120:
        return False
    
    # Skip if contains too much code
    if text.count('{') > 0 or text.count('}') > 0 or text.count('//') > 1:
        return False
    
    # Skip if starts with programming keywords
    skip_prefixes = ['http', 'package ', 'func ', 'type ', 'import ', 'var ', 'const ', '//']
    if any(text.lower().startswith(p) for p in skip_prefixes):
        return False
    
    # Must have question indicator
    indicators = ['?', '？', '什么是', '为什么', '如何', '怎么', '介绍一下', '请简述', '请说明', '如何理解', 
                  '有什么区别', '有什么不同', '有哪些', '讲讲', '说说', '谈谈', '是什么', '怎么', '简述']
    if not any(ind in text for ind in indicators):
        return False
    
    # Skip common non-questions
    skip_patterns = ['⾯试题', '⾯试官', 'github', 'mp.weixin', 'csdn', 'xiaobaidebug', '微信公众号', '关注公众号']
    if any(p in text for p in skip_patterns):
        return False
    
    return True

# Extract questions using multiple patterns
questions = []

# Pattern 1: Numbered questions (1. 2. 3.)
# Look for lines starting with numbers followed by question content
lines = raw_text.split('\n')
for line in lines:
    line = line.strip()
    if not line:
        continue
    
    # Try to extract question from line
    # Remove numbering
    clean_line = re.sub(r'^\s*(?:\d+|\(\d+\)|（\d+）)[\.．、\s]+', '', line)
    
    # Check if it looks like a question
    if is_valid_question(clean_line):
        q_clean = clean_question(clean_line)
        if q_clean and len(q_clean) >= 10:
            questions.append(q_clean)

# Pattern 2: Questions with explicit question marks
# Find segments ending with ? or ？
segments = re.split(r'([?？])', raw_text)
for i in range(0, len(segments)-1, 2):
    if i+1 < len(segments):
        q_text = segments[i] + segments[i+1]
        q_text = q_text.strip()
        # Take last 100 chars before the question mark
        if len(q_text) > 120:
            q_text = q_text[-120:]
        if is_valid_question(q_text):
            q_clean = clean_question(q_text)
            if q_clean:
                questions.append(q_clean)

# Pattern 3: Specific question patterns without question marks
patterns = [
    r'(?:什么是|啥是)[^，。？\n]{3,60}(?=[，。\n])',
    r'(?:为什么)[^，。？\n]{3,60}(?=[，。\n])',
    r'(?:如何实现|怎么实现)[^，。？\n]{3,60}(?=[，。\n])',
    r'(?:介绍一下|请简述|请说明)[^，。？\n]{3,60}(?=[，。\n])',
    r'(?:如何理解|怎么理解)[^，。？\n]{3,60}(?=[，。\n])',
    r'(?:有什么区别|有什么不同)[^，。？\n]{3,60}(?=[，。\n])',
    r'(?:有哪些)[^，。？\n]{3,40}(?=[，。\n])',
]

for pattern in patterns:
    matches = re.findall(pattern, raw_text)
    for m in matches:
        m = m.strip() + '？'
        if is_valid_question(m):
            q_clean = clean_question(m)
            if q_clean:
                questions.append(q_clean)

# Remove duplicates
seen = set()
unique_questions = []
for q in questions:
    # Normalize for deduplication
    normalized = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9]', '', q.lower())
    if normalized not in seen and len(normalized) > 5:
        seen.add(normalized)
        unique_questions.append(q)

print(f"Extracted {len(unique_questions)} unique questions")

# Categorize questions
for q in unique_questions:
    cat = detect_category(q)
    if cat and cat in categories:
        categories[cat].append(q)
    else:
        # Try to find best matching category
        best_cat = None
        best_score = 0
        for cat_name in categories.keys():
            score = 0
            q_lower = q.lower()
            if cat_name == "Go语言" and any(w in q_lower for w in ['go', 'golang', 'goroutine']):
                score = 1
            elif cat_name == "MySQL" and 'mysql' in q_lower:
                score = 1
            elif cat_name == "Redis" and 'redis' in q_lower:
                score = 1
            elif cat_name == "Linux" and 'linux' in q_lower:
                score = 1
            if score > best_score:
                best_score = score
                best_cat = cat_name
        
        if best_cat:
            categories[best_cat].append(q)
        else:
            # Put in System design as default
            categories["System design"].append(q)

# Save results
output_path = "/home/fengxu/mylib/interview-agent/extracted_questions.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(categories, f, ensure_ascii=False, indent=2)

# Print summary
print("\n" + "="*60)
print("Extraction Summary")
print("="*60)
total = 0
for cat, qs in sorted(categories.items()):
    count = len(qs)
    print(f"{cat}: {count} questions")
    total += count
print(f"\nTotal: {total} questions")
print(f"\nSaved to: {output_path}")

# Show samples
print("\n" + "="*60)
print("Sample Questions")
print("="*60)
for cat in ["Go语言", "MySQL", "Redis", "Linux", "Kafka/RocketMQ"]:
    qs = categories[cat]
    if qs:
        print(f"\n{cat} ({len(qs)} questions):")
        for i, q in enumerate(qs[:5], 1):
            print(f"  {i}. {q}")
