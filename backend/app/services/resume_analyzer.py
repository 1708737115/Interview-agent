#!/usr/bin/env python3
"""
LLM简历解析服务
深度解析简历，提取结构化信息，生成面试策略
"""

import os
import re
import json
import logging
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime

import PyPDF2
from docx import Document

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 添加路径
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))
from services.llm_service import GLM4Service


@dataclass
class ResumeData:
    """简历数据结构"""
    id: str = ""
    raw_text: str = ""
    
    # 基本信息
    name: str = ""
    phone: str = ""
    email: str = ""
    
    # 教育背景
    education: List[Dict] = field(default_factory=list)
    
    # 工作经历
    work_experience: List[Dict] = field(default_factory=list)
    
    # 技能栈
    skills: Dict[str, List[str]] = field(default_factory=dict)
    
    # 项目经历
    projects: List[Dict] = field(default_factory=list)
    
    # 分析结果
    estimated_level: str = ""  # 初级/中级/高级
    years_of_experience: float = 0.0
    skill_gaps: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    
    # 面试策略
    interview_strategy: Dict = field(default_factory=dict)
    
    # 元数据
    source_file: str = ""
    parsed_at: str = ""


class ResumeParser:
    """简历文本提取器"""
    
    def __init__(self):
        pass
    
    def parse_pdf(self, file_path: str) -> str:
        """解析PDF文件"""
        try:
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text
        except Exception as e:
            logger.error(f"PDF解析失败: {e}")
            return ""
    
    def parse_docx(self, file_path: str) -> str:
        """解析DOCX文件"""
        try:
            doc = Document(file_path)
            text = ""
            for para in doc.paragraphs:
                text += para.text + "\n"
            return text
        except Exception as e:
            logger.error(f"DOCX解析失败: {e}")
            return ""
    
    def parse_file(self, file_path: str) -> str:
        """根据文件类型解析"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            logger.error(f"文件不存在: {file_path}")
            return ""
        
        suffix = file_path.suffix.lower()
        
        if suffix == '.pdf':
            return self.parse_pdf(str(file_path))
        elif suffix in ['.docx', '.doc']:
            return self.parse_docx(str(file_path))
        elif suffix == '.txt':
            return file_path.read_text(encoding='utf-8')
        else:
            logger.error(f"不支持的文件格式: {suffix}")
            return ""


class LLMResumeAnalyzer:
    """LLM简历分析器"""
    
    def __init__(self):
        self.llm = GLM4Service()
        self.cache = {}
        self.cache_dir = Path("/home/fengxu/mylib/interview-agent/backend/data/cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._load_cache()
    
    def _load_cache(self):
        """加载缓存"""
        cache_file = self.cache_dir / "resume_parse_cache.json"
        if cache_file.exists():
            with open(cache_file, 'r', encoding='utf-8') as f:
                self.cache = json.load(f)
    
    def _save_cache(self):
        """保存缓存"""
        cache_file = self.cache_dir / "resume_parse_cache.json"
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(self.cache, f, ensure_ascii=False, indent=2)
    
    def _get_cache_key(self, text: str) -> str:
        """生成缓存key"""
        return hashlib.md5(text[:1000].encode()).hexdigest()
    
    async def analyze_resume(self, resume_text: str) -> ResumeData:
        """
        完整分析简历
        """
        logger.info("开始分析简历...")
        
        resume_data = ResumeData(
            id=self._get_cache_key(resume_text),
            raw_text=resume_text,
            parsed_at=datetime.now().isoformat()
        )
        
        # 步骤1: 结构化提取
        logger.info("步骤1: 结构化信息提取...")
        structured_info = await self._extract_structured_info(resume_text)
        
        resume_data.name = structured_info.get('name', '')
        resume_data.phone = structured_info.get('phone', '')
        resume_data.email = structured_info.get('email', '')
        resume_data.education = structured_info.get('education', [])
        resume_data.work_experience = structured_info.get('work_experience', [])
        resume_data.skills = structured_info.get('skills', {})
        resume_data.projects = structured_info.get('projects', [])
        
        # 步骤2: 能力评估
        logger.info("步骤2: 能力评估...")
        assessment = await self._assess_candidate(resume_text, structured_info)
        
        resume_data.estimated_level = assessment.get('level', '中级')
        resume_data.years_of_experience = assessment.get('years_of_experience', 0)
        resume_data.strengths = assessment.get('strengths', [])
        resume_data.skill_gaps = assessment.get('skill_gaps', [])
        
        # 步骤3: 生成面试策略
        logger.info("步骤3: 生成面试策略...")
        strategy = await self._generate_interview_strategy(resume_data)
        resume_data.interview_strategy = strategy
        
        logger.info("简历分析完成！")
        return resume_data
    
    async def _extract_structured_info(self, resume_text: str) -> Dict:
        """提取结构化信息"""
        cache_key = f"structured_{self._get_cache_key(resume_text)}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        prompt = f"""请从以下简历中提取结构化信息，以JSON格式返回：

简历内容：
{resume_text[:3000]}...

请提取以下信息（JSON格式）：
{{
    "name": "姓名",
    "phone": "电话",
    "email": "邮箱",
    "education": [
        {{
            "school": "学校名称",
            "major": "专业",
            "degree": "学历（本科/硕士/博士）",
            "graduation_year": "毕业年份"
        }}
    ],
    "work_experience": [
        {{
            "company": "公司名称",
            "position": "职位",
            "duration": "工作时长",
            "responsibilities": ["职责1", "职责2"],
            "achievements": ["成果1", "成果2"]
        }}
    ],
    "skills": {{
        "programming_languages": ["Java", "Go", "Python"],
        "frameworks": ["Spring Boot", "Gin"],
        "databases": ["MySQL", "Redis"],
        "middleware": ["Kafka", "RocketMQ"],
        "tools": ["Git", "Docker", "K8s"]
    }},
    "projects": [
        {{
            "name": "项目名称",
            "description": "项目描述",
            "tech_stack": ["技术1", "技术2"],
            "role": "角色",
            "highlights": ["亮点1", "亮点2"],
            "challenges": ["挑战1", "挑战2"]
        }}
    ]
}}

注意：
1. 只返回JSON格式，不要有其他文字
2. 如果某部分信息缺失，返回空数组或空字符串
3. 技能部分尽可能详细，包括编程语言、框架、数据库、中间件等
"""
        
        try:
            response = await self.llm.chat_completion(
                [{"role": "user", "content": prompt}],
                temperature=0.1
            )
            
            # 清理响应文本，提取JSON部分
            response_text = response.strip()
            
            # 移除Markdown代码块标记
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            
            response_text = response_text.strip()
            
            # 解析JSON
            result = json.loads(response_text)
            self.cache[cache_key] = result
            self._save_cache()
            return result
            
        except Exception as e:
            logger.error(f"结构化提取失败: {e}")
            logger.debug(f"原始响应: {response[:500] if 'response' in locals() else 'N/A'}")
            return {}
    
    async def _assess_candidate(self, resume_text: str, structured_info: Dict) -> Dict:
        """评估候选人能力"""
        cache_key = f"assess_{self._get_cache_key(resume_text)}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        prompt = f"""请评估以下后端开发候选人，以JSON格式返回评估结果：

简历信息：
教育背景：{json.dumps(structured_info.get('education', []), ensure_ascii=False)}
工作经历：{json.dumps(structured_info.get('work_experience', []), ensure_ascii=False)}
技能栈：{json.dumps(structured_info.get('skills', {}), ensure_ascii=False)}
项目经历：{json.dumps(structured_info.get('projects', []), ensure_ascii=False)}

请评估以下内容（JSON格式）：
{{
    "level": "初级/中级/高级",
    "years_of_experience": 3.5,
    "reasoning": "评估理由（100字左右）",
    "strengths": ["优势1", "优势2", "优势3"],
    "skill_gaps": ["知识缺口1", "知识缺口2"],
    "project_quality": "项目质量评价（高/中/低）",
    "tech_depth": "技术深度评价（高/中/低）",
    "recommendation": "面试建议"
}}

评估标准：
- 初级：0-2年经验，掌握基础技术栈，做过简单项目
- 中级：2-5年经验，熟悉主流框架，有复杂项目经验
- 高级：5年以上经验，精通原理，有架构设计经验
"""
        
        try:
            response = await self.llm.chat_completion(
                [{"role": "user", "content": prompt}],
                temperature=0.2
            )
            
            # 清理响应文本
            response_text = response.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            result = json.loads(response_text)
            self.cache[cache_key] = result
            self._save_cache()
            return result
            
        except Exception as e:
            logger.error(f"能力评估失败: {e}")
            return {
                "level": "中级",
                "years_of_experience": 0,
                "strengths": [],
                "skill_gaps": []
            }
    
    async def _generate_interview_strategy(self, resume_data: ResumeData) -> Dict:
        """生成面试策略"""
        skills = resume_data.skills
        projects = resume_data.projects
        level = resume_data.estimated_level
        gaps = resume_data.skill_gaps
        
        prompt = f"""请为以下候选人制定后端面试策略，以JSON格式返回：

候选人信息：
- 水平：{level}
- 工作年限：{resume_data.years_of_experience}年
- 技能栈：{json.dumps(skills, ensure_ascii=False)}
- 项目经历：{len(projects)}个项目
- 知识缺口：{json.dumps(gaps, ensure_ascii=False)}

请制定以下内容（JSON格式）：
{{
    "difficulty_adjustment": "难度调整建议（提高/正常/降低）",
    "focus_areas": ["重点考察领域1", "重点考察领域2", "重点考察领域3"],
    "avoid_areas": ["避免考察领域1"],
    "recommended_questions": [
        {{
            "category": "分类（Go/MySQL/Redis等）",
            "question": "推荐问题",
            "reason": "推荐理由"
        }}
    ],
    "project_questions": [
        {{
            "project": "项目名称",
            "questions": ["深挖问题1", "深挖问题2"]
        }}
    ],
    "scenario_design": "推荐的场景设计题类型",
    "time_allocation": {{
        "technical": 20,
        "project": 12,
        "design": 8
    }},
    "followup_strategy": "追问策略建议",
    "special_notes": "特别注意事项"
}}

面试策略原则：
1. 重点考察候选人掌握的技术领域
2. 针对项目经历设计深挖问题
3. 知识缺口作为辅助考察点
4. 根据候选人水平调整难度
"""
        
        try:
            response = await self.llm.chat_completion(
                [{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            # 清理响应文本
            response_text = response.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            return json.loads(response_text)
            
        except Exception as e:
            logger.error(f"策略生成失败: {e}")
            return {
                "focus_areas": ["Go语言", "MySQL", "Redis"],
                "recommended_questions": [],
                "difficulty_adjustment": "正常"
            }


def save_resume_analysis(resume_data: ResumeData, output_dir: Path):
    """保存简历分析结果"""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / f"resume_{resume_data.id}.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(asdict(resume_data), f, ensure_ascii=False, indent=2)
    
    logger.info(f"保存简历分析结果: {output_file}")


# 便捷函数
async def analyze_resume_file(file_path: str) -> ResumeData:
    """分析简历文件"""
    # 解析文本
    parser = ResumeParser()
    resume_text = parser.parse_file(file_path)
    
    if not resume_text:
        raise ValueError(f"无法解析简历文件: {file_path}")
    
    # LLM分析
    analyzer = LLMResumeAnalyzer()
    resume_data = await analyzer.analyze_resume(resume_text)
    resume_data.source_file = file_path
    
    return resume_data


# 测试用简历文本
test_resume = """
张三
电话：13800138000 | 邮箱：zhangsan@example.com

教育背景
北京大学 | 计算机科学与技术 | 本科 | 2018-2022

工作经历
字节跳动 | 后端开发工程师 | 2022.07-至今
• 负责抖音电商订单系统的开发和维护
• 参与设计高并发订单处理架构，支持日订单量100万+
• 优化数据库性能，SQL查询性能提升50%
• 使用Go语言重构核心服务，降低延迟30%

实习经历
阿里巴巴 | Java开发实习生 | 2021.07-2021.12
• 参与淘宝购物车服务开发
• 使用Spring Boot开发微服务接口
• 学习Redis缓存和MySQL优化

技能特长
• 编程语言：Go(熟练)、Java(熟练)、Python(了解)
• 数据库：MySQL、Redis、MongoDB
• 消息队列：Kafka、RocketMQ
• 框架：Gin、Spring Boot、GORM
• 工具：Git、Docker、Kubernetes、Prometheus
• 熟悉微服务架构、分布式系统、高并发设计

项目经历
电商订单系统重构
• 项目描述：重构抖音电商订单系统，支持高并发场景
• 技术栈：Go、MySQL、Redis、Kafka、Kubernetes
• 个人职责：负责订单创建和支付模块开发
• 项目成果：系统QPS从1000提升到5000，稳定性99.99%

分布式ID生成服务
• 项目描述：设计并实现分布式ID生成服务，替代数据库自增ID
• 技术栈：Go、Snowflake算法、etcd
• 个人职责：独立负责服务设计和开发
• 项目成果：支持每秒10万ID生成，无单点故障
"""


async def test_resume_analyzer():
    """测试简历分析器"""
    print("=" * 60)
    print("测试简历分析器")
    print("=" * 60)
    
    # 创建分析器
    analyzer = LLMResumeAnalyzer()
    
    # 分析测试简历
    print("\n分析测试简历...")
    resume_data = await analyzer.analyze_resume(test_resume)
    
    print("\n分析结果：")
    print(f"姓名: {resume_data.name}")
    print(f"电话: {resume_data.phone}")
    print(f"邮箱: {resume_data.email}")
    
    print(f"\n教育背景:")
    for edu in resume_data.education:
        print(f"  - {edu.get('school')} | {edu.get('major')} | {edu.get('degree')}")
    
    print(f"\n工作经历:")
    for work in resume_data.work_experience:
        print(f"  - {work.get('company')} | {work.get('position')} | {work.get('duration')}")
    
    print(f"\n技能栈:")
    for category, skills in resume_data.skills.items():
        if skills:
            print(f"  {category}: {', '.join(skills)}")
    
    print(f"\n项目经历:")
    for project in resume_data.projects:
        print(f"  - {project.get('name')}")
        print(f"    技术栈: {', '.join(project.get('tech_stack', []))}")
    
    print(f"\n能力评估:")
    print(f"  预估等级: {resume_data.estimated_level}")
    print(f"  工作年限: {resume_data.years_of_experience}年")
    print(f"  优势: {resume_data.strengths}")
    print(f"  知识缺口: {resume_data.skill_gaps}")
    
    print(f"\n面试策略:")
    strategy = resume_data.interview_strategy
    print(f"  难度调整: {strategy.get('difficulty_adjustment')}")
    print(f"  重点考察: {strategy.get('focus_areas')}")
    print(f"  场景设计题: {strategy.get('scenario_design')}")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_resume_analyzer())
