#!/usr/bin/env python3
"""Extract interview questions from PDF raw text."""

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

# Category detection patterns
category_patterns = {
    "Go语言": r'(?:Go|Golang|goroutine|channel|slice|map|defer|panic|recover|gc|内存管理|并发|协程|GMP|调度)',
    "MySQL": r'(?:MySQL|mysql|索引|事务|B\+树|InnoDB|锁|慢查询|主从|explain|死锁|查询优化|范式|Binlog|存储引擎)',
    "Redis": r'(?:Redis|redis|缓存|RDB|AOF|持久化|cluster|哨兵|zset|哈希|过期|淘汰策略|缓存穿透|缓存雪崩|缓存击穿)',
    "Linux": r'(?:Linux|linux|进程|线程|epoll|select|poll|文件系统|命令|内核|shell|bash|通配符|信号|IO|awk)',
    "Kafka/RocketMQ": r'(?:Kafka|kafka|RocketMQ|rocketmq|消息队列|MQ|topic|partition|消费者|生产者|消息|Broker)',
    "Docker": r'(?:Docker|docker|容器|镜像|kubernetes|k8s|Dockerfile|容器化|Swarm|DevOps|CI)',
    "Networks and OS": r'(?:TCP|UDP|HTTP|HTTPS|网络|协议|三次握手|四次挥手|滑动窗口|OS|操作系统|IP|路由|DNS|socket)',
    "Microservices": r'(?:微服务|服务发现|注册中心|网关|熔断|限流|降级|RPC|领域驱动|DDD|REST)',
    "Distributed systems": r'(?:分布式|一致性|Raft|Paxos|CAP|BASE|分布式锁|分布式事务|ZooKeeper|etcd|幂等性)',
    "MongoDB": r'(?:MongoDB|mongodb|文档|NoSQL|副本集|分片|ObjectID|aggregate)',
    "Nginx": r'(?:Nginx|nginx|反向代理|负载均衡|location|upstream|Master|Worker|高并发|静态资源)',
    "Elasticsearch": r'(?:Elasticsearch|elasticsearch|ES|倒排索引|分词|搜索|Lucene|节点|集群|索引)',
    "System design": r'(?:设计|架构|系统|高并发|高可用|秒杀|短链|设计题|性能优化|监控|日志)'
}

# Split text into lines
lines = raw_text.split('\n')

# Extract questions - looking for patterns
questions = []

# Pattern 1: Numbered questions (1. 2. 3. etc.)
pattern1 = re.compile(r'(?:^|\n)\s*(\d+)[\.．、]\s*([^\n]{5,150}?)(?:\n|$)')
matches1 = pattern1.findall(raw_text)
for num, text in matches1:
    if '?' in text or '？' in text or any(kw in text for kw in ['什么是', '为什么', '如何实现', '介绍一下', '请简述', '请说明', '如何理解', '有什么区别', '如何解决', '如何处理', '怎么', '哪些', '什么']):
        questions.append((num, text.strip()))

# Pattern 2: Questions ending with ? or ？
pattern2 = re.compile(r'([^\n]{10,200}[?？])')
matches2 = pattern2.findall(raw_text)
for text in matches2:
    text = text.strip()
    if len(text) >= 10 and len(text) <= 200:
        questions.append((None, text))

# Pattern 3: "Question-like" patterns
question_indicators = [
    r'(?:什么是|啥是)[^?？]{3,80}[?？]?',
    r'(?:为什么)[^?？]{3,80}[?？]?',
    r'(?:如何实现|怎么实现)[^?？]{3,80}[?？]?',
    r'(?:介绍一下|简述一下|请简述|请说明)[^?？]{3,80}[?？]?',
    r'(?:如何理解|怎么理解)[^?？]{3,80}[?？]?',
    r'(?:有什么区别|有什么不同)[^?？]{3,80}[?？]?',
    r'(?:有什么优缺点|有什么优势)[^?？]{3,80}[?？]?',
    r'(?:如何解决|怎么处理|怎么解决)[^?？]{3,80}[?？]?',
    r'(?:有哪些|有什么)[^?？]{3,80}[?？]?',
    r'(?:怎么做|如何做)[^?？]{3,80}[?？]?',
    r'(?:讲讲|说说|谈一下)[^?？]{3,80}[?？]?',
    r'(?:你了解|知道)[^?？]{3,80}[?？]?',
]

for pattern in question_indicators:
    matches = re.findall(pattern, raw_text)
    for text in matches:
        text = text.strip()
        if 10 <= len(text) <= 200:
            questions.append((None, text))

# Deduplicate
deduplicated = []
seen = set()
for num, q in questions:
    # Normalize for deduplication
    normalized = q.lower().replace(' ', '').replace('　', '')
    if normalized not in seen and len(q) >= 10:
        seen.add(normalized)
        deduplicated.append(q)

print(f"Found {len(deduplicated)} unique questions")

# Categorize questions
for q in deduplicated:
    matched = False
    for cat, pattern in category_patterns.items():
        if re.search(pattern, q, re.IGNORECASE):
            categories[cat].append(q)
            matched = True
            break
    
    # If not matched, try to detect based on content
    if not matched:
        if any(kw in q.lower() for kw in ['go', 'golang', 'goroutine', 'channel', 'slice', 'map', 'defer']):
            categories["Go语言"].append(q)
        elif any(kw in q.lower() for kw in ['mysql', '索引', '事务', 'innodb', '查询']):
            categories["MySQL"].append(q)
        elif any(kw in q.lower() for kw in ['redis', '缓存', 'rdb', 'aof']):
            categories["Redis"].append(q)
        elif any(kw in q.lower() for kw in ['linux', '进程', '线程', 'epoll', '文件']):
            categories["Linux"].append(q)
        elif any(kw in q.lower() for kw in ['kafka', 'rocketmq', '消息队列', 'mq']):
            categories["Kafka/RocketMQ"].append(q)
        elif any(kw in q.lower() for kw in ['docker', '容器', '镜像', 'k8s']):
            categories["Docker"].append(q)
        elif any(kw in q.lower() for kw in ['tcp', 'udp', 'http', '网络', '协议']):
            categories["Networks and OS"].append(q)
        elif any(kw in q.lower() for kw in ['微服务', 'rpc', '熔断', '限流']):
            categories["Microservices"].append(q)
        elif any(kw in q.lower() for kw in ['分布式', 'cap', 'base', 'raft', 'paxos']):
            categories["Distributed systems"].append(q)
        elif any(kw in q.lower() for kw in ['mongodb', 'mongo']):
            categories["MongoDB"].append(q)
        elif any(kw in q.lower() for kw in ['nginx']):
            categories["Nginx"].append(q)
        elif any(kw in q.lower() for kw in ['elasticsearch', 'es', '搜索']):
            categories["Elasticsearch"].append(q)
        else:
            # Default to System design or skip
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
for cat, qs in categories.items():
    print(f"{cat}: {len(qs)} questions")
    total += len(qs)
print(f"\nTotal: {total} questions")
print(f"\nSaved to: {output_path}")

# Show sample questions from each category
print("\n" + "="*60)
print("Sample Questions from Each Category")
print("="*60)
for cat, qs in categories.items():
    if qs:
        print(f"\n{cat}:")
        for i, q in enumerate(qs[:3], 1):
            print(f"  {i}. {q[:80]}...")
