#!/usr/bin/env python3
"""
股票风险控制策略 - 2%原则仓位计算
"""

import sys

def show_help():
    print("📊 股票风险控制策略 - 2%原则")
    print("=========================")
    print()
    print("用法:")
    print("  /risk 集中 <现价> <止损价>   - 计算2%集中仓位")
    print("  /risk 2%集中 <现价> <止损价>")
    print("  /risk 分散 <现价> <止损价>   - 计算2%分散仓位")
    print("  /risk 2%分散 <现价> <止损价>")
    print()
    print("示例:")
    print("  /risk 集中 2960 2457")
    print()

def calculate_concentrated(current_price, stop_loss):
    # 计算止损跌幅
    stop_loss_drop = 1 - stop_loss / current_price

    # 计算仓位
    # 2% / 止损跌幅 = 仓位
    position = 2 / (stop_loss_drop * 100)

    # 百分比格式
    stop_loss_drop_pct = stop_loss_drop * 100
    position_pct = position * 100

    print("📊 2%集中仓位计算")
    print("────────────────────────")
    print(f"标的：自定义")
    print(f"现价：{current_price}")
    print(f"止损价：{stop_loss}")
    print(f"止损跌幅：{stop_loss_drop_pct:.2f}%")
    print(f"建议仓位：{position_pct:.1f}%")
    print("────────────────────────")
    print("✅ 风险控制：最多承担本金2%风险")

def calculate_diversified(current_price, stop_loss):
    print("📊 2%分散仓位计算")
    print("────────────────────────")
    print(f"标的：自定义")
    print(f"现价：{current_price}")
    print(f"止损价：{stop_loss}")
    print("────────────────────────")
    print("💡 2%分散：每个品种独立计算2%风险")
    print("适合多品种组合投资")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        show_help()
        sys.exit(0)

    command = sys.argv[1]

    if command in ["集中", "2%集中"]:
        if len(sys.argv) != 4:
            print("❌ 请提供现价和止损价")
            print("示例: /risk 集中 2960 2457")
            sys.exit(1)
        try:
            current_price = float(sys.argv[2])
            stop_loss = float(sys.argv[3])
            calculate_concentrated(current_price, stop_loss)
        except ValueError:
            print("❌ 现价和止损价必须是数字")
            sys.exit(1)

    elif command in ["分散", "2%分散"]:
        if len(sys.argv) != 4:
            print("❌ 请提供现价和止损价")
            print("示例: /risk 分散 2960 2457")
            sys.exit(1)
        try:
            current_price = float(sys.argv[2])
            stop_loss = float(sys.argv[3])
            calculate_diversified(current_price, stop_loss)
        except ValueError:
            print("❌ 现价和止损价必须是数字")
            sys.exit(1)

    else:
        print(f"❌ 未知命令: {command}")
        print()
        show_help()
        sys.exit(1)
