#!/usr/bin/env python3
"""
LLM增强处理模块
为解析的题目添加：标签、难度、追问点、向量化等
"""

import os
import json
import logging
from typing import List, Dict, Optional
from dataclasses import asdict
import hashlib

from markdown_parser import Question, CodeExample, parse_markdown_directory

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from services.llm_service import GLM4Service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# 知识图谱标签体系
KNOWLEDGE_GRAPH = {
    "go": {
        "基础": ["变量", "常量", "数据类型", "控制流", "函数", "方法", "接口"],
        "数据结构": ["数组", "slice", "map", "channel", "struct"],
        "并发": ["goroutine", "GMP调度", "锁", "原子操作", "Context"],
        "内存": ["GC", "内存逃逸", "内存对齐", "栈/堆"],
        "标准库": ["HTTP", "JSON", "IO", "反射", "testing"],
        "进阶": ["源码阅读", "性能优化", "调试", "pprof"]
    },
    "mysql": {
        "基础": ["SQL", "数据类型", "索引基础"],
        "进阶": ["B+树", "InnoDB", "MVCC", "事务", "锁"],
        "优化": ["索引优化", "查询优化", "分库分表", "主从复制"],
        "架构": ["高可用", "读写分离", "分片"]
    },
    "redis": {
        "基础": ["数据类型", "命令", "持久化"],
        "进阶": ["底层结构", "集群", "Sentinel", "分布式锁"],
        "场景": ["缓存", "消息队列", "计数器", "限流"],
        "问题": ["穿透", "击穿", "雪崩", "一致性"]
    },
    "network": {
        "基础": ["OSI模型", "TCP/IP", "HTTP/HTTPS"],
        "TCP": ["三次握手", "四次挥手", "滑动窗口", "拥塞控制"],
        "HTTP": ["方法", "状态码", "版本演进", "RPC"],
        "安全": ["HTTPS", "TLS", "证书", "攻击防护"]
    },
    "system": {
        "基础": ["进程", "线程", "协程", "调度"],
        "IO": ["IO模型", "epoll", "零拷贝"],
        "内存": ["虚拟内存", "物理内存", "内存管理"],
        "Linux": ["命令", "文件系统", "进程管理"]
    },
    "system-design": {
        "基础": ["设计原则", "架构模式", "CAP/BASE"],
        "场景": ["秒杀", "短链", "IM", "Feed流", "搜索"],
        "组件": ["负载均衡", "网关", "消息队列", "缓存", "数据库"],
        "分布式": ["一致性", "分布式锁", "分布式ID", "分布式事务"]
    }
}


class LLMEnhancer:
    """LLM增强处理器"""
    
    def __init__(self, cache_dir: str = "/home/fengxu/mylib/interview-agent/backend/data/cache"):
        self.llm = GLM4Service()
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        self.cache = self._load_cache()
    
    def _load_cache(self) -> Dict:
        """加载缓存"""
        cache_file = os.path.join(self.cache_dir, "llm_enhance_cache.json")
        if os.path.exists(cache_file):
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _save_cache(self):
        """保存缓存"""
        cache_file = os.path.join(self.cache_dir, "llm_enhance_cache.json")
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(self.cache, f, ensure_ascii=False, indent=2)
    
    def _get_cache_key(self, question: Question, task: str) -> str:
        """生成缓存key"""
        content = f"{question.text}{question.answer}{task}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _get_cached_or_call(self, question: Question, task: str, prompt_func, **kwargs):
        """获取缓存或调用LLM"""
        import asyncio
        
        cache_key = self._get_cache_key(question, task)
        
        if cache_key in self.cache:
            logger.debug(f"使用缓存: {task}")
            return self.cache[cache_key]
        
        # 调用LLM
        prompt = prompt_func(question, **kwargs)
        try:
            # 运行异步函数
            result = asyncio.run(self.llm.chat_completion(prompt, temperature=0.3))
            self.cache[cache_key] = result
            return result
        except Exception as e:
            logger.error(f"LLM调用失败: {e}")
            return None
    
    def generate_tags(self, question: Question) -> List[str]:
        """生成知识点标签"""
        
        def _prompt(q: Question, **kwargs):
            return f"""分析以下后端面试题，提取3-5个核心技术知识点标签。

问题：{q.text}
答案：{q.answer[:500]}...

要求：
1. 标签要精准，反映核心技术概念
2. 使用中文或英文技术术语（如：Goroutine, B+树, 索引）
3. 标签粒度适中，不要太宽泛（如不要用"编程"这种大标签）
4. 优先从以下领域选择：Go语言、MySQL、Redis、计算机网络、操作系统、系统设计

直接输出标签列表，每行一个，不要有任何解释。
"""
        
        result = self._get_cached_or_call(question, "tags", _prompt)
        
        if result:
            tags = [tag.strip() for tag in result.split('\n') if tag.strip()]
            # 去重和限制数量
            tags = list(dict.fromkeys(tags))[:5]
            return tags
        
        # 回退到规则匹配
        return self._rule_based_tags(question)
    
    def _rule_based_tags(self, question: Question) -> List[str]:
        """基于规则的标签生成"""
        text = f"{question.text} {question.answer}".lower()
        tags = []
        
        tag_keywords = {
            "goroutine": ["goroutine", "协程", "并发"],
            "channel": ["channel", "管道", "通信"],
            "slice": ["slice", "切片", "扩容"],
            "map": ["map", "字典", "hash"],
            "gmp": ["gmp", "调度", "调度器"],
            "gc": ["gc", "垃圾回收", "垃圾收集"],
            "mysql索引": ["索引", "b+树", "innodb"],
            "事务": ["事务", "acid", "隔离级别"],
            "mvcc": ["mvcc", "多版本", "并发控制"],
            "redis": ["redis", "缓存"],
            "tcp": ["tcp", "三次握手", "四次挥手"],
            "http": ["http", "https", "状态码"],
        }
        
        for tag, keywords in tag_keywords.items():
            if any(kw in text for kw in keywords):
                tags.append(tag)
        
        return tags[:5]
    
    def assess_difficulty(self, question: Question) -> int:
        """评估题目难度（1-5）"""
        
        def _prompt(q: Question, **kwargs):
            return f"""评估以下后端面试题的难度等级(1-5)：

参考标准：
1级 - 基础概念，记忆性知识（如：什么是goroutine？）
2级 - 基础应用，简单场景（如：channel如何实现通信？）
3级 - 进阶原理，需要理解（如：GMP调度模型详解）
4级 - 深度原理，源码级别（如：GC三色标记算法实现）
5级 - 系统设计，综合应用（如：设计一个高并发消息队列）

问题：{q.text}
答案长度：{len(q.answer)}字

请只输出数字(1-5)，不要有任何其他内容。
"""
        
        result = self._get_cached_or_call(question, "difficulty", _prompt)
        
        try:
            if result:
                difficulty = int(result.strip())
                return max(1, min(5, difficulty))
        except:
            pass
        
        # 回退到规则评估
        return self._rule_based_difficulty(question)
    
    def _rule_based_difficulty(self, question: Question) -> int:
        """基于规则的难度评估"""
        score = 3  # 默认中等
        answer = question.answer.lower()
        
        # 根据内容深度判断
        depth_indicators = {
            5: ["设计", "架构", "分布式", "高并发", "百万", "千万"],
            4: ["源码", "原理", "实现", "机制", "底层"],
            3: ["优化", "性能", "调优", "解决方案"],
            2: ["使用", "应用", "场景"],
        }
        
        for level, keywords in depth_indicators.items():
            if any(kw in answer for kw in keywords):
                score = max(score, level)
        
        # 根据答案长度调整
        if len(question.answer) < 200:
            score = min(score, 2)
        elif len(question.answer) > 1000:
            score = max(score, 3)
        
        return min(5, score)
    
    def extract_followup_points(self, question: Question) -> List[Dict]:
        """提取追问点"""
        
        def _prompt(q: Question, **kwargs):
            return f"""分析以下面试题，提取2-3个可以追问的点。

问题：{q.text}
答案：{q.answer[:800]}...

追问点类型：
1. 深度追问 - 答案提到了某个概念，可以问其原理
2. 场景追问 - 可以问在实际项目中可能遇到的问题
3. 对比追问 - 可以问与其他技术的对比

输出格式（JSON）：
[
  {{
    "type": "depth",
    "concept": "概念名称",
    "question": "追问问题文本"
  }}
]

只输出JSON数组，不要其他解释。
"""
        
        result = self._get_cached_or_call(question, "followup", _prompt)
        
        try:
            if result:
                points = json.loads(result)
                return points if isinstance(points, list) else []
        except:
            pass
        
        return self._rule_based_followup(question)
    
    def _rule_based_followup(self, question: Question) -> List[Dict]:
        """基于规则的追问点提取"""
        points = []
        text = question.answer.lower()
        
        # 常见的技术概念
        concepts = {
            "goroutine": ("depth", "goroutine的底层实现原理是什么？"),
            "channel": ("depth", "channel的底层数据结构是怎样的？"),
            "slice": ("depth", "slice扩容的详细过程是什么？"),
            "gmp": ("depth", "GMP调度器如何处理阻塞？"),
            "gc": ("depth", "GC的三色标记算法具体如何工作？"),
            "索引": ("scenario", "索引在什么情况下会失效？"),
            "缓存": ("scenario", "如何保证缓存和数据库的一致性？"),
            "tcp": ("depth", "TCP的TIME_WAIT状态是什么作用？"),
        }
        
        for concept, (ftype, qtext) in concepts.items():
            if concept in text:
                points.append({
                    "type": ftype,
                    "concept": concept,
                    "question": qtext
                })
        
        return points[:3]
    
    def generate_embedding_text(self, question: Question) -> str:
        """生成用于向量化的文本"""
        # 组合问题、答案和标签
        text_parts = [
            f"问题: {question.text}",
            f"答案: {question.answer[:1000]}",  # 限制长度
            f"分类: {question.category}",
            f"标签: {', '.join(question.tags)}"
        ]
        
        return "\n".join(text_parts)
    
    def enhance_question(self, question: Question) -> Question:
        """增强单个问题"""
        logger.info(f"增强问题: {question.text[:50]}...")
        
        # 1. 生成标签
        question.tags = self.generate_tags(question)
        
        # 2. 评估难度
        question.difficulty = self.assess_difficulty(question)
        
        # 3. 提取追问点
        followup_data = self.extract_followup_points(question)
        question.followup_points = [p["question"] for p in followup_data]
        
        return question
    
    def enhance_questions(self, questions: List[Question], batch_size: int = 10) -> List[Question]:
        """批量增强问题"""
        enhanced = []
        
        for i, q in enumerate(questions):
            try:
                enhanced_q = self.enhance_question(q)
                enhanced.append(enhanced_q)
                
                # 每处理batch_size个保存一次缓存
                if (i + 1) % batch_size == 0:
                    self._save_cache()
                    logger.info(f"已处理 {i+1}/{len(questions)} 题")
                    
            except Exception as e:
                logger.error(f"增强问题失败: {e}")
                enhanced.append(q)  # 使用原始问题
        
        # 最后保存缓存
        self._save_cache()
        
        return enhanced
    
    def export_to_json(self, questions: List[Question], output_path: str):
        """导出到JSON文件"""
        data = []
        for q in questions:
            q_dict = asdict(q)
            # 转换CodeExample为dict
            q_dict['code_examples'] = [
                asdict(ce) for ce in q.code_examples
            ]
            data.append(q_dict)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"导出 {len(questions)} 题到 {output_path}")


# 便捷函数
def enhance_questions_batch(questions: List[Question]) -> List[Question]:
    """批量增强问题"""
    enhancer = LLMEnhancer()
    return enhancer.enhance_questions(questions)


if __name__ == "__main__":
    # 测试
    import sys
    from pathlib import Path
    
    # 添加父目录到路径
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    if len(sys.argv) > 1:
        # 解析目录
        input_dir = sys.argv[1]
        logger.info(f"解析目录: {input_dir}")
        
        questions = parse_markdown_directory(input_dir)
        logger.info(f"解析完成，共 {len(questions)} 题")
        
        # 增强处理
        enhancer = LLMEnhancer()
        enhanced = enhancer.enhance_questions(questions[:5])  # 先测试5题
        
        # 导出
        output_file = "/home/fengxu/mylib/interview-agent/backend/data/processed/enhanced_questions.json"
        enhancer.export_to_json(enhanced, output_file)
        
        # 打印示例
        for q in enhanced[:2]:
            print(f"\n{'='*50}")
            print(f"问题: {q.text}")
            print(f"分类: {q.category}")
            print(f"难度: {q.difficulty}")
            print(f"标签: {q.tags}")
            print(f"追问点: {q.followup_points}")
