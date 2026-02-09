#!/usr/bin/env python3
"""
InterviewerAgent - 智能面试官Agent
45分钟面试流程控制 + 混合追问策略 + 实时评估
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
from pathlib import Path

# 添加路径
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.llm_service import GLM4Service
from services.resume_analyzer import ResumeData
from knowledge_base.style_config_loader import get_style_config
from knowledge_base.vector_store import get_vector_store

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InterviewPhase(Enum):
    """面试阶段"""
    OPENING = "opening"              # 开场破冰
    TECHNICAL_BASIC = "technical"    # 技术基础
    PROJECT_DEEP_DIVE = "project"    # 项目深挖
    SYSTEM_DESIGN = "design"         # 场景设计
    CLOSING = "closing"              # 总结反馈
    COMPLETED = "completed"          # 已完成


class QuestionStyle(Enum):
    """提问风格"""
    DIRECT = "direct"      # 直接式
    GUIDING = "guiding"    # 引导式


class FollowUpStrategy(Enum):
    """追问策略"""
    CONSERVATIVE = "conservative"  # 保守策略
    AGGRESSIVE = "aggressive"      # 激进策略


@dataclass
class InterviewSession:
    """面试会话数据"""
    id: str
    resume_data: ResumeData
    
    # 状态
    current_phase: InterviewPhase = InterviewPhase.OPENING
    phase_start_time: datetime = field(default_factory=datetime.now)
    session_start_time: datetime = field(default_factory=datetime.now)
    
    # 进度
    current_question_index: int = 0
    total_questions_asked: int = 0
    followup_count: int = 0
    
    # 对话历史
    conversation_history: List[Dict] = field(default_factory=list)
    
    # 评估数据
    evaluations: List[Dict] = field(default_factory=list)
    
    # 配置
    style_config: Dict = field(default_factory=dict)
    interview_strategy: Dict = field(default_factory=dict)


@dataclass
class Question:
    """面试问题"""
    id: str
    text: str
    category: str
    difficulty: int
    expected_points: List[str] = field(default_factory=list)
    followup_questions: List[str] = field(default_factory=list)


@dataclass
class AnswerEvaluation:
    """回答评估"""
    question_id: str
    accuracy: int = 0           # 准确性 0-100
    completeness: int = 0       # 完整性 0-100
    logic: int = 0              # 逻辑性 0-100
    depth: int = 0              # 深度 0-100
    total_score: int = 0        # 总分 0-100
    feedback: str = ""
    suggestions: List[str] = field(default_factory=list)


class InterviewTimer:
    """面试计时器"""
    
    def __init__(self, total_duration: int = 45):
        self.total_duration = total_duration * 60  # 转换为秒
        self.start_time = None
        self.phase_times = {}
        
    def start(self):
        """开始计时"""
        self.start_time = time.time()
        
    def get_elapsed_seconds(self) -> int:
        """获取已用时间（秒）"""
        if self.start_time is None:
            return 0
        return int(time.time() - self.start_time)
    
    def get_remaining_seconds(self) -> int:
        """获取剩余时间（秒）"""
        return max(0, self.total_duration - self.get_elapsed_seconds())
    
    def get_elapsed_minutes(self) -> float:
        """获取已用时间（分钟）"""
        return self.get_elapsed_seconds() / 60
    
    def get_phase_time_limit(self, phase: InterviewPhase) -> int:
        """获取阶段时间限制（秒）"""
        phase_limits = {
            InterviewPhase.OPENING: 3 * 60,
            InterviewPhase.TECHNICAL_BASIC: 20 * 60,
            InterviewPhase.PROJECT_DEEP_DIVE: 12 * 60,
            InterviewPhase.SYSTEM_DESIGN: 8 * 60,
            InterviewPhase.CLOSING: 2 * 60
        }
        return phase_limits.get(phase, 5 * 60)
    
    def should_warn_time(self) -> bool:
        """是否应该时间警告"""
        remaining = self.get_remaining_seconds()
        return remaining < 5 * 60  # 最后5分钟警告
    
    def should_force_next(self) -> bool:
        """是否应该强制进入下一阶段"""
        remaining = self.get_remaining_seconds()
        return remaining < 2 * 60  # 最后2分钟强制切换


class QuestionGenerator:
    """问题生成器"""
    
    def __init__(self, vector_store=None):
        self.llm = GLM4Service()
        self.vector_store = vector_store or get_vector_store()
        self.style_config = get_style_config()
    
    async def generate_questions_for_phase(
        self,
        phase: InterviewPhase,
        resume_data: ResumeData,
        strategy: Dict,
        count: int = 3
    ) -> List[Question]:
        """
        为面试阶段生成问题
        
        Args:
            phase: 面试阶段
            resume_data: 简历数据
            strategy: 面试策略
            count: 生成问题数量
            
        Returns:
            问题列表
        """
        if phase == InterviewPhase.TECHNICAL_BASIC:
            return await self._generate_technical_questions(resume_data, strategy, count)
        elif phase == InterviewPhase.PROJECT_DEEP_DIVE:
            return await self._generate_project_questions(resume_data, count)
        elif phase == InterviewPhase.SYSTEM_DESIGN:
            return await self._generate_design_questions(resume_data, count)
        else:
            return []
    
    async def _generate_technical_questions(
        self,
        resume_data: ResumeData,
        strategy: Dict,
        count: int
    ) -> List[Question]:
        """生成技术基础问题"""
        focus_areas = strategy.get('focus_areas', ['Go', 'MySQL', 'Redis'])
        level = resume_data.estimated_level
        
        questions = []
        
        # 从知识库检索相关问题
        for area in focus_areas[:3]:  # 取前3个重点领域
            try:
                # 简单检索（暂时不使用向量检索）
                # 从增强后的JSON文件中加载问题
                questions_file = Path("/home/fengxu/mylib/interview-agent/backend/data/processed/enhanced_questions.json")
                if questions_file.exists():
                    with open(questions_file, 'r', encoding='utf-8') as f:
                        all_questions = json.load(f)
                    
                    # 筛选相关问题
                    area_questions = [
                        q for q in all_questions 
                        if area.lower() in q.get('category', '').lower() 
                        or any(area.lower() in tag.lower() for tag in q.get('tags', []))
                    ]
                    
                    # 根据难度筛选
                    if level == "初级":
                        area_questions = [q for q in area_questions if q.get('difficulty', 3) <= 2]
                    elif level == "中级":
                        area_questions = [q for q in area_questions if 2 <= q.get('difficulty', 3) <= 4]
                    else:  # 高级
                        area_questions = [q for q in area_questions if q.get('difficulty', 3) >= 3]
                    
                    # 随机选择
                    import random
                    selected = random.sample(area_questions, min(2, len(area_questions)))
                    
                    for q in selected:
                        questions.append(Question(
                            id=q.get('id', ''),
                            text=q.get('text', ''),
                            category=q.get('category', ''),
                            difficulty=q.get('difficulty', 3),
                            followup_questions=q.get('followup_points', [])
                        ))
                        
            except Exception as e:
                logger.error(f"生成技术问题失败: {e}")
                continue
        
        return questions[:count]
    
    async def _generate_project_questions(
        self,
        resume_data: ResumeData,
        count: int
    ) -> List[Question]:
        """生成项目深挖问题"""
        projects = resume_data.projects
        questions = []
        
        for project in projects[:2]:  # 取前2个项目
            project_name = project.get('name', '')
            tech_stack = project.get('tech_stack', [])
            
            # 生成深挖问题
            prompts = [
                f"你在{project_name}中提到了{', '.join(tech_stack[:3])}，能详细说说技术选型的考虑吗？",
                f"{project_name}项目中遇到的最大技术挑战是什么？如何解决的？",
                f"如果{project_name}的流量扩大10倍，你会如何优化架构？"
            ]
            
            for i, prompt in enumerate(prompts):
                questions.append(Question(
                    id=f"project_{project_name}_{i}",
                    text=prompt,
                    category="project",
                    difficulty=4,
                    followup_questions=[
                        "这个方案在更高并发下会有什么瓶颈？",
                        "有没有考虑过其他技术方案？为什么选这个？"
                    ]
                ))
        
        return questions[:count]
    
    async def _generate_design_questions(
        self,
        resume_data: ResumeData,
        count: int
    ) -> List[Question]:
        """生成场景设计问题"""
        strategy = resume_data.interview_strategy
        scenario_type = strategy.get('scenario_design', '秒杀系统')
        
        # 固定题库中的设计题
        design_questions = {
            "秒杀系统": "设计一个秒杀系统，要求支持10万QPS，如何保证不超卖？",
            "短链服务": "设计一个短链接服务，需要考虑高可用和海量数据存储。",
            "IM系统": "设计一个即时通讯系统，支持单聊和群聊，消息不丢失。",
            "订单系统": "设计一个电商订单系统，处理高并发下的订单创建和库存扣减。"
        }
        
        question_text = design_questions.get(scenario_type, design_questions["秒杀系统"])
        
        return [Question(
            id="design_001",
            text=question_text,
            category="system-design",
            difficulty=5,
            followup_questions=[
                "数据库怎么设计？",
                "缓存策略是什么？",
                "如果服务挂了怎么保证数据一致性？"
            ]
        )]
    
    def get_opening_questions(self, candidate_name: str) -> List[str]:
        """获取开场问题"""
        return [
            f"你好{candidate_name}，请简单介绍一下自己。",
            "今天的面试大概需要45分钟，分为几个环节：技术基础、项目深挖和场景设计题。你准备好了吗？"
        ]
    
    def get_closing_questions(self) -> List[str]:
        """获取结束问题"""
        return [
            "今天的面试到此结束，你有什么问题想问我吗？",
            "面试结果会在3个工作日内通知，请保持手机畅通。"
        ]


class AnswerEvaluator:
    """回答评估器"""
    
    def __init__(self):
        self.llm = GLM4Service()
    
    async def evaluate(
        self,
        question: Question,
        answer: str,
        context: str = ""
    ) -> AnswerEvaluation:
        """
        评估候选人回答
        
        Args:
            question: 问题
            answer: 候选人回答
            context: 上下文
            
        Returns:
            评估结果
        """
        prompt = f"""请评估以下面试回答，返回JSON格式评估结果：

问题：{question.text}
预期要点：{', '.join(question.expected_points) if question.expected_points else '无'}

候选人回答：
{answer[:1000]}

请从以下维度评估（JSON格式）：
{{
    "accuracy": 85,
    "completeness": 80,
    "logic": 90,
    "depth": 75,
    "total_score": 82,
    "feedback": "具体评价",
    "suggestions": ["改进建议1", "改进建议2"],
    "has_potential": true,
    "can_go_deeper": true
}}

评分标准：
- accuracy: 内容正确性（0-100）
- completeness: 要点覆盖度（0-100）
- logic: 逻辑清晰度（0-100）
- depth: 理解深度（0-100）
- has_potential: 是否有潜力值得深挖
- can_go_deeper: 是否可以继续追问
"""
        
        try:
            response = await self.llm.chat_completion(
                [{"role": "user", "content": prompt}],
                temperature=0.2
            )
            
            # 清理响应
            response_text = response.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            result = json.loads(response_text)
            
            return AnswerEvaluation(
                question_id=question.id,
                accuracy=result.get('accuracy', 70),
                completeness=result.get('completeness', 70),
                logic=result.get('logic', 70),
                depth=result.get('depth', 70),
                total_score=result.get('total_score', 70),
                feedback=result.get('feedback', ''),
                suggestions=result.get('suggestions', [])
            )
            
        except Exception as e:
            logger.error(f"评估失败: {e}")
            return AnswerEvaluation(
                question_id=question.id,
                total_score=70,
                feedback="评估出错，使用默认评分"
            )


class FollowUpEngine:
    """追问引擎"""
    
    def __init__(self):
        self.style_config = get_style_config()
        self.max_followups = self.style_config.get_max_followups()
    
    def should_followup(
        self,
        evaluation: AnswerEvaluation,
        current_count: int,
        elapsed_time: float,
        candidate_confidence: float = 0.5
    ) -> Tuple[bool, FollowUpStrategy]:
        """
        判断是否追问
        
        Returns:
            (是否追问, 追问策略)
        """
        # 检查追问次数
        if current_count >= self.max_followups:
            return False, FollowUpStrategy.CONSERVATIVE
        
        # 检查时间
        if elapsed_time < 15:  # 前15分钟保守
            strategy = FollowUpStrategy.CONSERVATIVE
        elif elapsed_time < 35:  # 中间根据表现
            if candidate_confidence > 0.7:
                strategy = FollowUpStrategy.AGGRESSIVE
            else:
                strategy = FollowUpStrategy.CONSERVATIVE
        else:  # 后10分钟保守
            strategy = FollowUpStrategy.CONSERVATIVE
        
        # 评估回答质量决定是否追问
        should_follow = False
        
        if strategy == FollowUpStrategy.AGGRESSIVE:
            # 激进策略：回答好就深挖
            if evaluation.total_score > 75 and evaluation.depth < 80:
                should_follow = True
        else:
            # 保守策略：回答有缺陷才追问
            if evaluation.completeness < 70:
                should_follow = True
            elif evaluation.accuracy < 60:
                should_follow = True
        
        return should_follow, strategy
    
    async def generate_followup(
        self,
        question: Question,
        answer: str,
        evaluation: AnswerEvaluation,
        strategy: FollowUpStrategy
    ) -> str:
        """生成追问问题"""
        
        if evaluation.completeness < 70:
            # 补充型追问
            return self.style_config.get_followup_phrase('incomplete')
        elif evaluation.accuracy < 60:
            # 纠错型追问
            return self.style_config.get_followup_phrase('wrong')
        elif strategy == FollowUpStrategy.AGGRESSIVE:
            # 深度追问
            return self.style_config.get_followup_phrase('deep', concept=question.category)
        else:
            # 场景追问
            return self.style_config.get_followup_phrase('scenario', topic=question.category)


class InterviewerAgent:
    """面试官Agent主类"""
    
    def __init__(self):
        self.llm = GLM4Service()
        self.timer = InterviewTimer()
        self.question_generator = QuestionGenerator()
        self.answer_evaluator = AnswerEvaluator()
        self.followup_engine = FollowUpEngine()
        self.style_config = get_style_config()
        
        self.current_session: Optional[InterviewSession] = None
        self.current_questions: List[Question] = []
        self.current_question_index: int = 0
    
    async def start_interview(self, resume_data: ResumeData) -> InterviewSession:
        """
        开始面试
        
        Args:
            resume_data: 简历数据
            
        Returns:
            面试会话
        """
        logger.info(f"开始面试 - 候选人: {resume_data.name}")
        
        # 创建会话
        session_id = f"interview_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.current_session = InterviewSession(
            id=session_id,
            resume_data=resume_data,
            style_config=self.style_config.config,
            interview_strategy=resume_data.interview_strategy
        )
        
        # 启动计时器
        self.timer.start()
        
        # 设置初始阶段
        await self._enter_phase(InterviewPhase.OPENING)
        
        return self.current_session
    
    async def _enter_phase(self, phase: InterviewPhase):
        """进入面试阶段"""
        if not self.current_session:
            return
        
        self.current_session.current_phase = phase
        self.current_session.phase_start_time = datetime.now()
        
        logger.info(f"进入阶段: {phase.value}")
        
        # 为该阶段生成问题
        if phase in [InterviewPhase.TECHNICAL_BASIC, InterviewPhase.PROJECT_DEEP_DIVE, InterviewPhase.SYSTEM_DESIGN]:
            self.current_questions = await self.question_generator.generate_questions_for_phase(
                phase,
                self.current_session.resume_data,
                self.current_session.interview_strategy,
                count=5
            )
            self.current_question_index = 0
            logger.info(f"生成 {len(self.current_questions)} 个问题")
    
    async def get_next_action(self) -> Dict[str, Any]:
        """
        获取下一步行动
        
        Returns:
            下一步行动信息
        """
        if not self.current_session:
            return {"type": "error", "message": "没有活跃的面试会话"}
        
        phase = self.current_session.current_phase
        
        # 检查时间
        elapsed_minutes = self.timer.get_elapsed_minutes()
        phase_time_limit = self.timer.get_phase_time_limit(phase) / 60
        
        # 检查是否需要切换阶段
        if elapsed_minutes >= phase_time_limit or self.timer.should_force_next():
            next_phase = self._get_next_phase(phase)
            if next_phase:
                await self._enter_phase(next_phase)
                return await self.get_next_action()
            else:
                return {"type": "completed", "message": "面试结束"}
        
        # 根据阶段返回相应行动
        if phase == InterviewPhase.OPENING:
            return await self._handle_opening()
        elif phase == InterviewPhase.TECHNICAL_BASIC:
            return await self._handle_technical()
        elif phase == InterviewPhase.PROJECT_DEEP_DIVE:
            return await self._handle_project()
        elif phase == InterviewPhase.SYSTEM_DESIGN:
            return await self._handle_design()
        elif phase == InterviewPhase.CLOSING:
            return await self._handle_closing()
        else:
            return {"type": "completed", "message": "面试已完成"}
    
    async def _handle_opening(self) -> Dict[str, Any]:
        """处理开场阶段"""
        questions = self.question_generator.get_opening_questions(
            self.current_session.resume_data.name
        )
        
        return {
            "type": "question",
            "phase": "opening",
            "questions": questions,
            "duration": 3,
            "message": "开场破冰"
        }
    
    async def _handle_technical(self) -> Dict[str, Any]:
        """处理技术基础阶段"""
        if self.current_question_index < len(self.current_questions):
            question = self.current_questions[self.current_question_index]
            
            return {
                "type": "question",
                "phase": "technical",
                "question": {
                    "id": question.id,
                    "text": question.text,
                    "category": question.category,
                    "difficulty": question.difficulty
                },
                "progress": f"{self.current_question_index + 1}/{len(self.current_questions)}",
                "duration": 20
            }
        else:
            # 该阶段问题已问完，进入下一阶段
            await self._enter_phase(InterviewPhase.PROJECT_DEEP_DIVE)
            return await self.get_next_action()
    
    async def _handle_project(self) -> Dict[str, Any]:
        """处理项目深挖阶段"""
        if self.current_question_index < len(self.current_questions):
            question = self.current_questions[self.current_question_index]
            
            return {
                "type": "question",
                "phase": "project",
                "question": {
                    "id": question.id,
                    "text": question.text,
                    "category": question.category,
                    "difficulty": question.difficulty
                },
                "progress": f"{self.current_question_index + 1}/{len(self.current_questions)}",
                "duration": 12
            }
        else:
            await self._enter_phase(InterviewPhase.SYSTEM_DESIGN)
            return await self.get_next_action()
    
    async def _handle_design(self) -> Dict[str, Any]:
        """处理场景设计阶段"""
        if self.current_questions:
            question = self.current_questions[0]
            
            return {
                "type": "design_question",
                "phase": "design",
                "question": {
                    "id": question.id,
                    "text": question.text,
                    "category": question.category,
                    "difficulty": question.difficulty
                },
                "duration": 8
            }
        else:
            await self._enter_phase(InterviewPhase.CLOSING)
            return await self.get_next_action()
    
    async def _handle_closing(self) -> Dict[str, Any]:
        """处理结束阶段"""
        questions = self.question_generator.get_closing_questions()
        
        return {
            "type": "closing",
            "phase": "closing",
            "questions": questions,
            "duration": 2
        }
    
    async def process_answer(self, answer: str) -> Dict[str, Any]:
        """
        处理候选人回答
        
        Args:
            answer: 候选人回答
            
        Returns:
            处理结果
        """
        if not self.current_session or not self.current_questions:
            return {"type": "error", "message": "没有当前问题"}
        
        # 获取当前问题
        current_question = self.current_questions[self.current_question_index]
        
        # 评估回答
        evaluation = await self.answer_evaluator.evaluate(
            current_question,
            answer
        )
        
        # 保存评估
        self.current_session.evaluations.append({
            'question_id': current_question.id,
            'evaluation': evaluation
        })
        
        # 记录对话
        self.current_session.conversation_history.append({
            'role': 'candidate',
            'content': answer,
            'timestamp': datetime.now().isoformat()
        })
        
        # 判断是否追问
        should_follow, strategy = self.followup_engine.should_followup(
            evaluation,
            self.current_session.followup_count,
            self.timer.get_elapsed_minutes(),
            candidate_confidence=evaluation.total_score / 100
        )
        
        if should_follow:
            # 生成追问
            followup_question = await self.followup_engine.generate_followup(
                current_question,
                answer,
                evaluation,
                strategy
            )
            
            self.current_session.followup_count += 1
            
            return {
                "type": "followup",
                "question": followup_question,
                "strategy": strategy.value,
                "evaluation": {
                    "score": evaluation.total_score,
                    "feedback": evaluation.feedback
                }
            }
        else:
            # 进入下一个问题
            self.current_question_index += 1
            self.current_session.total_questions_asked += 1
            
            return {
                "type": "next_question",
                "evaluation": {
                    "score": evaluation.total_score,
                    "feedback": evaluation.feedback
                }
            }
    
    def _get_next_phase(self, current_phase: InterviewPhase) -> Optional[InterviewPhase]:
        """获取下一阶段"""
        phase_order = [
            InterviewPhase.OPENING,
            InterviewPhase.TECHNICAL_BASIC,
            InterviewPhase.PROJECT_DEEP_DIVE,
            InterviewPhase.SYSTEM_DESIGN,
            InterviewPhase.CLOSING,
            InterviewPhase.COMPLETED
        ]
        
        try:
            current_index = phase_order.index(current_phase)
            if current_index < len(phase_order) - 1:
                return phase_order[current_index + 1]
        except ValueError:
            pass
        
        return None
    
    async def generate_report(self) -> Dict[str, Any]:
        """生成面试报告"""
        if not self.current_session:
            return {"error": "没有面试数据"}
        
        evaluations = self.current_session.evaluations
        
        if not evaluations:
            return {"error": "没有评估数据"}
        
        # 计算平均分
        avg_scores = {
            'accuracy': sum(e.get('evaluation', {}).accuracy for e in evaluations) / len(evaluations),
            'completeness': sum(e.get('evaluation', {}).completeness for e in evaluations) / len(evaluations),
            'logic': sum(e.get('evaluation', {}).logic for e in evaluations) / len(evaluations),
            'depth': sum(e.get('evaluation', {}).depth for e in evaluations) / len(evaluations),
            'total': sum(e.get('evaluation', {}).total_score for e in evaluations) / len(evaluations)
        }
        
        # 确定等级
        level = "中级"
        if avg_scores['total'] >= 90:
            level = "高级"
        elif avg_scores['total'] < 70:
            level = "初级"
        
        return {
            "session_id": self.current_session.id,
            "candidate": self.current_session.resume_data.name,
            "duration": self.timer.get_elapsed_minutes(),
            "total_questions": self.current_session.total_questions_asked,
            "total_followups": self.current_session.followup_count,
            "scores": avg_scores,
            "level": level,
            "recommendation": "推荐" if avg_scores['total'] >= 75 else "待定",
            "detailed_evaluations": [
                {
                    "question_id": e.get('question_id'),
                    "score": e.get('evaluation', {}).total_score,
                    "feedback": e.get('evaluation', {}).feedback
                }
                for e in evaluations
            ]
        }


# 测试函数
async def test_interviewer_agent():
    """测试InterviewerAgent"""
    print("=" * 60)
    print("测试 InterviewerAgent")
    print("=" * 60)
    
    # 创建测试简历数据
    from services.resume_analyzer import ResumeData
    
    test_resume = ResumeData(
        id="test_resume_001",
        name="张三",
        raw_text="测试简历",
        skills={
            "programming_languages": ["Go", "Java"],
            "databases": ["MySQL", "Redis"],
            "frameworks": ["Gin", "Spring Boot"]
        },
        estimated_level="中级",
        years_of_experience=3.5,
        interview_strategy={
            "focus_areas": ["Go", "MySQL", "Redis"],
            "difficulty_adjustment": "正常"
        }
    )
    
    # 创建Agent
    agent = InterviewerAgent()
    
    # 开始面试
    print("\n1. 开始面试...")
    session = await agent.start_interview(test_resume)
    print(f"   会话ID: {session.id}")
    print(f"   候选人: {session.resume_data.name}")
    
    # 获取开场行动
    print("\n2. 获取开场行动...")
    action = await agent.get_next_action()
    print(f"   类型: {action['type']}")
    print(f"   问题: {action.get('questions', [])}")
    
    # 模拟候选人回答
    print("\n3. 模拟候选人回答...")
    answer = "我叫张三，毕业于北京大学计算机专业，目前在字节跳动做后端开发，主要使用Go语言。"
    result = await agent.process_answer(answer)
    print(f"   结果类型: {result['type']}")
    print(f"   评分: {result.get('evaluation', {}).get('score')}")
    
    # 获取技术问题
    print("\n4. 获取技术问题...")
    action = await agent.get_next_action()
    print(f"   类型: {action['type']}")
    print(f"   问题: {action.get('question', {}).get('text', 'N/A')[:80]}...")
    
    # 模拟回答
    print("\n5. 模拟技术问题回答...")
    answer = "Go语言的goroutine是轻量级线程，由Go运行时管理，比系统线程更轻量。GPM调度模型中，G是goroutine，P是逻辑处理器，M是系统线程。"
    result = await agent.process_answer(answer)
    print(f"   结果类型: {result['type']}")
    if result['type'] == 'followup':
        print(f"   追问: {result.get('question')}")
    
    # 生成报告
    print("\n6. 生成面试报告...")
    report = await agent.generate_report()
    print(f"   总分: {report.get('scores', {}).get('total')}")
    print(f"   等级: {report.get('level')}")
    print(f"   推荐: {report.get('recommendation')}")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_interviewer_agent())
