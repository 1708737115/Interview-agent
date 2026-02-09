#!/usr/bin/env python3
"""
牛客面经风格学习模块
爬取牛客面试经验帖子，提取面试官风格和追问模式
"""

import os
import re
import json
import logging
import asyncio
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, field, asdict

import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 配置
DATA_DIR = Path("/home/fengxu/mylib/interview-agent/backend/data/nowcoder")
DATA_DIR.mkdir(parents=True, exist_ok=True)

# 牛客面经URL模板
NOWCODER_URLS = {
    "backend": "https://www.nowcoder.com/discuss?type=2&order=time&page={}",
    "java": "https://www.nowcoder.com/discuss?type=2&tagId=644&order=time&page={}",
    "go": "https://www.nowcoder.com/discuss?type=2&tagId=20264&order=time&page={}",
}


@dataclass
class InterviewPost:
    """面试帖子数据结构"""
    id: str
    title: str
    content: str
    company: str = ""           # 面试公司
    position: str = ""          # 岗位
    interview_rounds: List[Dict] = field(default_factory=list)  # 面试轮次
    questions: List[str] = field(default_factory=list)          # 面试问题
    interviewer_quotes: List[str] = field(default_factory=list) # 面试官话术
    followup_patterns: List[str] = field(default_factory=list)  # 追问模式
    process_description: str = ""  # 流程描述
    source_url: str = ""
    created_at: str = ""


class NowcoderCrawler:
    """牛客面经爬虫"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def fetch_post_list(self, category: str = "backend", page: int = 1) -> List[Dict]:
        """
        获取帖子列表
        
        Args:
            category: 分类（backend/java/go）
            page: 页码
            
        Returns:
            帖子列表
        """
        url = NOWCODER_URLS.get(category, NOWCODER_URLS["backend"]).format(page)
        
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code != 200:
                logger.error(f"获取列表失败: {response.status_code}")
                return []
            
            # 解析HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            posts = []
            
            # 查找帖子元素
            for item in soup.find_all('div', class_='discuss-item'):
                try:
                    # 提取基本信息
                    title_elem = item.find('a', class_='discuss-title')
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    post_url = title_elem.get('href', '')
                    
                    # 过滤非面经帖子
                    if not self._is_interview_post(title):
                        continue
                    
                    # 提取元数据
                    meta = item.find('div', class_='discuss-meta')
                    company = ""
                    position = ""
                    
                    if meta:
                        # 尝试提取公司和岗位
                        tags = meta.find_all('span', class_='tag')
                        for tag in tags:
                            text = tag.get_text(strip=True)
                            if '面试' in text or '面经' in text:
                                continue
                            if not company:
                                company = text
                            elif not position:
                                position = text
                    
                    posts.append({
                        'id': self._extract_post_id(post_url),
                        'title': title,
                        'url': f"https://www.nowcoder.com{post_url}" if post_url.startswith('/') else post_url,
                        'company': company,
                        'position': position
                    })
                    
                except Exception as e:
                    logger.error(f"解析帖子项失败: {e}")
                    continue
            
            return posts
            
        except Exception as e:
            logger.error(f"获取列表失败: {e}")
            return []
    
    def _is_interview_post(self, title: str) -> bool:
        """判断是否为面试经验帖子"""
        keywords = ['面经', '面试', 'offer', '校招', '秋招', '春招', '实习']
        return any(kw in title for kw in keywords)
    
    def _extract_post_id(self, url: str) -> str:
        """从URL中提取帖子ID"""
        match = re.search(r'/discuss/(\d+)', url)
        return match.group(1) if match else ""
    
    def fetch_post_detail(self, post_url: str) -> Optional[str]:
        """获取帖子详情内容"""
        try:
            response = self.session.get(post_url, timeout=15)
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找内容区域
            content_elem = soup.find('div', class_='post-content')
            if not content_elem:
                content_elem = soup.find('div', {'data-v-3': True})  # 尝试其他选择器
            
            if content_elem:
                return content_elem.get_text(separator='\n', strip=True)
            
            return None
            
        except Exception as e:
            logger.error(f"获取帖子详情失败: {e}")
            return None
    
    def crawl_interview_posts(self, max_posts: int = 50) -> List[InterviewPost]:
        """
        爬取面试帖子
        
        Args:
            max_posts: 最大爬取数量
            
        Returns:
            面试帖子列表
        """
        logger.info(f"开始爬取牛客面经，目标数量: {max_posts}")
        
        all_posts = []
        page = 1
        
        while len(all_posts) < max_posts and page <= 10:
            logger.info(f"正在获取第 {page} 页...")
            
            posts = self.fetch_post_list("backend", page)
            if not posts:
                break
            
            for post_info in posts:
                if len(all_posts) >= max_posts:
                    break
                
                logger.info(f"获取详情: {post_info['title'][:50]}...")
                
                # 获取详情
                content = self.fetch_post_detail(post_info['url'])
                if not content or len(content) < 200:
                    continue
                
                # 创建帖子对象
                interview_post = InterviewPost(
                    id=post_info['id'],
                    title=post_info['title'],
                    content=content,
                    company=post_info.get('company', ''),
                    position=post_info.get('position', ''),
                    source_url=post_info['url'],
                    created_at=datetime.now().isoformat()
                )
                
                all_posts.append(interview_post)
                logger.info(f"✓ 已获取 {len(all_posts)}/{max_posts}")
                
                # 添加延迟
                import time
                time.sleep(2)
            
            page += 1
            time.sleep(3)
        
        logger.info(f"爬取完成，共 {len(all_posts)} 篇面经")
        return all_posts


class InterviewStyleAnalyzer:
    """面试风格分析器"""
    
    def __init__(self):
        self.llm = None
    
    def analyze_post(self, post: InterviewPost) -> Dict:
        """
        分析单个面经帖子，提取面试官风格
        
        Args:
            post: 面试帖子
            
        Returns:
            风格分析结果
        """
        # 1. 提取面试官话术
        interviewer_quotes = self._extract_interviewer_quotes(post.content)
        post.interviewer_quotes = interviewer_quotes
        
        # 2. 提取面试问题
        questions = self._extract_questions(post.content)
        post.questions = questions
        
        # 3. 提取追问模式
        followup_patterns = self._extract_followup_patterns(post.content)
        post.followup_patterns = followup_patterns
        
        # 4. 分析面试流程
        interview_rounds = self._extract_interview_rounds(post.content)
        post.interview_rounds = interview_rounds
        
        return {
            'post_id': post.id,
            'title': post.title,
            'company': post.company,
            'position': post.position,
            'total_quotes': len(interviewer_quotes),
            'total_questions': len(questions),
            'total_followups': len(followup_patterns),
            'interview_rounds': len(interview_rounds),
            'interviewer_quotes': interviewer_quotes[:10],  # 只保留前10个
            'questions': questions[:20],  # 只保留前20个问题
            'followup_patterns': followup_patterns[:10],  # 只保留前10个
        }
    
    def _extract_interviewer_quotes(self, content: str) -> List[str]:
        """提取面试官话术"""
        quotes = []
        
        # 匹配常见的面试官话术模式
        patterns = [
            r'面试官[说问]*[:：]\s*([^\n。]+[。?？])',
            r'面试官[:：]?\s*["""]([^"""]+)["""]',
            r'[问Q][:：]\s*([^\n。]+[。?？])',
            r'["""]([^"""]{10,100})["""]',  # 引号中的话
            r'面试官让我([^\n。]+)',
            r'面试官问[我道]*[:：]?\s*([^\n。]+)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                quote = match.strip()
                if len(quote) > 10 and len(quote) < 200:
                    quotes.append(quote)
        
        # 去重
        return list(dict.fromkeys(quotes))
    
    def _extract_questions(self, content: str) -> List[str]:
        """提取面试问题"""
        questions = []
        
        # 匹配问题模式
        patterns = [
            r'[问Q][:：]\s*([^\n。]+[?？])',
            r'面试官问[:：]?\s*([^\n。]+[?？])',
            r'[问]([^\n]{10,100}[?？])',
            r'(?:什么是|为什么|怎么|如何|简述|介绍一下)([^\n。]{10,100}[?？])',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                question = match.strip()
                if len(question) > 10 and len(question) < 150:
                    questions.append(question)
        
        return list(dict.fromkeys(questions))
    
    def _extract_followup_patterns(self, content: str) -> List[str]:
        """提取追问模式"""
        patterns = []
        
        # 匹配追问话术
        followup_keywords = [
            '接着问', '然后问', '继续问', '追问', '深挖', '延伸到',
            '进一步问', '继续追问', '又问我', '还问了'
        ]
        
        for keyword in followup_keywords:
            # 找到关键词附近的文本
            regex = f'{keyword}[:：]?\s*([^\n。]{10,100})'
            matches = re.findall(regex, content)
            patterns.extend(matches)
        
        return patterns[:20]
    
    def _extract_interview_rounds(self, content: str) -> List[Dict]:
        """提取面试轮次"""
        rounds = []
        
        # 匹配常见的轮次描述
        round_patterns = [
            r'(一面|二面|三面|HR面|技术一面|技术二面)[：:]?\s*([^\n]{50,500})',
            r'(第[一二三]轮|终面|初试|复试)[：:]?\s*([^\n]{50,500})',
        ]
        
        for pattern in round_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                round_name = match[0]
                round_desc = match[1]
                
                rounds.append({
                    'name': round_name,
                    'description': round_desc[:200],
                    'duration': self._estimate_duration(round_desc),
                    'focus': self._extract_focus(round_desc)
                })
        
        return rounds
    
    def _estimate_duration(self, desc: str) -> str:
        """估算面试时长"""
        if '分钟' in desc:
            match = re.search(r'(\d+)\s*分钟', desc)
            if match:
                return f"{match.group(1)}分钟"
        
        if '小时' in desc:
            match = re.search(r'(\d+)\s*小时', desc)
            if match:
                return f"{match.group(1)}小时"
        
        return "未知"
    
    def _extract_focus(self, desc: str) -> List[str]:
        """提取面试重点"""
        focus_areas = []
        
        keywords = {
            '基础': ['基础', '八股文', '概念'],
            '项目': ['项目', '实习', '经历'],
            '算法': ['算法', 'leetcode', '代码', '编程'],
            '设计': ['设计', '架构', '系统设计'],
            '场景': ['场景', '业务', '实际问题']
        }
        
        for area, words in keywords.items():
            if any(word in desc for word in words):
                focus_areas.append(area)
        
        return focus_areas
    
    def generate_style_profile(self, posts: List[InterviewPost]) -> Dict:
        """
        基于所有面经生成面试官风格画像
        
        Args:
            posts: 面试帖子列表
            
        Returns:
            风格画像
        """
        # 收集所有数据
        all_quotes = []
        all_questions = []
        all_followups = []
        all_rounds = []
        
        for post in posts:
            all_quotes.extend(post.interviewer_quotes)
            all_questions.extend(post.questions)
            all_followups.extend(post.followup_patterns)
            all_rounds.extend(post.interview_rounds)
        
        # 统计
        style_profile = {
            'total_posts_analyzed': len(posts),
            'total_interviewer_quotes': len(all_quotes),
            'total_questions': len(all_questions),
            'total_followups': len(all_followups),
            'avg_questions_per_interview': len(all_questions) / len(posts) if posts else 0,
            'avg_followups_per_interview': len(all_followups) / len(posts) if posts else 0,
            
            # 提问风格分析
            'questioning_style': self._analyze_questioning_style(all_quotes),
            
            # 追问模式分析
            'followup_patterns': self._analyze_followup_patterns(all_followups),
            
            # 面试流程分析
            'interview_flow': self._analyze_interview_flow(all_rounds),
            
            # 常见话术模板
            'common_phrases': self._extract_common_phrases(all_quotes),
            
            # 热门面试题
            'popular_questions': self._get_popular_questions(all_questions, top_n=20),
            
            # 生成时间
            'generated_at': datetime.now().isoformat()
        }
        
        return style_profile
    
    def _analyze_questioning_style(self, quotes: List[str]) -> Dict:
        """分析提问风格"""
        direct_count = 0
        guiding_count = 0
        
        direct_patterns = ['直接', '问你', '说说', '讲一下', '介绍一下']
        guiding_patterns = ['你觉得', '你怎么看', '你的想法', '请描述', '能否']
        
        for quote in quotes:
            if any(p in quote for p in direct_patterns):
                direct_count += 1
            if any(p in quote for p in guiding_patterns):
                guiding_count += 1
        
        total = len(quotes) if quotes else 1
        
        return {
            'direct_ratio': direct_count / total,
            'guiding_ratio': guiding_count / total,
            'dominant_style': 'direct' if direct_count > guiding_count else 'guiding'
        }
    
    def _analyze_followup_patterns(self, followups: List[str]) -> Dict:
        """分析追问模式"""
        triggers = {
            'incomplete': ['继续', '还有', '补充', '详细'],
            'wrong': ['不对', '错误', '问题', '但是'],
            'deep': ['为什么', '原理', '底层', '怎么实现'],
            'scenario': ['场景', '实际', '如果', '假设']
        }
        
        trigger_counts = {k: 0 for k in triggers.keys()}
        
        for followup in followups:
            for trigger_type, keywords in triggers.items():
                if any(kw in followup for kw in keywords):
                    trigger_counts[trigger_type] += 1
        
        return {
            'trigger_types': trigger_counts,
            'avg_followup_depth': len(followups) / len(trigger_counts) if trigger_counts else 0
        }
    
    def _analyze_interview_flow(self, rounds: List[Dict]) -> Dict:
        """分析面试流程"""
        round_types = {}
        focus_areas = {}
        
        for round_info in rounds:
            name = round_info.get('name', '未知')
            round_types[name] = round_types.get(name, 0) + 1
            
            for focus in round_info.get('focus', []):
                focus_areas[focus] = focus_areas.get(focus, 0) + 1
        
        return {
            'common_rounds': round_types,
            'common_focus_areas': focus_areas,
            'avg_rounds_per_interview': len(rounds) / len(round_types) if round_types else 0
        }
    
    def _extract_common_phrases(self, quotes: List[str]) -> List[str]:
        """提取常见话术"""
        # 简单的统计频率
        phrase_counts = {}
        
        for quote in quotes:
            # 提取关键词组合
            words = quote.split()
            for i in range(len(words) - 1):
                phrase = words[i] + words[i+1]
                phrase_counts[phrase] = phrase_counts.get(phrase, 0) + 1
        
        # 返回高频短语
        sorted_phrases = sorted(phrase_counts.items(), key=lambda x: x[1], reverse=True)
        return [phrase for phrase, count in sorted_phrases[:10] if count > 1]
    
    def _get_popular_questions(self, questions: List[str], top_n: int = 20) -> List[str]:
        """获取热门面试题"""
        # 基于相似度聚类（简化版：统计关键词）
        keyword_counts = {}
        
        for question in questions:
            keywords = self._extract_keywords(question)
            for kw in keywords:
                keyword_counts[kw] = keyword_counts.get(kw, 0) + 1
        
        # 返回高频问题
        sorted_questions = sorted(
            [(q, sum(keyword_counts.get(kw, 0) for kw in self._extract_keywords(q))) 
             for q in questions],
            key=lambda x: x[1],
            reverse=True
        )
        
        return [q for q, _ in sorted_questions[:top_n]]
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 技术关键词
        tech_keywords = [
            'goroutine', 'channel', 'mysql', 'redis', '索引', '事务', '并发',
            '锁', 'gc', 'map', 'slice', 'tcp', 'http', '算法', '排序',
            '分布式', '架构', '设计', '优化', '性能'
        ]
        
        found = []
        text_lower = text.lower()
        for kw in tech_keywords:
            if kw in text_lower:
                found.append(kw)
        
        return found


def save_posts(posts: List[InterviewPost], output_dir: Path):
    """保存帖子数据"""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 保存为JSON
    posts_data = []
    for post in posts:
        posts_data.append(asdict(post))
    
    output_file = output_dir / "interview_posts.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(posts_data, f, ensure_ascii=False, indent=2)
    
    logger.info(f"保存 {len(posts)} 篇面经到 {output_file}")


def save_style_profile(profile: Dict, output_dir: Path):
    """保存风格画像"""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "interview_style_profile.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(profile, f, ensure_ascii=False, indent=2)
    
    logger.info(f"保存风格画像到 {output_file}")


async def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="牛客面经风格学习")
    parser.add_argument("--max-posts", type=int, default=50, help="爬取帖子数量")
    parser.add_argument("--skip-crawl", action="store_true", help="跳过爬取，使用已有数据")
    args = parser.parse_args()
    
    posts = []
    
    # 步骤1: 爬取数据
    if not args.skip_crawl:
        logger.info("=" * 60)
        logger.info("步骤1: 爬取牛客面经")
        logger.info("=" * 60)
        
        crawler = NowcoderCrawler()
        posts = crawler.crawl_interview_posts(max_posts=args.max_posts)
        
        # 保存原始数据
        save_posts(posts, DATA_DIR)
    else:
        # 加载已有数据
        posts_file = DATA_DIR / "interview_posts.json"
        if posts_file.exists():
            with open(posts_file, 'r', encoding='utf-8') as f:
                posts_data = json.load(f)
                posts = [InterviewPost(**p) for p in posts_data]
            logger.info(f"加载 {len(posts)} 篇已有面经")
        else:
            logger.error("没有已有数据，请先爬取")
            return
    
    # 步骤2: 分析风格
    if posts:
        logger.info("\n" + "=" * 60)
        logger.info("步骤2: 分析面试官风格")
        logger.info("=" * 60)
        
        analyzer = InterviewStyleAnalyzer()
        
        # 分析每个帖子
        for i, post in enumerate(posts):
            logger.info(f"分析帖子 {i+1}/{len(posts)}: {post.title[:50]}...")
            analyzer.analyze_post(post)
        
        # 生成风格画像
        logger.info("\n生成风格画像...")
        style_profile = analyzer.generate_style_profile(posts)
        
        # 保存风格画像
        save_style_profile(style_profile, DATA_DIR)
        
        # 打印摘要
        logger.info("\n" + "=" * 60)
        logger.info("分析结果摘要")
        logger.info("=" * 60)
        logger.info(f"分析帖子数: {style_profile['total_posts_analyzed']}")
        logger.info(f"面试官话术: {style_profile['total_interviewer_quotes']} 条")
        logger.info(f"面试问题: {style_profile['total_questions']} 个")
        logger.info(f"追问模式: {style_profile['total_followups']} 个")
        logger.info(f"平均每场面试题: {style_profile['avg_questions_per_interview']:.1f}")
        logger.info(f"提问风格: {style_profile['questioning_style']['dominant_style']}")
        logger.info(f"\n热门面试题TOP5:")
        for i, q in enumerate(style_profile['popular_questions'][:5], 1):
            logger.info(f"  {i}. {q[:80]}...")


if __name__ == "__main__":
    asyncio.run(main())
