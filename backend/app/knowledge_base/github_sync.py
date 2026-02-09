#!/usr/bin/env python3
"""
GitHub面试题库自动同步模块
每周批量处理，自动爬取前十相关领域面试题仓库
"""

import os
import json
import subprocess
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 配置
DATA_DIR = Path("/home/fengxu/mylib/interview-agent/backend/data")
REPOS_DIR = DATA_DIR / "repos"
PROCESSED_DIR = DATA_DIR / "processed"
STATE_FILE = DATA_DIR / "sync_state.json"

# 核心仓库列表（初始）
CORE_REPOS = [
    {
        "url": "https://github.com/yongxinz/backend-interview.git",
        "name": "backend-interview",
        "category": "backend",
        "priority": 1
    },
    {
        "url": "https://github.com/2637309949/go-interview.git",
        "name": "go-interview",
        "category": "go",
        "priority": 1
    },
    {
        "url": "https://github.com/yongxinz/gopher.git",
        "name": "gopher",
        "category": "go",
        "priority": 2
    }
]

# 搜索关键词（用于发现新仓库）
SEARCH_KEYWORDS = [
    "backend interview questions",
    "go interview",
    "java interview",
    "system design interview",
    "redis interview",
    "mysql interview",
    "network interview"
]


class GitHubSyncManager:
    """GitHub数据同步管理器"""
    
    def __init__(self):
        self.state = self._load_state()
        REPOS_DIR.mkdir(parents=True, exist_ok=True)
        PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    
    def _load_state(self) -> Dict:
        """加载同步状态"""
        if STATE_FILE.exists():
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "last_sync": None,
            "repos": {},
            "processed_files": [],
            "total_questions": 0
        }
    
    def _save_state(self):
        """保存同步状态"""
        self.state["last_sync"] = datetime.now().isoformat()
        with open(STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)
    
    def sync_core_repos(self):
        """同步核心仓库"""
        logger.info("开始同步核心仓库...")
        
        for repo in CORE_REPOS:
            repo_name = repo["name"]
            repo_url = repo["url"]
            repo_dir = REPOS_DIR / repo_name
            
            try:
                if repo_dir.exists():
                    # 更新已有仓库
                    logger.info(f"更新仓库: {repo_name}")
                    subprocess.run(
                        ["git", "pull", "origin", "main"],
                        cwd=repo_dir,
                        capture_output=True,
                        check=True
                    )
                    self.state["repos"][repo_name] = {
                        "status": "updated",
                        "last_update": datetime.now().isoformat(),
                        **repo
                    }
                else:
                    # 克隆新仓库
                    logger.info(f"克隆仓库: {repo_name}")
                    subprocess.run(
                        ["git", "clone", repo_url, str(repo_dir)],
                        capture_output=True,
                        check=True
                    )
                    self.state["repos"][repo_name] = {
                        "status": "cloned",
                        "last_update": datetime.now().isoformat(),
                        **repo
                    }
                
                logger.info(f"✓ {repo_name} 同步完成")
                
            except subprocess.CalledProcessError as e:
                logger.error(f"✗ {repo_name} 同步失败: {e}")
                self.state["repos"][repo_name] = {
                    "status": "failed",
                    "error": str(e),
                    **repo
                }
    
    def discover_new_repos(self, max_results: int = 10) -> List[Dict]:
        """发现新的热门面试题仓库"""
        logger.info("发现新的面试题仓库...")
        
        discovered = []
        
        for keyword in SEARCH_KEYWORDS:
            try:
                # GitHub Search API
                url = f"https://api.github.com/search/repositories"
                params = {
                    "q": f"{keyword} stars:>100 language:markdown",
                    "sort": "stars",
                    "order": "desc",
                    "per_page": 5
                }
                
                response = requests.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    for item in data.get("items", []):
                        repo_info = {
                            "name": item["name"],
                            "url": item["clone_url"],
                            "stars": item["stargazers_count"],
                            "description": item["description"],
                            "category": self._categorize_repo(item["name"], item["description"]),
                            "priority": 3
                        }
                        
                        # 检查是否已存在
                        if repo_info["name"] not in self.state["repos"]:
                            discovered.append(repo_info)
                            
            except Exception as e:
                logger.error(f"搜索关键词 '{keyword}' 失败: {e}")
        
        # 去重并按stars排序
        seen = set()
        unique_repos = []
        for repo in sorted(discovered, key=lambda x: x["stars"], reverse=True):
            if repo["name"] not in seen and len(unique_repos) < max_results:
                seen.add(repo["name"])
                unique_repos.append(repo)
        
        logger.info(f"发现 {len(unique_repos)} 个新仓库")
        return unique_repos
    
    def _categorize_repo(self, name: str, description: Optional[str]) -> str:
        """根据名称和描述分类仓库"""
        text = f"{name} {description or ''}".lower()
        
        if "go" in text or "golang" in text:
            return "go"
        elif "java" in text:
            return "java"
        elif "python" in text:
            return "python"
        elif "system design" in text or "system-design" in text:
            return "system-design"
        elif "redis" in text:
            return "redis"
        elif "mysql" in text or "database" in text:
            return "database"
        elif "network" in text or "networking" in text:
            return "network"
        else:
            return "backend"
    
    def get_markdown_files(self) -> List[Path]:
        """获取所有Markdown文件"""
        md_files = []
        
        for repo_dir in REPOS_DIR.iterdir():
            if repo_dir.is_dir():
                for md_file in repo_dir.rglob("*.md"):
                    # 过滤node_modules等非代码文件
                    if "node_modules" not in str(md_file) and ".git" not in str(md_file):
                        md_files.append(md_file)
        
        logger.info(f"找到 {len(md_files)} 个Markdown文件")
        return md_files
    
    def run_sync(self, discover: bool = False):
        """运行同步流程"""
        logger.info("=" * 50)
        logger.info("开始GitHub数据同步")
        logger.info("=" * 50)
        
        # 1. 同步核心仓库
        self.sync_core_repos()
        
        # 2. 发现新仓库（可选）
        if discover:
            new_repos = self.discover_new_repos(max_results=10)
            if new_repos:
                logger.info(f"\n发现 {len(new_repos)} 个新仓库，准备同步...")
                for repo in new_repos:
                    # 这里可以自动克隆新发现的仓库
                    pass
        
        # 3. 保存状态
        self._save_state()
        
        logger.info("=" * 50)
        logger.info("同步完成")
        logger.info(f"已同步仓库数: {len(self.state['repos'])}")
        logger.info(f"上次同步时间: {self.state['last_sync']}")
        logger.info("=" * 50)


def main():
    """主函数"""
    sync_manager = GitHubSyncManager()
    
    # 检查是否需要同步（每周一次）
    last_sync = sync_manager.state.get("last_sync")
    if last_sync:
        last_sync_time = datetime.fromisoformat(last_sync)
        if datetime.now() - last_sync_time < timedelta(days=7):
            logger.info("距离上次同步不足7天，跳过本次同步")
            return
    
    # 运行同步
    sync_manager.run_sync(discover=False)


if __name__ == "__main__":
    main()
