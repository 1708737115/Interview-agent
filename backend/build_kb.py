#!/usr/bin/env python3
"""
简化版知识库构建脚本
直接使用绝对导入路径
"""

import os
import sys
import json
import logging
import asyncio
from pathlib import Path
from datetime import datetime

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()

# 目录设置
BASE_DIR = Path("/home/fengxu/mylib/interview-agent/backend")
DATA_DIR = BASE_DIR / "data"
REPOS_DIR = DATA_DIR / "repos"
PROCESSED_DIR = DATA_DIR / "processed"

# 添加app目录到Python路径（用于Pylance识别导入）
sys.path.insert(0, str(BASE_DIR / "app"))

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# 核心仓库列表
CORE_REPOS = [
    "https://github.com/yongxinz/backend-interview.git",
    "https://github.com/2637309949/go-interview.git",
    "https://github.com/yongxinz/gopher.git"
]


class SimpleBuilder:
    """简化版知识库构建器"""
    
    def __init__(self):
        self.questions = []
        
    async def run(self, limit=None):
        """运行构建流程"""
        logger.info("=" * 60)
        logger.info("开始构建面试题知识库")
        logger.info("=" * 60)
        
        # Step 1: 同步GitHub仓库
        logger.info("\n[Step 1/4] 同步GitHub仓库...")
        await self._sync_repos()
        
        # Step 2: 解析Markdown
        logger.info("\n[Step 2/4] 解析Markdown文件...")
        self._parse_all_repos()
        
        if limit:
            self.questions = self.questions[:limit]
            logger.info(f"限制处理前 {limit} 题")
        
        # Step 3: LLM增强
        logger.info("\n[Step 3/4] LLM增强处理...")
        await self._enhance_questions()
        
        # Step 4: 保存结果
        logger.info("\n[Step 4/4] 保存结果...")
        self._save_results()
        
        self._print_stats()
        
        logger.info("\n" + "=" * 60)
        logger.info("知识库构建完成！")
        logger.info("=" * 60)
    
    async def _sync_repos(self):
        """同步GitHub仓库"""
        import subprocess
        
        REPOS_DIR.mkdir(parents=True, exist_ok=True)
        
        for repo_url in CORE_REPOS:
            repo_name = repo_url.split('/')[-1].replace('.git', '')
            repo_dir = REPOS_DIR / repo_name
            
            try:
                if repo_dir.exists():
                    logger.info(f"更新仓库: {repo_name}")
                    subprocess.run(
                        ["git", "pull"],
                        cwd=repo_dir,
                        capture_output=True,
                        check=True
                    )
                else:
                    logger.info(f"克隆仓库: {repo_name}")
                    subprocess.run(
                        ["git", "clone", "--depth", "1", repo_url, str(repo_dir)],
                        capture_output=True,
                        check=True
                    )
                logger.info(f"✓ {repo_name} 同步完成")
            except Exception as e:
                logger.error(f"✗ {repo_name} 同步失败: {e}")
    
    def _parse_all_repos(self):
        """解析所有仓库"""
        from knowledge_base.markdown_parser import MarkdownParser
        
        parser = MarkdownParser()
        
        for repo_dir in REPOS_DIR.iterdir():
            if repo_dir.is_dir():
                logger.info(f"解析仓库: {repo_dir.name}")
                questions = parser.parse_directory(repo_dir, repo_dir.name)
                self.questions.extend(questions)
                logger.info(f"  - 解析 {len(questions)} 题")
        
        logger.info(f"\n总计解析: {len(self.questions)} 题")
    
    async def _enhance_questions(self):
        """LLM增强处理"""
        from services.llm_service import GLM4Service
        
        llm = GLM4Service()
        
        for i, q in enumerate(self.questions):
            try:
                # 生成标签
                tags_prompt = f"""分析以下面试题，提取3-5个核心技术知识点标签。

问题：{q.text}
答案：{q.answer[:300]}

直接输出标签列表，每行一个，不要解释。"""
                
                tags_result = await llm.chat_completion(
                    [{"role": "user", "content": tags_prompt}],
                    temperature=0.3
                )
                q.tags = [t.strip() for t in tags_result.split('\n') if t.strip()][:5]
                
                # 评估难度
                diff_prompt = f"""评估以下面试题的难度(1-5)：
1级-基础概念，2级-基础应用，3级-进阶原理，4级-深度原理，5级-系统设计

问题：{q.text}

只输出数字(1-5)。"""
                
                diff_result = await llm.chat_completion(
                    [{"role": "user", "content": diff_prompt}],
                    temperature=0.1
                )
                
                try:
                    q.difficulty = max(1, min(5, int(diff_result.strip())))
                except:
                    q.difficulty = 3
                
                # 生成追问点
                followup_prompt = f"""基于以下面试题，生成2个可以追问的点。

问题：{q.text}
答案：{q.answer[:300]}

输出追问问题，每行一个。"""
                
                followup_result = await llm.chat_completion(
                    [{"role": "user", "content": followup_prompt}],
                    temperature=0.5
                )
                q.followup_points = [f.strip() for f in followup_result.split('\n') if f.strip()][:2]
                
                if (i + 1) % 5 == 0:
                    logger.info(f"  已处理 {i+1}/{len(self.questions)} 题")
                    
            except Exception as e:
                logger.error(f"处理题目 {i+1} 失败: {e}")
                q.tags = []
                q.difficulty = 3
                q.followup_points = []
    
    def _save_results(self):
        """保存结果"""
        # 保存为JSON
        output_file = PROCESSED_DIR / "enhanced_questions.json"
        
        data = []
        for q in self.questions:
            data.append({
                "id": q.id,
                "text": q.text,
                "answer": q.answer,
                "category": q.category,
                "difficulty": q.difficulty,
                "tags": q.tags,
                "followup_points": q.followup_points,
                "source_repo": q.source_repo,
                "source_file": q.source_file,
                "code_examples": [{"code": c.code, "language": c.language} for c in q.code_examples]
            })
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"结果已保存: {output_file}")
        logger.info(f"共 {len(data)} 题")
    
    def _print_stats(self):
        """打印统计"""
        categories = {}
        difficulties = {i: 0 for i in range(1, 6)}
        total_followups = 0
        
        for q in self.questions:
            categories[q.category] = categories.get(q.category, 0) + 1
            difficulties[q.difficulty] = difficulties.get(q.difficulty, 0) + 1
            total_followups += len(q.followup_points)
        
        logger.info("\n" + "=" * 60)
        logger.info("知识库统计")
        logger.info("=" * 60)
        logger.info(f"总问题数: {len(self.questions)}")
        logger.info(f"\n分类分布:")
        for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            logger.info(f"  - {cat}: {count} 题")
        logger.info(f"\n难度分布:")
        for diff, count in difficulties.items():
            logger.info(f"  - 等级{diff}: {count} 题")
        logger.info(f"\n总追问点: {total_followups}")


async def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None, help="限制处理数量")
    args = parser.parse_args()
    
    builder = SimpleBuilder()
    await builder.run(limit=args.limit)


if __name__ == "__main__":
    asyncio.run(main())
