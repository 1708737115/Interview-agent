#!/usr/bin/env python3
"""
知识库构建主流程
整合数据同步、解析、增强、向量化的完整流程
"""

import sys
import json
import logging
from pathlib import Path
from typing import Optional

# 添加路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from knowledge_base.github_sync import GitHubSyncManager
from knowledge_base.markdown_parser import MarkdownParser, Question
from knowledge_base.llm_enhancer import LLMEnhancer
from knowledge_base.vector_store import VectorStore
from services.llm_service import GLM4Service

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class KnowledgeBaseBuilder:
    """知识库构建器"""
    
    def __init__(self):
        self.sync_manager = GitHubSyncManager()
        self.parser = MarkdownParser()
        self.enhancer = LLMEnhancer()
        self.vector_store = VectorStore()
        self.llm_service = GLM4Service()
        
        # 目录
        self.data_dir = Path("/home/fengxu/mylib/interview-agent/backend/data")
        self.repos_dir = self.data_dir / "repos"
        self.processed_dir = self.data_dir / "processed"
        self.processed_dir.mkdir(exist_ok=True)
    
    def run_full_pipeline(self, skip_sync: bool = False, limit: Optional[int] = None):
        """
        运行完整构建流程
        
        Args:
            skip_sync: 是否跳过GitHub同步
            limit: 限制处理的问题数量（用于测试）
        """
        logger.info("=" * 60)
        logger.info("开始构建面试题知识库")
        logger.info("=" * 60)
        
        # Step 1: 同步GitHub仓库
        if not skip_sync:
            logger.info("\n[Step 1/4] 同步GitHub仓库...")
            self.sync_manager.run_sync(discover=False)
        else:
            logger.info("\n[Step 1/4] 跳过GitHub同步")
        
        # Step 2: 解析Markdown文件
        logger.info("\n[Step 2/4] 解析Markdown文件...")
        all_questions = []
        
        for repo_name in self.sync_manager.state.get("repos", {}).keys():
            repo_dir = self.repos_dir / repo_name
            if repo_dir.exists():
                logger.info(f"解析仓库: {repo_name}")
                questions = self.parser.parse_directory(repo_dir, repo_name)
                all_questions.extend(questions)
                logger.info(f"  - 解析 {len(questions)} 题")
        
        logger.info(f"\n总计解析: {len(all_questions)} 题")
        
        if limit:
            all_questions = all_questions[:limit]
            logger.info(f"限制处理前 {limit} 题")
        
        # Step 3: LLM增强处理
        logger.info("\n[Step 3/4] LLM增强处理...")
        enhanced_questions = self.enhancer.enhance_questions(all_questions)
        
        # 保存增强后的JSON
        enhanced_file = self.processed_dir / "enhanced_questions.json"
        self.enhancer.export_to_json(enhanced_questions, str(enhanced_file))
        logger.info(f"增强结果保存到: {enhanced_file}")
        
        # Step 4: 向量化存储
        logger.info("\n[Step 4/4] 向量化存储...")
        self._vectorize_and_store(enhanced_questions)
        
        # 输出统计
        self._print_stats(enhanced_questions)
        
        logger.info("\n" + "=" * 60)
        logger.info("知识库构建完成")
        logger.info("=" * 60)
    
    def _vectorize_and_store(self, questions: list):
        """向量化并存储"""
        
        # 删除旧数据
        logger.info("清理旧向量数据...")
        self.vector_store.delete_collection()
        self.vector_store = VectorStore()
        
        # 分批处理
        batch_size = 20
        total = len(questions)
        
        for i in range(0, total, batch_size):
            batch = questions[i:i+batch_size]
            
            # 准备数据
            ids = []
            texts = []
            metadatas = []
            
            for q in batch:
                embed_text = self.enhancer.generate_embedding_text(q)
                
                ids.append(q.id)
                texts.append(embed_text)
                metadatas.append({
                    'category': q.category,
                    'difficulty': q.difficulty,
                    'tags': ','.join(q.tags[:5]),  # 限制标签数量
                    'source_repo': q.source_repo,
                    'question_text': q.text[:100],
                    'has_code': len(q.code_examples) > 0
                })
            
            # 生成向量
            logger.info(f"生成向量 {i+1}-{min(i+batch_size, total)}/{total}")
            try:
                import asyncio
                embeddings = asyncio.run(
                    self.llm_service.generate_embeddings(texts)
                )
                
                # 存储
                self.vector_store.add_questions(ids, texts, embeddings, metadatas)
                
            except Exception as e:
                logger.error(f"向量化失败: {e}")
                continue
    
    def _print_stats(self, questions: list):
        """打印统计信息"""
        logger.info("\n" + "=" * 60)
        logger.info("知识库统计")
        logger.info("=" * 60)
        
        # 分类统计
        categories = {}
        difficulties = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        total_code = 0
        total_followups = 0
        
        for q in questions:
            categories[q.category] = categories.get(q.category, 0) + 1
            difficulties[q.difficulty] = difficulties.get(q.difficulty, 0) + 1
            total_code += len(q.code_examples)
            total_followups += len(q.followup_points)
        
        logger.info(f"\n总问题数: {len(questions)}")
        
        logger.info(f"\n分类分布:")
        for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            logger.info(f"  - {cat}: {count} 题")
        
        logger.info(f"\n难度分布:")
        for diff, count in difficulties.items():
            bar = "█" * (count // max(difficulties.values()) * 20 + 1) if max(difficulties.values()) > 0 else ""
            logger.info(f"  - 等级{diff}: {count} 题 {bar}")
        
        logger.info(f"\n代码示例: {total_code} 个")
        logger.info(f"追问点: {total_followups} 个")
        logger.info(f"平均每题追问: {total_followups/len(questions):.1f}")
        
        # 向量库统计
        vector_stats = self.vector_store.get_stats()
        logger.info(f"\n向量库:")
        logger.info(f"  - 总问题数: {vector_stats['total_questions']}")


def quick_test():
    """快速测试流程"""
    logger.info("运行快速测试（处理前10题）...")
    
    builder = KnowledgeBaseBuilder()
    builder.run_full_pipeline(skip_sync=False, limit=10)


def full_build():
    """完整构建"""
    logger.info("运行完整构建流程...")
    
    builder = KnowledgeBaseBuilder()
    builder.run_full_pipeline(skip_sync=False)


def update_only():
    """仅更新（不重新同步GitHub）"""
    logger.info("运行更新流程（跳过GitHub同步）...")
    
    builder = KnowledgeBaseBuilder()
    builder.run_full_pipeline(skip_sync=True)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="面试题知识库构建工具")
    parser.add_argument(
        "mode",
        choices=["test", "build", "update"],
        default="test",
        help="运行模式: test(测试10题), build(完整构建), update(仅更新)"
    )
    
    args = parser.parse_args()
    
    if args.mode == "test":
        quick_test()
    elif args.mode == "build":
        full_build()
    elif args.mode == "update":
        update_only()
