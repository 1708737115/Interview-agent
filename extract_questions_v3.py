#!/usr/bin/env python3
"""Extract interview questions from PDF raw text - Refined version."""

import json
import re

# Read raw text
with open("/home/fengxu/mylib/interview-agent/raw_text.txt", "r", encoding="utf-8") as f:
    raw_text = f.read()

# Define categories and their keywords
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

# Section markers in the text
section_markers = {
    "Go语言": ["Go 入门", "Go语言", "Go ⼊⻔", "Go 进阶", "Go ⾼级", "golang", "Golang", "Goroutine", "GMP"],
    "MySQL": ["MySQL", "mysql", "Mysql", "索引", "事务", "InnoDB", "B+树", "死锁"],
    "Redis": ["Redis", "redis", "缓存", "RDB", "AOF", "zset"],
    "Linux": ["Linux", "linux", "Unix", "BASH", "bash", "shell", "内核", "进程", "线程"],
    "Kafka/RocketMQ": ["Kafka", "kafka", "RocketMQ", "rocketmq", "消息队列", "RabbitMQ", "rabbitmq"],
    "Docker": ["Docker", "docker", "容器", "镜像", "Dockerfile", "Swarm", "DevOps"],
    "Networks and OS": ["网络", "操作系统", "OS", "TCP", "UDP", "HTTP", "HTTPS", "socket", "IO多路复用"],
    "Microservices": ["微服务", "领域驱动", "DDD", "REST", "服务发现", "注册中心", "网关"],
    "Distributed systems": ["分布式", "分布式锁", "分布式事务", "CAP", "BASE", "Raft", "Paxos", "ZooKeeper", "etcd", "幂等性"],
    "MongoDB": ["MongoDB", "mongodb", "文档数据库", "NoSQL"],
    "Nginx": ["Nginx", "nginx", "反向代理", "负载均衡", "upstream"],
    "Elasticsearch": ["Elasticsearch", "elasticsearch", "ES", "倒排索引", "Lucene"],
    "System design": ["设计", "架构", "高并发", "高可用", "秒杀", "短链"]
}

def detect_category_by_content(text):
    """Detect category based on content keywords."""
    text_lower = text.lower()
    
    # Category keyword matching
    keywords = {
        "Go语言": ['go ', 'golang', 'goroutine', 'channel', 'slice', 'map', 'defer', 'panic', 'recover', 'gc', 'runtime', 'gmp', '协程', '并发', 'chan'],
        "MySQL": ['mysql', '索引', '事务', 'innodb', 'b+树', '查询优化', '锁', '死锁', '主从', 'explain', '慢查询', '范式', 'binlog'],
        "Redis": ['redis', '缓存', 'rdb', 'aof', '持久化', 'cluster', '哨兵', 'zset', 'hash', '过期', '淘汰策略', '缓存穿透', '缓存雪崩', '缓存击穿'],
        "Linux": ['linux', 'bash', 'shell', '内核', '进程', '线程', 'epoll', 'select', 'poll', '文件系统', '通配符', '信号', 'awk'],
        "Kafka/RocketMQ": ['kafka', 'rocketmq', '消息队列', 'mq', 'topic', 'partition', 'broker', '消费者', '生产者', 'rabbitmq'],
        "Docker": ['docker', '容器', '镜像', 'dockerfile', 'k8s', 'kubernetes', 'swarm', 'devops'],
        "Networks and OS": ['tcp', 'udp', 'http', 'https', '网络协议', '三次握手', '四次挥手', '滑动窗口', '操作系统', 'os', 'ip', '路由', 'dns', 'socket'],
        "Microservices": ['微服务', '服务发现', '注册中心', '网关', '熔断', '限流', '降级', 'rpc', 'ddd', '领域驱动', 'rest'],
        "Distributed systems": ['分布式', 'cap', 'base', 'raft', 'paxos', '分布式锁', '分布式事务', 'zookeeper', 'etcd', '幂等性', '一致性'],
        "MongoDB": ['mongodb', 'mongo', '文档数据库', 'nosql', 'objectid', '分片'],
        "Nginx": ['nginx', '反向代理', '负载均衡', 'location', 'upstream'],
        "Elasticsearch": ['elasticsearch', 'es', '倒排索引', '分词', 'lucene'],
        "System design": ['设计', '架构', '高并发', '高可用', '秒杀', '短链', '性能优化']
    }
    
    scores = {}
    for cat, words in keywords.items():
        score = sum(1 for w in words if w in text_lower)
        if score > 0:
            scores[cat] = score
    
    if scores:
        return max(scores.items(), key=lambda x: x[1])[0]
    return None

def clean_question(text):
    """Clean question text."""
    # Remove URLs
    text = re.sub(r'https?://\S+', '', text)
    # Remove extra whitespace
    text = ' '.join(text.split())
    # Remove common prefixes
    text = re.sub(r'^\d+[\.\s\-）\)]+', '', text)
    text = re.sub(r'^[（(]\d+[)）][\.\s]*', '', text)
    return text.strip()

def is_valid_question(text):
    """Check if text is a valid question."""
    if len(text) < 15 or len(text) > 150:
        return False
    
    # Skip if it's just code or URLs
    if text.startswith('http') or text.startswith('package ') or text.startswith('func ') or text.startswith('type '):
        return False
    
    # Skip if it contains too much code-like content
    if text.count('{') > 1 or text.count('}') > 1 or text.count('//') > 2:
        return False
    
    # Must contain question indicators
    question_indicators = ['?', '？', '什么是', '为什么', '如何', '怎么', '介绍一下', '请简述', '请说明', '如何理解', '有什么区别', '有哪些', '讲讲', '说说', '谈谈']
    has_indicator = any(ind in text for ind in question_indicators)
    
    return has_indicator

# Split into sentences/paragraphs
# First, split by newlines and periods that are followed by spaces or newlines
text_parts = re.split(r'[。！\n]+', raw_text)

questions = []

for part in text_parts:
    part = part.strip()
    if not part or len(part) < 15:
        continue
    
    # Look for question patterns within each part
    # Pattern 1: Questions ending with ? or ？
    q_matches = re.findall(r'([^?？]{10,120}[?？])', part)
    for q in q_matches:
        q_clean = clean_question(q)
        if is_valid_question(q_clean):
            questions.append(q_clean)
    
    # Pattern 2: Chinese question patterns without explicit question mark
    if '?' not in part and '？' not in part:
        # Check for question patterns
        patterns = [
            r'(?:什么是|啥是)[^，。]{3,50}',
            r'(?:为什么)[^，。]{3,50}',
            r'(?:如何实现|怎么实现)[^，。]{3,50}',
            r'(?:介绍一下|简述一下|请简述|请说明)[^，。]{3,50}',
            r'(?:如何理解|怎么理解)[^，。]{3,50}',
            r'(?:有什么区别|有什么不同)[^，。]{3,50}',
            r'(?:有什么优缺点)[^，。]{3,50}',
            r'(?:如何解决|怎么处理|怎么解决)[^，。]{3,50}',
            r'(?:有哪些)[^，。]{3,50}',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, part)
            for m in matches:
                m_clean = clean_question(m)
                if is_valid_question(m_clean + '？'):
                    questions.append(m_clean + '？')

# Remove duplicates
seen = set()
unique_questions = []
for q in questions:
    normalized = q.lower().replace(' ', '').replace('　', '').replace('，', ',').replace('。', '.')
    if normalized not in seen:
        seen.add(normalized)
        unique_questions.append(q)

print(f"Found {len(unique_questions)} unique questions")

# Categorize
for q in unique_questions:
    cat = detect_category_by_content(q)
    if cat and cat in categories:
        categories[cat].append(q)

# Save results
output_path = "/home/fengxu/mylib/interview-agent/extracted_questions.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(categories, f, ensure_ascii=False, indent=2)

# Print summary
print("\n" + "="*60)
print("Extraction Summary")
print("="*60)
total = 0
for cat, qs in categories.items():
    print(f"{cat}: {len(qs)} questions")
    total += len(qs)
print(f"\nTotal: {total} questions")
print(f"\nSaved to: {output_path}")

# Show sample questions
print("\n" + "="*60)
print("Sample Questions from Top Categories")
print("="*60)
for cat in ["Go语言", "MySQL", "Redis", "Linux"]:
    qs = categories[cat]
    if qs:
        print(f"\n{cat} ({len(qs)} questions):")
        for i, q in enumerate(qs[:5], 1):
            display = q[:100] + "..." if len(q) > 100 else q
            print(f"  {i}. {display}")
