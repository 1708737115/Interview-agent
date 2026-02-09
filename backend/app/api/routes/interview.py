from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from typing import List, Optional
from app.models.schemas import (
    DocumentUploadRequest, DocumentResponse, StartInterviewRequest,
    InterviewSession, QuestionResponse, AnswerRequest, AnswerResponse,
    InterviewReport, ChatRequest, ChatResponse
)
from app.services.document_service import document_parser
from app.services.llm_service import vector_store
from app.services.interview_service import interview_engine
from app.models.database import get_db, Document as DocumentModel
from sqlalchemy.orm import Session
import uuid
from datetime import datetime

router = APIRouter()


@router.post("/documents/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """上传并解析文档"""
    try:
        # Save file
        file_id, file_path, file_type, original_name = await document_parser.save_upload(file)
        
        # Create document record
        doc_record = DocumentModel(
            id=file_id,
            title=title,
            description=description,
            file_type=file_type.value,
            file_path=file_path,
            status="processing"
        )
        db.add(doc_record)
        db.commit()
        
        # Parse document
        content = await document_parser.parse_document(file_path, file_type)
        
        # Chunk content
        chunks = document_parser.chunk_text(content)
        
        # Store in vector database
        documents = [chunk['text'] for chunk in chunks]
        metadatas = [{
            'source': original_name,
            'document_id': file_id,
            'chunk_index': i,
            'created_at': datetime.now().isoformat()
        } for i in range(len(chunks))]
        
        await vector_store.add_documents(
            collection_name=file_id,
            documents=documents,
            metadatas=metadatas
        )
        
        # Update record
        doc_record.status = "completed"
        doc_record.chunk_count = len(chunks)
        doc_record.updated_at = datetime.now()
        db.commit()
        
        return DocumentResponse(
            id=file_id,
            title=title,
            description=description,
            file_type=file_type,
            status="completed",
            created_at=doc_record.created_at,
            chunk_count=len(chunks)
        )
        
    except Exception as e:
        import traceback
        error_msg = f"文档处理失败: {str(e)}"
        print(f"[ERROR] {error_msg}")
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=error_msg)


@router.get("/documents", response_model=List[DocumentResponse])
async def list_documents(db: Session = Depends(get_db)):
    """获取文档列表"""
    documents = db.query(DocumentModel).all()
    return [
        DocumentResponse(
            id=doc.id,
            title=doc.title,
            description=doc.description,
            file_type=doc.file_type,
            status=doc.status,
            created_at=doc.created_at,
            chunk_count=doc.chunk_count
        )
        for doc in documents
    ]


@router.delete("/documents/{document_id}")
async def delete_document(document_id: str, db: Session = Depends(get_db)):
    """删除文档"""
    doc = db.query(DocumentModel).filter(DocumentModel.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")
    
    # Delete from vector store
    await vector_store.delete_collection(document_id)
    
    # Delete from database
    db.delete(doc)
    db.commit()
    
    return {"message": "文档已删除"}


@router.post("/interview/start")
async def start_interview(request: StartInterviewRequest):
    """开始面试会话"""
    try:
        result = await interview_engine.start_interview(
            mode=request.mode,
            knowledge_base_ids=request.knowledge_base_ids,
            candidate_info=request.candidate_info,
            duration_minutes=request.duration_minutes
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"启动面试失败: {str(e)}")


@router.get("/interview/{session_id}/question", response_model=QuestionResponse)
async def get_question(session_id: str):
    """获取当前问题"""
    try:
        question = await interview_engine.get_next_question(session_id)
        if not question:
            raise HTTPException(status_code=404, detail="没有更多问题")
        return question
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取问题失败: {str(e)}")


@router.post("/interview/answer")
async def submit_answer(request: AnswerRequest):
    """提交回答"""
    try:
        evaluation = await interview_engine.evaluate_answer(
            session_id=request.session_id,
            question_id=request.question_id,
            answer=request.answer
        )
        
        # Get next question if available
        next_question = await interview_engine.get_next_question(request.session_id)
        
        # Format evaluation dimensions
        dimensions = []
        for dim in ['accuracy', 'completeness', 'logic', 'depth']:
            if dim in evaluation and isinstance(evaluation[dim], dict):
                dimensions.append({
                    'name': dim,
                    'score': evaluation[dim].get('score', 0),
                    'feedback': evaluation[dim].get('feedback', '')
                })
        
        return AnswerResponse(
            evaluation=dimensions,
            total_score=evaluation.get('total_score', 0),
            feedback=evaluation.get('overall_feedback', ''),
            suggestions=evaluation.get('suggestions', []),
            next_question=next_question
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"评估回答失败: {str(e)}")


@router.get("/interview/{session_id}/report", response_model=InterviewReport)
async def get_report(session_id: str):
    """获取面试报告"""
    try:
        report = await interview_engine.generate_report(session_id)
        
        return InterviewReport(
            session_id=report['session_id'],
            mode=report['mode'],
            total_questions=report['total_questions'],
            average_score=report['average_score'],
            dimensions_summary=report['dimensions_summary'],
            strengths=report['strengths'],
            weaknesses=report['weaknesses'],
            recommendations=report['recommendations'],
            generated_at=report['generated_at']
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成报告失败: {str(e)}")


@router.post("/interview/{session_id}/end")
async def end_interview(session_id: str):
    """结束面试"""
    try:
        report = await interview_engine.generate_report(session_id)
        return {
            "message": "面试已结束",
            "report": report
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"结束面试失败: {str(e)}")


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """开放式对话（用于开放式面试模式）"""
    try:
        from app.services.llm_service import glm4_service
        
        # Retrieve context if available
        session = interview_engine.sessions.get(request.session_id)
        contexts = []
        if session and session.get('knowledge_base_ids'):
            results = await vector_store.search(
                collection_name=session['knowledge_base_ids'][0],
                query=request.message,
                top_k=3
            )
            contexts = [r['document'] for r in results]
        
        # Build messages
        messages = [
            {"role": "system", "content": "你是一位专业的面试官，正在进行开放式面试。请根据候选人的回答进行深入追问。"}
        ]
        
        # Add context if available
        if contexts:
            context_text = "\n\n".join(contexts)
            messages.append({"role": "system", "content": f"相关知识：{context_text}"})
        
        messages.append({"role": "user", "content": request.message})
        
        # Generate response
        response = await glm4_service.chat_completion(messages)
        
        return ChatResponse(
            message=response,
            retrieved_contexts=contexts if contexts else None
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"对话失败: {str(e)}")


@router.post("/resume/parse")
async def parse_resume(file: UploadFile = File(...)):
    """解析简历文件并提取信息"""
    try:
        # Save uploaded file
        file_id, file_path, file_type, original_name = await document_parser.save_upload(file)
        
        # Parse document content
        content = await document_parser.parse_document(file_path, file_type)
        
        # Use LLM to extract structured information from resume
        from app.services.llm_service import glm4_service
        
        prompt = f"""请从以下简历内容中提取关键信息，并以JSON格式返回：

简历内容：
{content[:8000]}  # Limit content length

请提取以下信息并返回JSON格式：
{{
    "name": "姓名",
    "phone": "手机号（如果没有则返回空字符串）",
    "email": "邮箱（如果没有则返回空字符串）",
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
            "duration": "工作时间段"
        }}
    ],
    "skills": {{
        "programming_languages": ["编程语言列表"],
        "databases": ["数据库列表"],
        "frameworks": ["框架列表"],
        "middleware": ["中间件列表"]
    }},
    "estimated_level": "预估职级（初级/中级/高级）",
    "years_of_experience": 工作年限（数字）,
    "interview_strategy": {{
        "focus_areas": ["面试重点考察领域，3-5个"],
        "difficulty_adjustment": "难度调整（简单/正常/困难）",
        "scenario_design": "场景设计主题"
    }}
}}

请确保返回有效的JSON格式。"""

        messages = [
            {"role": "system", "content": "你是一位专业的简历解析助手。请从简历中提取关键信息并以JSON格式返回。"},
            {"role": "user", "content": prompt}
        ]
        
        response = await glm4_service.chat_completion(messages, temperature=0.3)
        
        # Parse JSON response
        import json
        try:
            # Try to extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                parsed_data = json.loads(json_str)
            else:
                parsed_data = json.loads(response)
        except json.JSONDecodeError:
            # If JSON parsing fails, return basic structure
            parsed_data = {
                "name": original_name.split('.')[0] if original_name else "候选人",
                "phone": "",
                "email": "",
                "education": [{"school": "", "major": "", "degree": "", "graduation_year": ""}],
                "work_experience": [{"company": "", "position": "", "duration": ""}],
                "skills": {
                    "programming_languages": [],
                    "databases": [],
                    "frameworks": [],
                    "middleware": []
                },
                "estimated_level": "中级",
                "years_of_experience": 0,
                "interview_strategy": {
                    "focus_areas": ["Go语言", "MySQL", "Redis"],
                    "difficulty_adjustment": "正常",
                    "scenario_design": "微服务架构设计"
                }
            }
        
        # Clean up uploaded file
        import os
        try:
            os.remove(file_path)
        except:
            pass
        
        return parsed_data
        
    except Exception as e:
        import traceback
        print(f"[ERROR] 简历解析失败: {str(e)}")
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"简历解析失败: {str(e)}")
