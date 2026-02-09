#!/usr/bin/env python3
"""
面试官风格配置加载器
加载和管理基于牛客面经分析的面试官风格配置
"""

import json
import random
from pathlib import Path
from typing import Dict, List, Optional


class InterviewerStyleConfig:
    """面试官风格配置管理器"""
    
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "data" / "nowcoder" / "interviewer_style_config.json"
        
        self.config_path = Path(config_path)
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """加载配置文件"""
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # 返回默认配置
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """获取默认配置"""
        return {
            "interviewer_persona": {
                "name": "资深后端技术面试官",
                "style": "专业严谨但不失亲和力"
            },
            "questioning_style": {
                "dominant_style": "direct",
                "direct_ratio": 0.6,
                "guiding_ratio": 0.4
            },
            "followup_strategy": {
                "max_followups": 8,
                "triggers": {
                    "deep": {"weight": 0.35, "phrases": ["为什么{concept}要这样设计？"]},
                    "incomplete": {"weight": 0.3, "phrases": ["能否再详细说说？"]},
                    "wrong": {"weight": 0.2, "phrases": ["这里有个小问题，你再想想？"]},
                    "scenario": {"weight": 0.15, "phrases": ["在实际项目中，{topic}会遇到什么挑战？"]}
                }
            },
            "interview_flow": {
                "total_duration": 45,
                "phases": [
                    {"name": "opening", "duration": 3},
                    {"name": "technical_basic", "duration": 20},
                    {"name": "project_deep_dive", "duration": 12},
                    {"name": "system_design", "duration": 8},
                    {"name": "closing", "duration": 2}
                ]
            }
        }
    
    def get_persona(self) -> Dict:
        """获取面试官人设"""
        return self.config.get("interviewer_persona", {})
    
    def get_questioning_style(self) -> str:
        """获取提问风格"""
        return self.config.get("questioning_style", {}).get("dominant_style", "direct")
    
    def get_followup_strategy(self) -> Dict:
        """获取追问策略"""
        return self.config.get("followup_strategy", {})
    
    def get_max_followups(self) -> int:
        """获取最大追问次数"""
        return self.config.get("followup_strategy", {}).get("max_followups", 8)
    
    def get_interview_flow(self) -> List[Dict]:
        """获取面试流程"""
        return self.config.get("interview_flow", {}).get("phases", [])
    
    def get_total_duration(self) -> int:
        """获取面试总时长（分钟）"""
        return self.config.get("interview_flow", {}).get("total_duration", 45)
    
    def get_response_template(self, category: str) -> str:
        """获取回复模板"""
        templates = self.config.get("response_templates", {}).get(category, ["好的，继续。"])
        return random.choice(templates)
    
    def get_followup_phrase(self, trigger_type: str, **kwargs) -> str:
        """
        获取追问话术
        
        Args:
            trigger_type: 触发类型 (deep/incomplete/wrong/scenario)
            **kwargs: 模板变量，如 concept, topic, scenario等
        """
        triggers = self.config.get("followup_strategy", {}).get("triggers", {})
        trigger_config = triggers.get(trigger_type, {})
        
        phrases = trigger_config.get("phrases", ["能详细说说吗？"])
        phrase = random.choice(phrases)
        
        # 替换模板变量
        try:
            return phrase.format(**kwargs)
        except:
            return phrase
    
    def get_question_pattern(self, style: str = None) -> str:
        """获取提问模板"""
        if style is None:
            style = self.get_questioning_style()
        
        patterns = self.config.get("questioning_style", {}).get("patterns", {}).get(style, [])
        if patterns:
            return random.choice(patterns)
        return "请介绍一下{topic}"
    
    def get_evaluation_criteria(self) -> Dict:
        """获取评估标准"""
        return self.config.get("evaluation_criteria", {})
    
    def get_common_questions(self, category: str) -> List[str]:
        """获取常见面试题"""
        return self.config.get("common_questions", {}).get(category, [])


# 便捷函数
def get_style_config() -> InterviewerStyleConfig:
    """获取风格配置实例"""
    return InterviewerStyleConfig()


if __name__ == "__main__":
    # 测试
    config = get_style_config()
    
    print("=" * 60)
    print("面试官风格配置")
    print("=" * 60)
    
    print("\n面试官人设:")
    persona = config.get_persona()
    print(f"  名称: {persona.get('name')}")
    print(f"  风格: {persona.get('style')}")
    
    print("\n提问风格:")
    print(f"  主导风格: {config.get_questioning_style()}")
    
    print("\n追问策略:")
    strategy = config.get_followup_strategy()
    print(f"  最大追问次数: {strategy.get('max_followups')}")
    
    print("\n追问话术示例:")
    print(f"  深度追问: {config.get_followup_phrase('deep', concept='Goroutine')}")
    print(f"  补充追问: {config.get_followup_phrase('incomplete')}")
    print(f"  场景追问: {config.get_followup_phrase('scenario', topic='Redis缓存')}")
    
    print("\n面试流程:")
    for phase in config.get_interview_flow():
        print(f"  - {phase['name']}: {phase['duration']}分钟 ({phase['description']})")
    
    print("\n回复模板示例:")
    print(f"  鼓励: {config.get_response_template('encouragement')}")
    print(f"  引导: {config.get_response_template('guidance')}")
    print(f"  总结: {config.get_response_template('closing')}")
    
    print("\n" + "=" * 60)
    print("配置加载成功！")
    print("=" * 60)
