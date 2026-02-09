#!/usr/bin/env python3
"""
向量数据库初始化与管理
用于存储面试题的向量表示，支持语义检索
"""

import os
import json
import logging
from typing import List, Dict, Optional
from pathlib import Path

import chromadb
from chromadb.config import Settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 配置
CHROMA_DB_PATH = "/home/fengxu/mylib/interview-agent/backend/data/chroma_db"
COLLECTION_NAME = "interview_questions"


class VectorStore:
    """向量数据库存储管理器"""
    
    def __init__(self, db_path: str = CHROMA_DB_PATH):
        self.db_path = db_path
        os.makedirs(db_path, exist_ok=True)
        
        # 初始化ChromaDB
        self.client = chromadb.PersistentClient(
            path=db_path,
            settings=Settings(
                anonymized_telemetry=False
            )
        )
        
        # 获取或创建集合
        self.collection = self._get_or_create_collection()
    
    def _get_or_create_collection(self):
        """获取或创建集合"""
        try:
            # 尝试获取已有集合
            collection = self.client.get_collection(name=COLLECTION_NAME)
            logger.info(f"使用已有集合: {COLLECTION_NAME}")
            return collection
        except:
            # 创建新集合
            collection = self.client.create_collection(
                name=COLLECTION_NAME,
                metadata={"description": "后端面试题向量库"}
            )
            logger.info(f"创建新集合: {COLLECTION_NAME}")
            return collection
    
    def add_questions(self, 
                     question_ids: List[str],
                     texts: List[str],
                     embeddings: List[List[float]],
                     metadatas: List[Dict]):
        """
        批量添加问题到向量库
        
        Args:
            question_ids: 问题ID列表
            texts: 问题文本列表
            embeddings: 向量表示列表
            metadatas: 元数据列表
        """
        try:
            self.collection.add(
                ids=question_ids,
                documents=texts,
                embeddings=embeddings,
                metadatas=metadatas
            )
            logger.info(f"成功添加 {len(question_ids)} 个问题到向量库")
        except Exception as e:
            logger.error(f"添加问题失败: {e}")
            raise
    
    def search_similar(self, 
                      query_embedding: List[float],
                      n_results: int = 5,
                      filter_dict: Optional[Dict] = None) -> List[Dict]:
        """
        语义相似度搜索
        
        Args:
            query_embedding: 查询向量
            n_results: 返回结果数量
            filter_dict: 过滤条件（如：{"category": "go"}）
            
        Returns:
            相似问题列表
        """
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=filter_dict
            )
            
            # 格式化结果
            formatted_results = []
            for i in range(len(results['ids'][0])):
                formatted_results.append({
                    'id': results['ids'][0][i],
                    'text': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i]
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"搜索失败: {e}")
            return []
    
    def get_by_category(self, category: str, limit: int = 100) -> List[Dict]:
        """按分类获取问题"""
        try:
            results = self.collection.get(
                where={"category": category},
                limit=limit
            )
            
            questions = []
            for i in range(len(results['ids'])):
                questions.append({
                    'id': results['ids'][i],
                    'text': results['documents'][i],
                    'metadata': results['metadatas'][i]
                })
            
            return questions
            
        except Exception as e:
            logger.error(f"获取分类失败: {e}")
            return []
    
    def get_question_count(self) -> int:
        """获取问题总数"""
        try:
            return self.collection.count()
        except:
            return 0
    
    def delete_collection(self):
        """删除整个集合（慎用）"""
        try:
            self.client.delete_collection(name=COLLECTION_NAME)
            logger.info(f"删除集合: {COLLECTION_NAME}")
        except Exception as e:
            logger.error(f"删除集合失败: {e}")
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        try:
            count = self.collection.count()
            
            # 获取各分类数量
            categories = {}
            all_data = self.collection.get()
            
            for metadata in all_data.get('metadatas', []):
                cat = metadata.get('category', 'unknown')
                categories[cat] = categories.get(cat, 0) + 1
            
            return {
                'total_questions': count,
                'categories': categories
            }
            
        except Exception as e:
            logger.error(f"获取统计失败: {e}")
            return {'total_questions': 0, 'categories': {}}


class VectorStoreManager:
    """向量库管理器（高级功能）"""
    
    def __init__(self):
        self.vector_store = VectorStore()
    
    def import_from_json(self, json_file: str, embedding_service):
        """
        从JSON文件导入问题到向量库
        
        Args:
            json_file: JSON文件路径
            embedding_service: 向量化服务
        """
        logger.info(f"从 {json_file} 导入数据...")
        
        with open(json_file, 'r', encoding='utf-8') as f:
            questions = json.load(f)
        
        logger.info(f"加载 {len(questions)} 个问题")
        
        # 分批处理
        batch_size = 50
        for i in range(0, len(questions), batch_size):
            batch = questions[i:i+batch_size]
            
            ids = []
            texts = []
            metadatas = []
            
            for q in batch:
                # 生成嵌入文本
                embed_text = f"问题: {q.get('text', '')}\n答案: {q.get('answer', '')[:500]}\n标签: {', '.join(q.get('tags', []))}"
                
                ids.append(q.get('id', f"q_{i}"))
                texts.append(embed_text)
                metadatas.append({
                    'category': q.get('category', 'general'),
                    'difficulty': q.get('difficulty', 3),
                    'tags': ','.join(q.get('tags', [])),
                    'source_repo': q.get('source_repo', ''),
                    'question_text': q.get('text', '')[:200],
                    'has_code': len(q.get('code_examples', [])) > 0
                })
            
            # 生成向量
            logger.info(f"生成向量 {i+1}-{min(i+batch_size, len(questions))}/{len(questions)}")
            embeddings = embedding_service.generate_embeddings(texts)
            
            # 添加到向量库
            self.vector_store.add_questions(ids, texts, embeddings, metadatas)
        
        logger.info("导入完成")
    
    def rebuild_collection(self, json_file: str, embedding_service):
        """重建整个集合"""
        logger.info("重建向量库集合...")
        
        # 删除旧集合
        self.vector_store.delete_collection()
        
        # 重新初始化
        self.vector_store = VectorStore()
        
        # 导入数据
        self.import_from_json(json_file, embedding_service)
        
        logger.info("重建完成")


# 便捷函数
def get_vector_store() -> VectorStore:
    """获取向量库实例"""
    return VectorStore()


if __name__ == "__main__":
    # 测试
    store = VectorStore()
    
    stats = store.get_stats()
    print(f"向量库统计:")
    print(f"  总问题数: {stats['total_questions']}")
    print(f"  分类分布: {stats['categories']}")
