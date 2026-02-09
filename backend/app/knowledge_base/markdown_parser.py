#!/usr/bin/env python3
"""
Markdown面试题解析器
解析GitHub仓库中的Markdown文件，提取结构化面试题
"""

import re
import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QuestionFormat(Enum):
    """问题格式类型"""
    HEADING = "heading"      # 基于标题层级
    LIST = "list"            # 基于列表
    QA = "qa"                # 基于Q&A标记
    MIXED = "mixed"          # 混合格式


@dataclass
class CodeExample:
    """代码示例"""
    code: str
    language: str = ""
    description: str = ""


@dataclass
class Question:
    """面试题数据结构"""
    id: str = ""
    text: str = ""
    answer: str = ""
    category: str = ""           # 分类：Go/MySQL/Redis等
    subcategory: str = ""        # 子分类
    difficulty: int = 3          # 难度：1-5
    tags: List[str] = field(default_factory=list)
    code_examples: List[CodeExample] = field(default_factory=list)
    followup_points: List[str] = field(default_factory=list)
    source_repo: str = ""
    source_file: str = ""
    related_questions: List[str] = field(default_factory=list)


class MarkdownParser:
    """Markdown面试题解析器"""
    
    def __init__(self):
        self.category_keywords = {
            "go": ["goroutine", "channel", "golang", "gpm", "gc", "slice", "map"],
            "mysql": ["mysql", "innodb", "mvcc", "索引", "b+树", "事务"],
            "redis": ["redis", "缓存", "rdb", "aof", "数据结构"],
            "network": ["tcp", "udp", "http", "https", "网络", "socket"],
            "system": ["linux", "操作系统", "进程", "线程", "io", "epoll"],
            "algorithm": ["算法", "排序", "链表", "树", "hash"],
            "system-design": ["设计", "架构", "分布式", "微服务", "高并发"]
        }
    
    def parse_file(self, file_path: Path, repo_name: str = "") -> List[Question]:
        """
        解析单个Markdown文件
        """
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            logger.error(f"读取文件失败 {file_path}: {e}")
            return []
        
        # 检测格式类型
        format_type = self._detect_format(content)
        logger.debug(f"文件 {file_path.name} 格式类型: {format_type}")
        
        # 根据格式解析
        if format_type == QuestionFormat.HEADING:
            questions = self._parse_by_headings(content, file_path, repo_name)
        elif format_type == QuestionFormat.LIST:
            questions = self._parse_by_lists(content, file_path, repo_name)
        elif format_type == QuestionFormat.QA:
            questions = self._parse_by_qa(content, file_path, repo_name)
        else:
            questions = self._parse_mixed(content, file_path, repo_name)
        
        # 后处理
        questions = self._post_process(questions, file_path, repo_name)
        
        return questions
    
    def _detect_format(self, content: str) -> QuestionFormat:
        """检测Markdown格式类型"""
        # 检查是否有Q&A标记
        if re.search(r'^[QA]\s*[:：]', content, re.MULTILINE):
            return QuestionFormat.QA
        
        # 检查是否有大量列表项作为问题
        list_pattern = r'^[-*]\s+[^\n]+(\n\s+[^\n]+)*'
        list_matches = len(re.findall(list_pattern, content, re.MULTILINE))
        
        # 检查标题层级
        heading_pattern = r'^#{2,4}\s+'
        heading_matches = len(re.findall(heading_pattern, content, re.MULTILINE))
        
        if list_matches > heading_matches * 2:
            return QuestionFormat.LIST
        elif heading_matches > 5:
            return QuestionFormat.HEADING
        else:
            return QuestionFormat.MIXED
    
    def _parse_by_headings(self, content: str, file_path: Path, repo_name: str) -> List[Question]:
        """基于标题层级解析"""
        questions = []
        
        # 按二级标题分割
        sections = re.split(r'\n(?=##\s+)', content)
        
        for section in sections:
            if not section.strip():
                continue
            
            # 提取标题作为问题
            heading_match = re.match(r'##\s+(.+)$', section, re.MULTILINE)
            if not heading_match:
                continue
            
            question_text = heading_match.group(1).strip()
            
            # 剩余内容作为答案
            answer_content = re.sub(r'##\s+.+$', '', section, flags=re.MULTILINE).strip()
            
            # 提取代码块
            code_examples = self._extract_code_blocks(answer_content)
            
            # 清理答案文本
            answer_text = self._clean_content(answer_content)
            
            if question_text and len(answer_text) > 50:
                questions.append(Question(
                    text=question_text,
                    answer=answer_text,
                    code_examples=code_examples,
                    source_repo=repo_name,
                    source_file=str(file_path)
                ))
        
        return questions
    
    def _parse_by_lists(self, content: str, file_path: Path, repo_name: str) -> List[Question]:
        """基于列表格式解析"""
        questions = []
        
        # 匹配列表项作为问题
        pattern = r'^[-*]\s+(.+?)(?=\n[-*]|\n#{2,}|\Z)'
        matches = re.finditer(pattern, content, re.MULTILINE | re.DOTALL)
        
        for match in matches:
            item_content = match.group(1).strip()
            
            # 尝试分离问题和答案
            lines = item_content.split('\n')
            question_text = lines[0].strip()
            
            # 答案可能是缩进的内容
            answer_lines = []
            for line in lines[1:]:
                if line.startswith('  ') or line.startswith('\t'):
                    answer_lines.append(line.strip())
            
            answer_text = '\n'.join(answer_lines) if answer_lines else item_content
            
            # 提取代码块
            code_examples = self._extract_code_blocks(answer_text)
            answer_text = self._clean_content(answer_text)
            
            if len(answer_text) > 50:
                questions.append(Question(
                    text=question_text,
                    answer=answer_text,
                    code_examples=code_examples,
                    source_repo=repo_name,
                    source_file=str(file_path)
                ))
        
        return questions
    
    def _parse_by_qa(self, content: str, file_path: Path, repo_name: str) -> List[Question]:
        """基于Q&A标记解析"""
        questions = []
        
        # 匹配 Q: / A: 格式
        pattern = r'^[QA]\s*[:：]\s*(.+?)(?=^[QA]\s*[:：]|\Z)'
        matches = re.finditer(pattern, content, re.MULTILINE | re.DOTALL)
        
        qa_pairs = []
        current_q = None
        
        for match in matches:
            text = match.group(1).strip()
            marker = match.group(0)[0].upper()
            
            if marker == 'Q':
                if current_q:
                    qa_pairs.append((current_q, ""))
                current_q = text
            elif marker == 'A' and current_q:
                qa_pairs.append((current_q, text))
                current_q = None
        
        for q_text, a_text in qa_pairs:
            code_examples = self._extract_code_blocks(a_text)
            a_text = self._clean_content(a_text)
            
            questions.append(Question(
                text=q_text,
                answer=a_text,
                code_examples=code_examples,
                source_repo=repo_name,
                source_file=str(file_path)
            ))
        
        return questions
    
    def _parse_mixed(self, content: str, file_path: Path, repo_name: str) -> List[Question]:
        """混合格式解析"""
        # 尝试多种策略，选择效果最好的一种
        questions = []
        
        # 尝试按段落分割，检测问题模式
        paragraphs = re.split(r'\n\n+', content)
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            # 检查是否像问题（包含问号、疑问词等）
            if self._looks_like_question(para):
                lines = para.split('\n')
                question_text = lines[0]
                answer_text = '\n'.join(lines[1:]) if len(lines) > 1 else para
                
                code_examples = self._extract_code_blocks(answer_text)
                answer_text = self._clean_content(answer_text)
                
                if len(answer_text) > 30:
                    questions.append(Question(
                        text=question_text,
                        answer=answer_text,
                        code_examples=code_examples,
                        source_repo=repo_name,
                        source_file=str(file_path)
                    ))
        
        return questions
    
    def _looks_like_question(self, text: str) -> bool:
        """判断文本是否像问题"""
        question_indicators = [
            r'[？?]$',  # 以问号结尾
            r'^(什么|为什么|如何|怎么|什么是|为什么|请解释|简述)',
            r'^(what|why|how|explain|describe|what\s+is)',
            r'[的\s]+区别[是\?]*',
            r'[的\s]+原理[是\?]*'
        ]
        
        for pattern in question_indicators:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    def _extract_code_blocks(self, content: str) -> List[CodeExample]:
        """提取代码块"""
        code_examples = []
        
        # 匹配代码块
        pattern = r'```(\w+)?\n(.*?)```'
        matches = re.finditer(pattern, content, re.DOTALL)
        
        for match in matches:
            language = match.group(1) or ""
            code = match.group(2).strip()
            
            if code:
                code_examples.append(CodeExample(
                    code=code,
                    language=language
                ))
        
        return code_examples
    
    def _clean_content(self, content: str) -> str:
        """清理内容"""
        # 移除代码块
        content = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
        
        # 移除HTML标签
        content = re.sub(r'<[^>]+>', '', content)
        
        # 规范化空白
        content = re.sub(r'\n+', '\n', content)
        content = re.sub(r'\s+', ' ', content)
        
        return content.strip()
    
    def _post_process(self, questions: List[Question], file_path: Path, repo_name: str) -> List[Question]:
        """后处理"""
        processed = []
        
        for i, q in enumerate(questions):
            # 生成分类
            q.category = self._categorize_question(q.text, q.answer)
            
            # 生成ID
            q.id = f"{repo_name}_{file_path.stem}_{i:03d}"
            
            # 过滤质量差的题目
            if len(q.answer) < 50 or len(q.text) < 10:
                continue
            
            processed.append(q)
        
        return processed
    
    def _categorize_question(self, question: str, answer: str) -> str:
        """根据内容分类"""
        text = f"{question} {answer}".lower()
        
        category_scores = {}
        for category, keywords in self.category_keywords.items():
            score = sum(1 for kw in keywords if kw in text)
            if score > 0:
                category_scores[category] = score
        
        if category_scores:
            return max(category_scores.items(), key=lambda x: x[1])[0]
        
        return "general"
    
    def parse_directory(self, dir_path: Path, repo_name: str = "") -> List[Question]:
        """解析整个目录"""
        all_questions = []
        
        for md_file in dir_path.rglob("*.md"):
            if "node_modules" in str(md_file) or ".git" in str(md_file):
                continue
            
            questions = self.parse_file(md_file, repo_name)
            all_questions.extend(questions)
            logger.info(f"解析 {md_file.relative_to(dir_path)}: {len(questions)} 题")
        
        return all_questions


# 便捷函数
def parse_markdown_file(file_path: str, repo_name: str = "") -> List[Question]:
    """解析单个Markdown文件"""
    parser = MarkdownParser()
    return parser.parse_file(Path(file_path), repo_name)


def parse_markdown_directory(dir_path: str, repo_name: str = "") -> List[Question]:
    """解析整个目录"""
    parser = MarkdownParser()
    return parser.parse_directory(Path(dir_path), repo_name)



if __name__ == "__main__":
    # 测试解析
    import sys
    
    if len(sys.argv) > 1:
        test_path = Path(sys.argv[1])
        if test_path.is_file():
            questions = parse_markdown_file(str(test_path))
        else:
            questions = parse_markdown_directory(str(test_path))
        
        print(f"共解析 {len(questions)} 道题目")
        for i, q in enumerate(questions[:3]):
            print(f"\n题目 {i+1}:")
            print(f"问题: {q.text[:100]}...")
            print(f"分类: {q.category}")
            print(f"代码示例: {len(q.code_examples)} 个")
