#!/usr/bin/env python3
"""
基准测试运行脚本

使用方法:
    python scripts/run_benchmarks.py                    # 运行所有基准测试
    python scripts/run_benchmarks.py --compare          # 与基线比较
    python scripts/run_benchmarks.py --save-baseline    # 保存基线
    python scripts/run_benchmarks.py --filter ipv4      # 只运行IPv4相关测试
"""

import argparse
import subprocess
import sys
import os
from pathlib import Path


def run_command(cmd, description):
    """运行命令并处理错误"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd,
                                shell=True,
                                check=True,
                                capture_output=True,
                                text=True)
        print(f"✅ {description} 完成")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} 失败: {e}")
        print(f"错误输出: {e.stderr}")
        return None


def main():
    parser = argparse.ArgumentParser(description="运行IPPool基准测试")
    parser.add_argument("--compare", action="store_true", help="与基线比较")
    parser.add_argument("--save-baseline",
                        action="store_true",
                        help="保存当前结果为基线")
    parser.add_argument("--filter",
                        type=str,
                        help="过滤测试（如：ipv4, ipv6, add, remove等）")
    parser.add_argument("--output",
                        type=str,
                        default="benchmark-results",
                        help="输出文件名")
    parser.add_argument("--rounds", type=int, default=5, help="最小运行轮数")
    parser.add_argument("--warmup",
                        action="store_true",
                        default=True,
                        help="启用预热")

    args = parser.parse_args()

    # 确保在项目根目录
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    # 构建pytest命令
    cmd_parts = [
        "pytest",
        "tests/test_benchmarks.py",
        "--benchmark-only",
        f"--benchmark-min-rounds={args.rounds}",
        "--benchmark-disable-gc",
        "--benchmark-sort=name",
        "--benchmark-columns=min,max,mean,stddev,rounds,iterations",
    ]

    if args.warmup:
        cmd_parts.append("--benchmark-warmup=on")

    if args.filter:
        cmd_parts.append(f"-k {args.filter}")

    if args.compare:
        cmd_parts.extend([
            "--benchmark-compare=.benchmarks/baseline.json",
            "--benchmark-compare-fail=mean:10%"
        ])

    if args.save_baseline:
        cmd_parts.extend(
            [f"--benchmark-save={args.output}", "--benchmark-save-data"])

    cmd = " ".join(cmd_parts)

    print("🚀 开始运行基准测试...")
    print(f"命令: {cmd}")
    print("-" * 50)

    # 运行基准测试
    output = run_command(cmd, "基准测试")

    if output:
        print("\n📊 基准测试结果:")
        print(output)

        if args.save_baseline:
            print(f"\n💾 基线已保存到 .benchmarks/{args.output}/")

    print("\n✨ 基准测试完成!")


if __name__ == "__main__":
    main()
