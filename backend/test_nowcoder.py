#!/usr/bin/env python3
"""
测试牛客风格学习模块
由于牛客有反爬机制，这里测试解析功能
"""

import sys
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(__file__).parent / "app"))

from knowledge_base.nowcoder_style_learning import InterviewStyleAnalyzer, InterviewPost

# 测试用面经内容（模拟牛客面经格式）
test_post_content = """
# 字节跳动后端开发面经

## 一面（45分钟）

面试官是个年轻小哥，先让我自我介绍。

**面试官问：** 介绍一下你的项目经历。

我介绍了实习期间做的微服务改造项目，用了Spring Cloud。

**面试官接着问：** 你们服务是怎么做服务发现的？

我说用了Eureka，然后讲了讲原理。

**面试官追问：** Eureka的心跳机制是怎么实现的？如果服务挂了，Eureka多久能感知到？

这个问题我没答好，只说了一个大概的默认值。

**面试官继续问：** 那如果Eureka本身挂了怎么办？

我说可以用集群部署，然后他让我详细讲讲Eureka的集群同步机制。

**面试官问：** 你项目里提到了Redis，说说Redis的持久化机制吧。

我讲了RDB和AOF两种机制。

**面试官追问：** 如果RDB和AOF同时开启，Redis重启时加载哪个？为什么？

这个我答对了，AOF优先，因为数据更完整。

**面试官问：** 最后一个问题，手写一个LRU缓存。

我用LinkedHashMap实现了一个。

面试官说："整体还可以，基础还可以再扎实一点。"

## 二面（1小时）

二面面试官看起来比较有经验。

**面试官问：** 看你简历有分布式经验，说说分布式事务吧。

我讲了2PC、3PC和TCC。

**面试官追问：** 2PC有什么问题？如果协调者挂了怎么办？

我说了阻塞问题和单点故障。

**面试官继续深挖：** 那3PC解决了吗？还是有其他方案？

我没答好，只说了个大概。

**面试官问：** 设计一个秒杀系统，要考虑哪些问题？

我说了限流、缓存、队列这些。

**面试官追问：** 如果库存只有100件，但是来了10000个请求，怎么保证不超卖？

我讲了Redis预减库存 + 异步下单。

**面试官继续问：** 如果Redis也扛不住呢？

我说可以加本地缓存 + 令牌桶限流。

面试官点了点头，没说什么。

## 总结

字节面试问得比较深，每一轮都有2-3个追问，考察思维深度。建议把原理吃透，不要只停留在使用层面。
"""


def test_analyzer():
    """测试分析器"""
    print("=" * 60)
    print("测试面试风格分析器")
    print("=" * 60)
    
    # 创建测试帖子
    post = InterviewPost(
        id="test_001",
        title="字节跳动后端开发面经",
        content=test_post_content,
        company="字节跳动",
        position="后端开发",
        source_url="https://www.nowcoder.com/discuss/test"
    )
    
    # 创建分析器
    analyzer = InterviewStyleAnalyzer()
    
    # 分析帖子
    print("\n分析面经帖子...")
    result = analyzer.analyze_post(post)
    
    print("\n分析结果：")
    print(f"标题: {result['title']}")
    print(f"公司: {result['company']}")
    print(f"岗位: {result['position']}")
    print(f"面试官话术: {result['total_quotes']} 条")
    print(f"面试问题: {result['total_questions']} 个")
    print(f"追问模式: {result['total_followups']} 个")
    print(f"面试轮次: {result['interview_rounds']} 轮")
    
    print("\n面试官话术示例:")
    for i, quote in enumerate(result['interviewer_quotes'][:5], 1):
        print(f"  {i}. {quote}")
    
    print("\n追问模式示例:")
    for i, followup in enumerate(result['followup_patterns'][:3], 1):
        print(f"  {i}. {followup}")
    
    # 测试风格画像生成
    print("\n" + "=" * 60)
    print("测试风格画像生成")
    print("=" * 60)
    
    # 创建多个帖子模拟
    posts = [post]
    
    # 生成风格画像
    profile = analyzer.generate_style_profile(posts)
    
    print("\n风格画像摘要:")
    print(f"分析帖子数: {profile['total_posts_analyzed']}")
    print(f"总话术数: {profile['total_interviewer_quotes']}")
    print(f"总问题数: {profile['total_questions']}")
    print(f"平均每场面试题: {profile['avg_questions_per_interview']:.1f}")
    
    print("\n提问风格分析:")
    style = profile['questioning_style']
    print(f"  直接式比例: {style['direct_ratio']:.2%}")
    print(f"  引导式比例: {style['guiding_ratio']:.2%}")
    print(f"  主导风格: {style['dominant_style']}")
    
    print("\n追问模式分析:")
    followup = profile['followup_patterns']
    print(f"  追问触发类型: {followup['trigger_types']}")
    
    print("\n面试流程分析:")
    flow = profile['interview_flow']
    print(f"  常见轮次: {flow['common_rounds']}")
    print(f"  考察重点: {flow['common_focus_areas']}")
    
    print("\n热门面试题TOP3:")
    for i, q in enumerate(profile['popular_questions'][:3], 1):
        print(f"  {i}. {q}")
    
    return profile


def main():
    print("\n" + "=" * 60)
    print("牛客风格学习模块测试")
    print("=" * 60 + "\n")
    
    try:
        profile = test_analyzer()
        
        print("\n" + "=" * 60)
        print("测试完成！")
        print("=" * 60)
        print("\n✅ 风格分析功能正常")
        print("\n注意: 实际使用时需要处理牛客反爬机制")
        print("建议：")
        print("  1. 使用代理IP池")
        print("  2. 添加随机延迟")
        print("  3. 模拟浏览器行为")
        print("  4. 限制爬取频率")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
