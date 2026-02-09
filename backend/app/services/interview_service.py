import uuid
import json
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum

from app.services.llm_service import glm4_service, vector_store
from app.models.schemas import InterviewMode, QuestionResponse, EvaluationDimension
from app.core.config import get_settings

settings = get_settings()


class InterviewEngine:
    """面试引擎核心服务"""
    
    def __init__(self):
        self.sessions: Dict[str, dict] = {}  # In-memory session storage
    
    async def start_interview(
        self,
        mode: InterviewMode,
        knowledge_base_ids: List[str],
        candidate_info: Optional[str] = None,
        duration_minutes: int = 30
    ) -> dict:
        """开始面试会话"""
        session_id = str(uuid.uuid4())
        
        session_data = {
            'id': session_id,
            'mode': mode,
            'knowledge_base_ids': knowledge_base_ids,
            'candidate_info': candidate_info,
            'duration_minutes': duration_minutes,
            'status': 'active',
            'started_at': datetime.now(),
            'current_question_index': 0,
            'questions': [],
            'answers': [],
            'history': []
        }
        
        if mode == InterviewMode.STRUCTURED:
            # Generate structured questions based on knowledge base
            session_data['questions'] = await self._generate_structured_questions(
                knowledge_base_ids
            )
            session_data['total_questions'] = len(session_data['questions'])
        else:
            # Open mode: prepare for free conversation
            session_data['total_questions'] = 0  # Dynamic
            session_data['context'] = candidate_info or ""
        
        self.sessions[session_id] = session_data
        
        return {
            'session_id': session_id,
            'mode': mode,
            'total_questions': session_data['total_questions'],
            'first_question': session_data['questions'][0] if session_data['questions'] else None
        }
    
    async def _generate_structured_questions(
        self,
        knowledge_base_ids: List[str],
        num_questions: int = 10
    ) -> List[dict]:
        """基于知识库生成结构化问题"""
        
        # Retrieve sample content from knowledge base
        sample_content = []
        for kb_id in knowledge_base_ids:
            results = await vector_store.search(
                collection_name=kb_id,
                query="重要概念 核心知识 关键技术",
                top_k=3
            )
            for result in results:
                sample_content.append(result['document'])
        
        context = "\n\n".join(sample_content[:3])  # Use top 3 chunks
        
        system_prompt = """你是一位专业的面试出题专家。请基于提供的知识库内容，设计面试问题。
要求：
1. 问题覆盖知识库的核心概念
2. 难度分布：30%基础、50%中等、20%困难
3. 问题类型包括：概念解释、场景应用、问题分析
4. 每个问题标注难度（1-5）和类型

请返回JSON格式的问题列表。"""
        
        user_prompt = f"""基于以下内容生成{num_questions}个面试问题：

{context}

请返回JSON格式：
{{
    "questions": [
        {{
            "id": "q1",
            "question": "具体问题内容",
            "type": "concept|application|analysis",
            "difficulty": 3,
            "expected_points": ["要点1", "要点2", "要点3"]
        }}
    ]
}}"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            response = await glm4_service.chat_completion(messages, temperature=0.7)
            
            # Parse JSON
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0]
            else:
                json_str = response
            
            data = json.loads(json_str.strip())
            questions = data.get('questions', [])
            
            # Add UUID to each question
            for i, q in enumerate(questions):
                q['id'] = f"q_{uuid.uuid4().hex[:8]}"
            
            return questions[:num_questions]
            
        except Exception as e:
            print(f"生成问题失败: {e}")
            # Return default questions
            return self._get_default_questions()
    
    def _get_default_questions(self) -> List[dict]:
        """获取默认问题（当生成失败时使用）"""
        return [
            {
                "id": f"q_{uuid.uuid4().hex[:8]}",
                "question": "请介绍一下你对这个领域的基本理解",
                "type": "concept",
                "difficulty": 2,
                "expected_points": ["基本概念", "主要应用", "核心价值"]
            },
            {
                "id": f"q_{uuid.uuid4().hex[:8]}",
                "question": "在实际项目中，你是如何应用这些知识的？",
                "type": "application",
                "difficulty": 3,
                "expected_points": ["具体案例", "实施过程", "遇到的问题和解决方案"]
            }
        ]
    
    async def get_next_question(self, session_id: str) -> Optional[QuestionResponse]:
        """获取下一个问题"""
        session = self.sessions.get(session_id)
        if not session or session['status'] != 'active':
            return None
        
        if session['mode'] == InterviewMode.STRUCTURED:
            # Get next pre-generated question
            index = session['current_question_index']
            if index < len(session['questions']):
                question = session['questions'][index]
                return QuestionResponse(
                    id=question['id'],
                    question=question['question'],
                    question_type=question['type'],
                    difficulty=question['difficulty'],
                    context=None
                )
            else:
                return None
        else:
            # Open mode: generate dynamic follow-up
            return await self._generate_followup_question(session)
    
    async def _generate_followup_question(self, session: dict) -> QuestionResponse:
        """生成开放式追问问题"""
        history = session.get('history', [])
        last_exchange = history[-1] if history else None
        
        # Retrieve relevant context from knowledge base
        context = ""
        if session['knowledge_base_ids']:
            query = last_exchange['answer'] if last_exchange else session.get('candidate_info', '')
            results = await vector_store.search(
                collection_name=session['knowledge_base_ids'][0],
                query=query,
                top_k=2
            )
            context = "\n".join([r['document'] for r in results])
        
        system_prompt = """你是一位经验丰富的面试官。请根据候选人的背景和之前的回答，提出一个深入的追问问题。
追问策略：
1. 针对模糊或不完整的回答进行澄清
2. 深入挖掘候选人的实际经验
3. 考察候选人的思维深度和广度
4. 保持对话的连贯性和自然性"""
        
        user_prompt = f"""候选人背景：{session.get('candidate_info', '无')}

{f'候选人上一个回答：{last_exchange["answer"]}' if last_exchange else '这是面试的开始'}

{f'相关知识：{context}' if context else ''}

请生成一个自然的追问问题。"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        response = await glm4_service.chat_completion(messages, temperature=0.8)
        
        return QuestionResponse(
            id=f"q_{uuid.uuid4().hex[:8]}",
            question=response.strip(),
            question_type="followup",
            difficulty=3,
            context=context if context else None
        )
    
    async def evaluate_answer(
        self,
        session_id: str,
        question_id: str,
        answer: str
    ) -> dict:
        """评估回答"""
        session = self.sessions.get(session_id)
        if not session:
            raise Exception("会话不存在")
        
        # Get question details
        question = None
        expected_points = []
        if session['mode'] == InterviewMode.STRUCTURED:
            for q in session['questions']:
                if q['id'] == question_id:
                    question = q['question']
                    expected_points = q.get('expected_points', [])
                    break
        
        if not question:
            # For open mode, get from history
            for exchange in session.get('history', []):
                if exchange.get('question_id') == question_id:
                    question = exchange['question']
                    break
        
        # Retrieve relevant context
        context = ""
        if session['knowledge_base_ids']:
            results = await vector_store.search(
                collection_name=session['knowledge_base_ids'][0],
                query=answer,
                top_k=2
            )
            context = "\n".join([r['document'] for r in results])
        
        # Evaluate
        evaluation = await glm4_service.evaluate_answer(
            question=question,
            answer=answer,
            context=context,
            expected_points=expected_points
        )
        
        # Store answer
        answer_record = {
            'question_id': question_id,
            'question': question,
            'answer': answer,
            'evaluation': evaluation,
            'timestamp': datetime.now()
        }
        session['answers'].append(answer_record)
        session['history'].append({
            'question_id': question_id,
            'question': question,
            'answer': answer
        })
        
        # Move to next question in structured mode
        if session['mode'] == InterviewMode.STRUCTURED:
            session['current_question_index'] += 1
        
        return evaluation
    
    async def generate_report(self, session_id: str) -> dict:
        """生成面试报告"""
        session = self.sessions.get(session_id)
        if not session:
            raise Exception("会话不存在")
        
        # Update session status
        session['status'] = 'completed'
        session['ended_at'] = datetime.now()
        
        answers = session['answers']
        if not answers:
            return {"error": "没有回答记录"}
        
        # Calculate statistics
        total_score = sum([a['evaluation'].get('total_score', 0) for a in answers]) / len(answers)
        
        # Aggregate dimension scores
        dimensions = {}
        for answer in answers:
            eval_data = answer['evaluation']
            for dim in ['accuracy', 'completeness', 'logic', 'depth']:
                if dim not in dimensions:
                    dimensions[dim] = []
                if dim in eval_data and isinstance(eval_data[dim], dict):
                    dimensions[dim].append(eval_data[dim].get('score', 0))
        
        dimensions_summary = []
        for dim, scores in dimensions.items():
            if scores:
                avg_score = sum(scores) / len(scores)
                dimensions_summary.append({
                    'name': dim,
                    'score': avg_score,
                    'feedback': self._get_dimension_feedback(dim, avg_score)
                })
        
        # Generate overall feedback
        system_prompt = """基于面试的所有回答，生成一份综合评估报告。包括：
1. 优势和亮点
2. 需要改进的地方
3. 具体的学习建议"""
        
        user_prompt = f"""面试模式：{session['mode']}
回答数量：{len(answers)}
平均分：{total_score}

各维度表现：
{chr(10).join([f"- {d['name']}: {d['score']}" for d in dimensions_summary])}

请生成简洁的综合评价。"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            overall_feedback = await glm4_service.chat_completion(messages, temperature=0.7)
        except:
            overall_feedback = "面试完成，总体表现良好。"
        
        return {
            'session_id': session_id,
            'mode': session['mode'],
            'total_questions': len(answers),
            'average_score': round(total_score, 2),
            'dimensions_summary': dimensions_summary,
            'overall_feedback': overall_feedback,
            'strengths': self._extract_strengths(answers),
            'weaknesses': self._extract_weaknesses(answers),
            'recommendations': self._generate_recommendations(answers),
            'generated_at': datetime.now()
        }
    
    def _get_dimension_feedback(self, dimension: str, score: float) -> str:
        """获取维度反馈"""
        if score >= 90:
            return "优秀"
        elif score >= 80:
            return "良好"
        elif score >= 70:
            return "合格"
        elif score >= 60:
            return "需改进"
        else:
            return "需重点提升"
    
    def _extract_strengths(self, answers: List[dict]) -> List[str]:
        """提取优势"""
        strengths = []
        for answer in answers:
            eval_data = answer['evaluation']
            for dim in ['accuracy', 'completeness', 'logic', 'depth']:
                if dim in eval_data and isinstance(eval_data[dim], dict):
                    if eval_data[dim].get('score', 0) >= 85:
                        strengths.append(f"{dim}表现出色")
        return list(set(strengths))[:3]  # Return top 3 unique strengths
    
    def _extract_weaknesses(self, answers: List[dict]) -> List[str]:
        """提取不足"""
        weaknesses = []
        for answer in answers:
            eval_data = answer['evaluation']
            for dim in ['accuracy', 'completeness', 'logic', 'depth']:
                if dim in eval_data and isinstance(eval_data[dim], dict):
                    if eval_data[dim].get('score', 0) < 70:
                        weaknesses.append(f"{dim}有待提升")
        return list(set(weaknesses))[:3]
    
    def _generate_recommendations(self, answers: List[dict]) -> List[str]:
        """生成建议"""
        recommendations = []
        for answer in answers:
            eval_data = answer['evaluation']
            if 'suggestions' in eval_data:
                recommendations.extend(eval_data['suggestions'])
        return list(set(recommendations))[:5]


# Global instance
interview_engine = InterviewEngine()
