#!/bin/bash
# 股票风险控制策略 - 2%原则仓位计算
# 快捷命令: /risk

show_help() {
    echo "📊 股票风险控制策略 - 2%原则"
    echo "========================="
    echo ""
    echo "用法:"
    echo "  /risk 集中 <现价> <止损价>   - 计算2%集中仓位"
    echo "  /risk 2%集中 <现价> <止损价>"
    echo "  /risk 分散 <现价> <止损价>   - 计算2%分散仓位"
    echo "  /risk 2%分散 <现价> <止损价>"
    echo ""
    echo "示例:"
    echo "  /risk 集中 2960 2457"
    echo ""
}

calculate_concentrated() {
    current_price=$1
    stop_loss=$2

    # 计算止损跌幅
    stop_loss_drop=$(awk "BEGIN {printf "%.4f", 1 - $stop_loss / $current_price}")

    # 计算仓位
    position=$(awk "BEGIN {printf "%.1f", 2 / ($stop_loss_drop * 100)}")

    # 百分比格式
    stop_loss_drop_pct=$(awk "BEGIN {printf "%.2f", $stop_loss_drop * 100}")

    echo "📊 2%集中仓位计算"
    echo "────────────────────────"
    echo "标的：自定义"
    echo "现价：$current_price"
    echo "止损价：$stop_loss"
    echo "止损跌幅：${stop_loss_drop_pct}%"
    echo "建议仓位：${position}%"
    echo "────────────────────────"
    echo "✅ 风险控制：最多承担本金2%风险"
}

calculate_diversified() {
    current_price=$1
    stop_loss=$2

    echo "📊 2%分散仓位计算"
    echo "────────────────────────"
    echo "标的：自定义"
    echo "现价：$current_price"
    echo "止损价：$stop_loss"
    echo "────────────────────────"
    echo "💡 2%分散：每个品种独立计算2%风险"
    echo "适合多品种组合投资"
}

if [ $# -eq 0 ]; then
    show_help
    exit 0
fi

case "$1" in
    集中|2%集中)
        if [ $# -ne 3 ]; then
            echo "❌ 请提供现价和止损价"
            echo "示例: /risk 集中 2960 2457"
            exit 1
        fi
        calculate_concentrated $2 $3
        ;;
    分散|2%分散)
        if [ $# -ne 3 ]; then
            echo "❌ 请提供现价和止损价"
            echo "示例: /risk 分散 2960 2457"
            exit 1
        fi
        calculate_diversified $2 $3
        ;;
    *)
        echo "❌ 未知命令: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
