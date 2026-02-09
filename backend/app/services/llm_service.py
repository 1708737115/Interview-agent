import os
import uuid
import aiofiles
from typing import List, Optional
from datetime import datetime

from zhipuai import ZhipuAI
import chromadb
from chromadb.config import Settings as ChromaSettings

from app.core.config import get_settings

settings = get_settings()


class GLM4Service:
    """GLM-4 API服务封装"""
    
    def __init__(self):
        self.client = ZhipuAI(api_key=settings.GLM4_API_KEY)
        self.model = settings.GLM4_MODEL
        self.embedding_model = settings.GLM4_EMBEDDING_MODEL
    
    async def chat_completion(
        self,
        messages: List[dict],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> str:
        """调用GLM-4进行对话"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature or settings.TEMPERATURE,
                max_tokens=max_tokens or settings.MAX_TOKENS,
                stream=stream
            )
            
            if stream:
                # Handle streaming response
                full_response = ""
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        full_response += chunk.choices[0].delta.content
                return full_response
            else:
                return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"GLM-4 API调用失败: {str(e)}")
    
    async def generate_embedding(self, text: str) -> List[float]:
        """生成文本向量"""
        try:
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            raise Exception(f"Embedding生成失败: {str(e)}")

    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """批量生成文本向量"""
        try:
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=texts
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            raise Exception(f"批量Embedding生成失败: {str(e)}")
    
    async def evaluate_answer(
        self,
        question: str,
        answer: str,
        context: Optional[str] = None,
        expected_points: Optional[List[str]] = None
    ) -> dict:
        """评估面试回答"""
        system_prompt = """你是一位专业的面试官，请从以下维度评估候选人的回答：
1. 准确性（Accuracy）：回答内容的正确程度
2. 完整性（Completeness）：是否覆盖了所有要点
3. 逻辑性（Logic）：思路是否清晰，论证是否合理
4. 深度（Depth）：对问题的理解深度

请为每个维度给出0-100的分数，并提供具体反馈。输出JSON格式。"""
        
        user_prompt = f"""问题：{question}

候选人回答：
{answer}

{f'参考上下文：{context}' if context else ''}
{f'预期要点：{chr(10).join(expected_points)}' if expected_points else ''}

请评估此回答并返回JSON格式：
{{
    "accuracy": {{"score": 85, "feedback": "具体反馈"}},
    "completeness": {{"score": 80, "feedback": "具体反馈"}},
    "logic": {{"score": 90, "feedback": "具体反馈"}},
    "depth": {{"score": 75, "feedback": "具体反馈"}},
    "total_score": 82.5,
    "overall_feedback": "总体评价",
    "suggestions": ["改进建议1", "改进建议2"]
}}"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            response = await self.chat_completion(messages, temperature=0.3)
            # Parse JSON from response
            import json
            # Extract JSON if wrapped in markdown
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0]
            else:
                json_str = response
            
            return json.loads(json_str.strip())
        except Exception as e:
            # Return default evaluation if parsing fails
            return {
                "accuracy": {"score": 70, "feedback": "无法准确评估"},
                "completeness": {"score": 70, "feedback": "无法准确评估"},
                "logic": {"score": 70, "feedback": "无法准确评估"},
                "depth": {"score": 70, "feedback": "无法准确评估"},
                "total_score": 70.0,
                "overall_feedback": f"评估过程出错: {str(e)}",
                "suggestions": ["请重试"]
            }


class VectorStoreService:
    """向量数据库服务"""
    
    def __init__(self):
        self.client = chromadb.PersistentClient(
            path=settings.CHROMA_DB_PATH,
            settings=ChromaSettings(
                anonymized_telemetry=False
            )
        )
        self.glm4_service = GLM4Service()
    
    async def create_collection(self, name: str):
        """创建集合"""
        return self.client.get_or_create_collection(name=name)
    
    async def add_documents(
        self,
        collection_name: str,
        documents: List[str],
        metadatas: List[dict],
        ids: Optional[List[str]] = None
    ):
        """添加文档到向量库"""
        collection = await self.create_collection(collection_name)
        
        # Generate embeddings
        embeddings = []
        for doc in documents:
            embedding = await self.glm4_service.generate_embedding(doc)
            embeddings.append(embedding)
        
        # Generate IDs if not provided
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in documents]
        
        collection.add(
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        return ids
    
    async def search(
        self,
        collection_name: str,
        query: str,
        top_k: int = None,
        filter_dict: Optional[dict] = None
    ) -> List[dict]:
        """搜索相似文档"""
        collection = await self.create_collection(collection_name)
        
        # Generate query embedding
        query_embedding = await self.glm4_service.generate_embedding(query)
        
        # Search
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k or settings.TOP_K_RETRIEVAL,
            where=filter_dict
        )
        
        # Format results
        formatted_results = []
        for i in range(len(results['ids'][0])):
            formatted_results.append({
                'id': results['ids'][0][i],
                'document': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i]
            })
        
        return formatted_results
    
    async def delete_collection(self, name: str):
        """删除集合"""
        try:
            self.client.delete_collection(name=name)
            return True
        except:
            return False


# Global instances
glm4_service = GLM4Service()
vector_store = VectorStoreService()
