#!/usr/bin/env python3
"""
上传文件生命周期管理脚本
功能：
1. 7天后自动压缩文件
2. 30天后自动删除文件

使用方法:
    python3 uploads_lifecycle.py [--uploads-dir UPLOADS_DIR] [--dry-run]

建议添加到crontab定时执行:
    0 2 * * * cd /path/to/project && python3 uploads_lifecycle.py
"""

import os
import sys
import gzip
import shutil
import argparse
from datetime import datetime, timedelta
from pathlib import Path


def compress_file(file_path: Path) -> bool:
    """压缩单个文件"""
    try:
        compressed_path = file_path.with_suffix(file_path.suffix + '.gz')
        with open(file_path, 'rb') as f_in:
            with gzip.open(compressed_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        # 删除原文件
        os.remove(file_path)
        
        # 保留原始修改时间
        stat = os.stat(compressed_path)
        os.utime(compressed_path, (stat.st_atime, stat.st_mtime))
        
        return True
    except Exception as e:
        print(f"   ❌ 压缩失败 {file_path.name}: {e}")
        return False


def delete_file(file_path: Path) -> bool:
    """删除文件"""
    try:
        os.remove(file_path)
        return True
    except Exception as e:
        print(f"   ❌ 删除失败 {file_path.name}: {e}")
        return False


def manage_uploads_lifecycle(uploads_dir: str, dry_run: bool = False):
    """管理上传文件的生命周期"""
    
    uploads_path = Path(uploads_dir)
    
    if not uploads_path.exists():
        print(f"❌ 目录不存在: {uploads_dir}")
        return
    
    print("=" * 60)
    print("📁 上传文件生命周期管理")
    print("=" * 60)
    print(f"目标目录: {uploads_dir}")
    print(f"运行模式: {'模拟运行 (dry-run)' if dry_run else '实际执行'}")
    print()
    
    # 时间阈值
    now = datetime.now()
    compress_threshold = now - timedelta(days=7)  # 7天压缩
    delete_threshold = now - timedelta(days=30)   # 30天删除
    
    # 统计
    compress_candidates = []
    delete_candidates = []
    
    # 扫描文件
    for file_path in uploads_path.iterdir():
        if not file_path.is_file():
            continue
        
        # 跳过.gitkeep和已压缩的文件
        if file_path.name == '.gitkeep' or file_path.suffix == '.gz':
            continue
        
        # 获取文件修改时间
        try:
            mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
        except Exception as e:
            print(f"⚠️  无法获取文件时间: {file_path.name} ({e})")
            continue
        
        # 检查是否需要删除（30天）
        if mtime < delete_threshold:
            delete_candidates.append((file_path, mtime))
        # 检查是否需要压缩（7天，但不包括7天内要删除的）
        elif mtime < compress_threshold and file_path.suffix != '.gz':
            compress_candidates.append((file_path, mtime))
    
    # 处理删除
    if delete_candidates:
        print(f"🗑️  发现 {len(delete_candidates)} 个文件超过30天，将被删除:")
        for file_path, mtime in delete_candidates:
            age_days = (now - mtime).days
            print(f"   - {file_path.name} ({age_days}天前)")
            
            if not dry_run:
                if delete_file(file_path):
                    print(f"     ✅ 已删除")
        print()
    else:
        print("✓ 没有需要删除的文件（30天以上）")
        print()
    
    # 处理压缩
    if compress_candidates:
        print(f"🗜️  发现 {len(compress_candidates)} 个文件超过7天，将被压缩:")
        for file_path, mtime in compress_candidates:
            age_days = (now - mtime).days
            size_mb = file_path.stat().st_size / (1024 * 1024)
            print(f"   - {file_path.name} ({age_days}天前, {size_mb:.1f}MB)")
            
            if not dry_run:
                if compress_file(file_path):
                    print(f"     ✅ 已压缩")
        print()
    else:
        print("✓ 没有需要压缩的文件（7天以上）")
        print()
    
    # 统计信息
    print("=" * 60)
    print("📊 处理统计")
    print("=" * 60)
    print(f"删除文件: {len(delete_candidates)} 个")
    print(f"压缩文件: {len(compress_candidates)} 个")
    print()
    
    # 计算节省空间（仅实际执行时）
    if not dry_run and compress_candidates:
        total_saved = sum(
            file_path.stat().st_size * 0.7  # 假设压缩率70%
            for file_path, _ in compress_candidates
        )
        print(f"💾 预计节省空间: {total_saved / (1024 * 1024):.1f} MB")
    
    print()
    print("✅ 生命周期管理完成")


def main():
    parser = argparse.ArgumentParser(description='上传文件生命周期管理')
    parser.add_argument('--uploads-dir', default='uploads',
                       help='上传文件目录 (默认: uploads)')
    parser.add_argument('--dry-run', action='store_true',
                       help='模拟运行，不实际执行操作')
    
    args = parser.parse_args()
    
    manage_uploads_lifecycle(args.uploads_dir, args.dry_run)


if __name__ == '__main__':
    main()
