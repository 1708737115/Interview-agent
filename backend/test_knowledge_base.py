#!/usr/bin/env python3
"""
快速测试脚本 - 验证知识库构建流程
"""

import sys
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from knowledge_base.markdown_parser import MarkdownParser, Question

# 测试用Markdown内容
test_md_content = """
# Go语言面试题

## Go语言new和make关键字的区别

`new`和`make`是Go语言中用于内存分配的两个内置函数，它们有以下区别：

**new函数：**
- 用于分配内存，返回指向该内存的指针
- 返回的是该类型的零值
- 适用于值类型（int, float, struct等）

**make函数：**
- 只用于slice、map、channel这三种引用类型的初始化
- 返回的是该类型本身，不是指针
- 会初始化内部数据结构

示例代码：
```go
// new示例
p := new(int)  // *int类型，值为0

// make示例
s := make([]int, 10)  // []int类型，长度为10
m := make(map[string]int)  // map类型
```

## Go语言切片是如何扩容的？

Go语言切片的扩容机制如下：

1. 如果新长度小于1024，容量翻倍
2. 如果新长度大于等于1024，容量增加25%
3. 实际分配时可能会分配更大的内存以保证内存对齐

扩容时会重新分配内存，将原数据复制到新内存中。

## Go语言的GPM调度模型是什么？

GPM是Go语言的运行时调度模型：

- **G (Goroutine)**：Go协程，轻量级线程
- **P (Processor)**：逻辑处理器，负责执行Goroutine
- **M (Machine)**：系统线程，由操作系统管理

调度流程：
1. P从本地队列获取G执行
2. 如果本地队列为空，从全局队列获取
3. 如果全局队列也为空，从其他P偷取G

这种模型实现了高效的并发调度，可以在少量系统线程上运行大量Goroutine。
"""


def test_parser():
    """测试Markdown解析器"""
    print("=" * 60)
    print("测试Markdown解析器")
    print("=" * 60)
    
    # 创建临时文件
    test_file = Path("/tmp/test_interview.md")
    test_file.write_text(test_md_content, encoding='utf-8')
    
    # 解析
    parser = MarkdownParser()
    questions = parser.parse_file(test_file, "test-repo")
    
    print(f"\n解析完成，共 {len(questions)} 道题目\n")
    
    for i, q in enumerate(questions, 1):
        print(f"题目 {i}:")
        print(f"  ID: {q.id}")
        print(f"  问题: {q.text}")
        print(f"  分类: {q.category}")
        print(f"  答案长度: {len(q.answer)} 字符")
        print(f"  代码示例: {len(q.code_examples)} 个")
        print()
    
    return questions


def test_enhancer(questions):
    """测试LLM增强器（模拟）"""
    print("=" * 60)
    print("测试LLM增强器（使用规则回退）")
    print("=" * 60)
    
    # 这里使用规则回退，不调用真实LLM
    for q in questions:
        # 基于规则的标签
        q.tags = []
        text = f"{q.text} {q.answer}".lower()
        
        if "new" in text or "make" in text:
            q.tags.append("内存分配")
        if "slice" in text or "切片" in text:
            q.tags.append("slice")
            q.tags.append("数据结构")
        if "gmp" in text or "调度" in text:
            q.tags.append("GPM调度")
            q.tags.append("并发")
        
        # 基于规则的难度
        if "底层" in text or "源码" in text or "模型" in text:
            q.difficulty = 4
        elif "扩容" in text or "机制" in text:
            q.difficulty = 3
        else:
            q.difficulty = 2
        
        # 基于规则的追问点
        q.followup_points = []
        if "扩容" in text:
            q.followup_points.append("扩容后的内存是如何分配的？")
        if "调度" in text:
            q.followup_points.append("Goroutine阻塞时M会怎样？")
    
    print("\n增强结果:\n")
    for i, q in enumerate(questions, 1):
        print(f"题目 {i}:")
        print(f"  难度: {q.difficulty}/5")
        print(f"  标签: {q.tags}")
        print(f"  追问点: {q.followup_points}")
        print()


def main():
    print("\n" + "=" * 60)
    print("知识库构建流程测试")
    print("=" * 60 + "\n")
    
    # 步骤1: 解析
    questions = test_parser()
    
    # 步骤2: 增强（使用规则）
    test_enhancer(questions)
    
    print("=" * 60)
    print("测试完成！")
    print("=" * 60)
    print("\n下一步：")
    print("1. 配置GLM-4 API密钥")
    print("2. 运行完整知识库构建流程")
    print("3. 启动后端服务")


if __name__ == "__main__":
    main()
