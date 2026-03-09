#!/usr/bin/env python3
"""
股票风险控制策略 - 数据库管理
更新支持：成本价、总资金、直接输入总金额、小于2%仓位
"""

import sys
import os
import sqlite3
from datetime import datetime

# 数据库路径
DB_PATH = "$DATA_DIR/stock_risk_control.db"

# 默认总资金
DEFAULT_TOTAL_CAPITAL = 100000

def init_db():
    """初始化数据库"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    if not os.path.exists(DB_PATH):
        print("📦 初始化数据库...")
        with open("$SKILL_DIR/init_db.sql", "r") as f:
            schema = f.read()
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.executescript(schema)
        conn.commit()
        conn.close()
        print("✅ 数据库初始化完成！")
    else:
        pass

def get_conn():
    """获取数据库连接"""
    return sqlite3.connect(DB_PATH)

def show_help():
    """显示帮助"""
    print("📊 股票风险控制策略 - 数据库管理")
    print("==============================")
    print()
    print("用法:")
    print("  /risk 列表                                           - 查看所有持仓股票（默认不显示总值，不显示ID）")
    print("  /risk 列表 显示总值                                 - 查看所有持仓股票（显示总值，不显示ID）")
    print("  /risk 列表 显示ID                                   - 查看所有持仓股票（不显示总值，显示ID）")
    print("  /risk 列表 显示总值 显示ID                         - 查看所有持仓股票（显示总值和ID）")
    print("  /risk 添加 <名称> <代码> <模式> <持有数量> <成本价> <止损价> <现价> [总资金] [持有理由]")
    print("  /risk 更新 <id> <现价> [持有理由]                   - 更新现价（每日更新）")
    print("  /risk 删除 <id>                                       - 软删除股票（数据还在）")
    print("  /risk 历史                                           - 查看历史记录（包括已删除）")
    print("  /risk 集中 <现价> <止损价> [目标风险]              - 计算集中仓位（目标风险默认2%）")
    print("  /risk 分散 <现价> <止损价> [目标风险]              - 计算2%分散仓位（目标风险默认2%）")
    print()
    print("说明:")
    print("  - 仓位/总值: 可以输入百分比（如11.8）或总金额（如5000）")
    print("  - 目标风险: 可以自定义（如1%、0.5%），默认2%")
    print("  - 总资金: 默认100000，可自定义")
    print("  - 持有理由: 可选，记录持有这只股票的理由")
    print("  - 列表默认不显示总值和ID，需要时用'显示总值'或'显示ID'")
    print("  - 模式: '集中'或'分散'（之前的'集中'/'2%分散'也兼容）")
    print()
    print("示例:")
    print("  /risk 集中 2960 2457")
    print("  /risk 集中 2960 2457 1")
    print("  /risk 添加 上证50 000016 集中 11.8 2457 2457 2960")
    print("  /risk 添加 股票B 000010 集中 5000 1.00 0.80 1.00 100000 \"AI趋势\"")
    print("  /risk 添加 股票A 688008 集中 80 80 80 80 100000 \"芯片龙头\"")
    print()

def calculate_pnl(current_price, cost_price, position, total_value):
    """计算盈亏（基于成本价）"""
    if cost_price and cost_price > 0:
        pnl_percent = (current_price - cost_price) / cost_price * 100
    else:
        pnl_percent = 0
    
    pnl = total_value * (pnl_percent / 100) if total_value else 0
    return pnl, pnl_percent

def calculate_total_value(quantity, current_price):
    """根据持有数量和现价计算个股市值"""
    total_value = quantity * current_price
    return total_value

def calculate_position(total_value, total_capital=DEFAULT_TOTAL_CAPITAL):
    """根据个股市值和总资金计算仓位百分比"""
    position_percent = (total_value / total_capital) * 100
    return position_percent

def calculate_concentrated(current_price, stop_loss, target_risk=2):
    """计算集中仓位（支持自定义目标风险）"""
    stop_loss_drop = 1 - stop_loss / current_price
    if stop_loss_drop <= 0:
        print("❌ 止损价必须小于现价")
        return
    
    position = target_risk / (stop_loss_drop * 100)
    position_pct = position * 100
    stop_loss_drop_pct = stop_loss_drop * 100
    
    print(f"📊 {target_risk}%集中仓位计算")
    print("────────────────────────")
    print(f"标的：自定义")
    print(f"现价：{current_price}")
    print(f"止损价：{stop_loss}")
    print(f"止损跌幅：{stop_loss_drop_pct:.2f}%")
    print(f"目标风险：{target_risk}%")
    print(f"建议仓位：{position_pct:.1f}%")
    print("────────────────────────")
    print(f"✅ 风险控制：最多承担本金{target_risk}%风险")
    
    return position_pct

def calculate_diversified(current_price, stop_loss, target_risk=2):
    """计算分散仓位（支持自定义目标风险）"""
    print(f"📊 {target_risk}%分散仓位计算")
    print("────────────────────────")
    print(f"标的：自定义")
    print(f"现价：{current_price}")
    print(f"止损价：{stop_loss}")
    print(f"目标风险：{target_risk}%")
    print("────────────────────────")
    print(f"💡 {target_risk}%分散：每个品种独立计算{target_risk}%风险")
    print("适合多品种组合投资")

def calculate_2pct_concentrated_position(current_price, stop_loss):
    """计算集中建议仓位"""
    if not stop_loss or stop_loss <= 0 or current_price <= 0:
        return None
    
    stop_loss_drop = 1 - stop_loss / current_price
    if stop_loss_drop <= 0:
        return None
    
    # 集中仓位 = 2% / 止损跌幅
    position = 2 / (stop_loss_drop * 100) * 100
    return position

def get_simple_suggestion(mode, current_price, stop_loss, position, hold_reason):
    """新建议规则：围绕集中和2%分散，加上止损价相关规则"""
    if not stop_loss or stop_loss <= 0:
        return "-"
    
    # 先检查止损价相关规则
    if current_price <= stop_loss:
        # 跌穿止损价 → 清仓
        return "🆘 清仓"
    
    # 计算距离止损价的百分比
    drop_to_stop = (current_price - stop_loss) / current_price * 100
    if drop_to_stop <= 10:
        # 离止损价10%以内 → 注意
        return "⚠️ 注意"
    
    # 简化模式名称
    mode_simple = mode
    if mode == "集中":
        mode_simple = "集中"
    elif mode == "2%分散":
        mode_simple = "分散"
    
    if mode_simple == "分散":
        # 分散的：仓位≤2% → 建议继续观察
        if position <= 2:
            return "👀 观察"
        else:
            return "-"
    elif mode_simple == "集中":
        # 计算集中建议仓位
        suggested_position = calculate_2pct_concentrated_position(current_price, stop_loss)
        if not suggested_position:
            return "-"
        
        if position > suggested_position:
            # 大于集中建议仓位 → 建议降低到x%
            return f"⚠️ 降低到{suggested_position:.1f}%"
        else:
            # 仓位≤集中建议仓位
            if not hold_reason or hold_reason.strip() == "":
                # 缺买入理由 → 建议补充买入理由
                return "📝 补充理由"
            else:
                # 有买入理由 → 建议耐心持有
                return "✅ 持有"
    else:
        return "-"

def list_stocks(show_deleted=False, show_total=False, show_id=False, show_cost=False, show_quantity=False, show_mode=False, show_reason=False, show_code=False):
    """列出股票"""
    init_db()
    conn = get_conn()
    cursor = conn.cursor()
    
    if show_deleted:
        cursor.execute("""
            SELECT id, name, code, mode, quantity, position, total_value, 
                   cost_price, stop_loss, current_price, hold_reason, pnl_percent, 
                   created_at, is_deleted, deleted_at
            FROM stocks
            ORDER BY position DESC
        """)
    else:
        cursor.execute("""
            SELECT id, name, code, mode, quantity, position, total_value, 
                   cost_price, stop_loss, current_price, hold_reason, pnl_percent
            FROM stocks
            WHERE is_deleted = 0
            ORDER BY position DESC
        """)
    
    stocks = cursor.fetchall()
    conn.close()
    
    if not stocks:
        print("📭 暂无持仓股票")
        return
    
    # 简化模式名称
    def simplify_mode(mode):
        if mode == "集中":
            return "集中"
        elif mode == "2%分散":
            return "分散"
        else:
            return mode
    
    print("📊 持仓股票列表")
    if show_total:
        if show_id:
            if show_cost:
                if show_mode:
                    if show_reason:
                        print("=" * 156)
                        print(f"{'ID':<4} {'名称':<12} {'仓位':<7} {'盈亏%':<8} {'模式':<6} {'建议':<8} {'现价':<8} {'成本价':<8} {'止损价':<8} {'代码':<8} {'总值':<10} {'持有理由':<20}")
                        print("-" * 156)
                    else:
                        print("=" * 134)
                        print(f"{'ID':<4} {'名称':<12} {'仓位':<7} {'盈亏%':<8} {'模式':<6} {'建议':<8} {'现价':<8} {'成本价':<8} {'止损价':<8} {'代码':<8} {'总值':<10}")
                        print("-" * 134)
                else:
                    if show_reason:
                        print("=" * 148)
                        print(f"{'ID':<4} {'名称':<12} {'仓位':<7} {'盈亏%':<8} {'建议':<8} {'现价':<8} {'成本价':<8} {'止损价':<8} {'代码':<8} {'总值':<10} {'持有理由':<20}")
                        print("-" * 148)
                    else:
                        print("=" * 126)
                        print(f"{'ID':<4} {'名称':<12} {'仓位':<7} {'盈亏%':<8} {'建议':<8} {'现价':<8} {'成本价':<8} {'止损价':<8} {'代码':<8} {'总值':<10}")
                        print("-" * 126)
            else:
                if show_mode:
                    if show_reason:
                        print("=" * 141)
                        print(f"{'ID':<4} {'名称':<12} {'仓位':<7} {'盈亏%':<8} {'模式':<6} {'建议':<8} {'现价':<8} {'止损价':<8} {'代码':<8} {'总值':<10} {'持有理由':<20}")
                        print("-" * 141)
                    else:
                        print("=" * 119)
                        print(f"{'ID':<4} {'名称':<12} {'仓位':<7} {'盈亏%':<8} {'模式':<6} {'建议':<8} {'现价':<8} {'止损价':<8} {'代码':<8} {'总值':<10}")
                        print("-" * 119)
                else:
                    if show_reason:
                        print("=" * 133)
                        print(f"{'ID':<4} {'名称':<12} {'仓位':<7} {'盈亏%':<8} {'建议':<8} {'现价':<8} {'止损价':<8} {'代码':<8} {'总值':<10} {'持有理由':<20}")
                        print("-" * 133)
                    else:
                        print("=" * 111)
                        print(f"{'ID':<4} {'名称':<12} {'仓位':<7} {'盈亏%':<8} {'建议':<8} {'现价':<8} {'止损价':<8} {'代码':<8} {'总值':<10}")
                        print("-" * 111)
        else:
            if show_cost:
                if show_mode:
                    if show_reason:
                        print("=" * 151)
                        print(f"{'名称':<12} {'仓位':<7} {'盈亏%':<8} {'模式':<6} {'建议':<8} {'现价':<8} {'成本价':<8} {'止损价':<8} {'代码':<8} {'总值':<10} {'持有理由':<20}")
                        print("-" * 151)
                    else:
                        print("=" * 129)
                        print(f"{'名称':<12} {'仓位':<7} {'盈亏%':<8} {'模式':<6} {'建议':<8} {'现价':<8} {'成本价':<8} {'止损价':<8} {'代码':<8} {'总值':<10}")
                        print("-" * 129)
                else:
                    if show_reason:
                        print("=" * 143)
                        print(f"{'名称':<12} {'仓位':<7} {'盈亏%':<8} {'建议':<8} {'现价':<8} {'成本价':<8} {'止损价':<8} {'代码':<8} {'总值':<10} {'持有理由':<20}")
                        print("-" * 143)
                    else:
                        print("=" * 121)
                        print(f"{'名称':<12} {'仓位':<7} {'盈亏%':<8} {'建议':<8} {'现价':<8} {'成本价':<8} {'止损价':<8} {'代码':<8} {'总值':<10}")
                        print("-" * 121)
            else:
                if show_mode:
                    if show_reason:
                        print("=" * 136)
                        print(f"{'名称':<12} {'仓位':<7} {'盈亏%':<8} {'模式':<6} {'建议':<8} {'现价':<8} {'止损价':<8} {'代码':<8} {'总值':<10} {'持有理由':<20}")
                        print("-" * 136)
                    else:
                        print("=" * 114)
                        print(f"{'名称':<12} {'仓位':<7} {'盈亏%':<8} {'模式':<6} {'建议':<8} {'现价':<8} {'止损价':<8} {'代码':<8} {'总值':<10}")
                        print("-" * 114)
                else:
                    if show_reason:
                        print("=" * 128)
                        print(f"{'名称':<12} {'仓位':<7} {'盈亏%':<8} {'建议':<8} {'现价':<8} {'止损价':<8} {'代码':<8} {'总值':<10} {'持有理由':<20}")
                        print("-" * 128)
                    else:
                        print("=" * 106)
                        print(f"{'名称':<12} {'仓位':<7} {'盈亏%':<8} {'建议':<8} {'现价':<8} {'止损价':<8} {'代码':<8} {'总值':<10}")
                        print("-" * 106)
    else:
        if show_id:
            if show_cost:
                if show_mode:
                    if show_reason:
                        print("=" * 136)
                        print(f"{'ID':<4} {'名称':<12} {'仓位':<7} {'盈亏%':<8} {'模式':<6} {'建议':<8} {'现价':<8} {'成本价':<8} {'止损价':<8} {'代码':<8} {'持有理由':<20}")
                        print("-" * 136)
                    else:
                        print("=" * 114)
                        print(f"{'ID':<4} {'名称':<12} {'仓位':<7} {'盈亏%':<8} {'模式':<6} {'建议':<8} {'现价':<8} {'成本价':<8} {'止损价':<8} {'代码':<8}")
                        print("-" * 114)
                else:
                    if show_reason:
                        print("=" * 128)
                        print(f"{'ID':<4} {'名称':<12} {'仓位':<7} {'盈亏%':<8} {'建议':<8} {'现价':<8} {'成本价':<8} {'止损价':<8} {'代码':<8} {'持有理由':<20}")
                        print("-" * 128)
                    else:
                        print("=" * 106)
                        print(f"{'ID':<4} {'名称':<12} {'仓位':<7} {'盈亏%':<8} {'建议':<8} {'现价':<8} {'成本价':<8} {'止损价':<8} {'代码':<8}")
                        print("-" * 106)
            else:
                if show_mode:
                    if show_reason:
                        print("=" * 121)
                        print(f"{'ID':<4} {'名称':<12} {'仓位':<7} {'盈亏%':<8} {'模式':<6} {'建议':<8} {'现价':<8} {'止损价':<8} {'代码':<8} {'持有理由':<20}")
                        print("-" * 121)
                    else:
                        print("=" * 99)
                        print(f"{'ID':<4} {'名称':<12} {'仓位':<7} {'盈亏%':<8} {'模式':<6} {'建议':<8} {'现价':<8} {'止损价':<8} {'代码':<8}")
                        print("-" * 99)
                else:
                    if show_reason:
                        print("=" * 113)
                        print(f"{'ID':<4} {'名称':<12} {'仓位':<7} {'盈亏%':<8} {'建议':<8} {'现价':<8} {'止损价':<8} {'代码':<8} {'持有理由':<20}")
                        print("-" * 113)
                    else:
                        print("=" * 91)
                        print(f"{'ID':<4} {'名称':<12} {'仓位':<7} {'盈亏%':<8} {'建议':<8} {'现价':<8} {'止损价':<8} {'代码':<8}")
                        print("-" * 91)
        else:
            if show_cost:
                if show_mode:
                    if show_reason:
                        print("=" * 131)
                        print(f"{'名称':<12} {'仓位':<7} {'盈亏%':<8} {'模式':<6} {'建议':<8} {'现价':<8} {'成本价':<8} {'止损价':<8} {'代码':<8} {'持有理由':<20}")
                        print("-" * 131)
                    else:
                        print("=" * 109)
                        print(f"{'名称':<12} {'仓位':<7} {'盈亏%':<8} {'模式':<6} {'建议':<8} {'现价':<8} {'成本价':<8} {'止损价':<8} {'代码':<8}")
                        print("-" * 109)
                else:
                    if show_reason:
                        print("=" * 123)
                        print(f"{'名称':<12} {'仓位':<7} {'盈亏%':<8} {'建议':<8} {'现价':<8} {'成本价':<8} {'止损价':<8} {'代码':<8} {'持有理由':<20}")
                        print("-" * 123)
                    else:
                        print("=" * 101)
                        print(f"{'名称':<12} {'仓位':<7} {'盈亏%':<8} {'建议':<8} {'现价':<8} {'成本价':<8} {'止损价':<8} {'代码':<8}")
                        print("-" * 101)
            else:
                if show_mode:
                    if show_reason:
                        print("=" * 116)
                        print(f"{'名称':<12} {'仓位':<7} {'盈亏%':<8} {'模式':<6} {'建议':<8} {'现价':<8} {'止损价':<8} {'代码':<8} {'持有理由':<20}")
                        print("-" * 116)
                    else:
                        print("=" * 94)
                        print(f"{'名称':<12} {'仓位':<7} {'盈亏%':<8} {'模式':<6} {'建议':<8} {'现价':<8} {'止损价':<8} {'代码':<8}")
                        print("-" * 94)
                else:
                    if show_reason:
                        print("=" * 108)
                        print(f"{'名称':<12} {'仓位':<7} {'盈亏%':<8} {'建议':<8} {'现价':<8} {'止损价':<8} {'代码':<8} {'持有理由':<20}")
                        print("-" * 108)
                    else:
                        print("=" * 86)
                        print(f"{'名称':<12} {'仓位':<7} {'盈亏%':<8} {'建议':<8} {'现价':<8} {'止损价':<8} {'代码':<8}")
                        print("-" * 86)
    
    for stock in stocks:
        if show_deleted:
            stock_id, name, code, mode, quantity, position, total_value, cost_price, stop_loss, current_price, hold_reason, pnl_percent, created_at, is_deleted, deleted_at = stock
            deleted_mark = " [已删]" if is_deleted else ""
        else:
            stock_id, name, code, mode, quantity, position, total_value, cost_price, stop_loss, current_price, hold_reason, pnl_percent = stock
            deleted_mark = ""
        
        # 简化模式名称
        mode_simple = simplify_mode(mode)
        
        # 计算建议
        suggestion = get_simple_suggestion(mode, current_price, stop_loss, position, hold_reason)
        
        cost_display = f"{cost_price:.2f}" if cost_price else "-"
        # 盈亏%符号规则：盈利加+，亏损带-
        if pnl_percent is not None:
            if pnl_percent > 0:
                pnl_display = f"+{pnl_percent:.2f}%"
            else:
                pnl_display = f"{pnl_percent:.2f}%"
        else:
            pnl_display = "-"
        reason_display = hold_reason[:18] + ".." if hold_reason and len(hold_reason) > 18 else (hold_reason or "-")
        
        if show_total:
            if show_id:
                if show_cost:
                    if show_mode:
                        if show_reason:
                            print(f"{stock_id:<4} {name:<12} {position:.1f}% {pnl_display:<8} {mode_simple:<6} {suggestion:<8} {current_price:<8.2f} {cost_display:<8} {stop_loss:<8.2f} {code or '-':<8} {total_value:<10.0f} {reason_display:<20}{deleted_mark}")
                        else:
                            print(f"{stock_id:<4} {name:<12} {position:.1f}% {pnl_display:<8} {mode_simple:<6} {suggestion:<8} {current_price:<8.2f} {cost_display:<8} {stop_loss:<8.2f} {code or '-':<8} {total_value:<10.0f}{deleted_mark}")
                    else:
                        if show_reason:
                            print(f"{stock_id:<4} {name:<12} {position:.1f}% {pnl_display:<8} {suggestion:<8} {current_price:<8.2f} {cost_display:<8} {stop_loss:<8.2f} {code or '-':<8} {total_value:<10.0f} {reason_display:<20}{deleted_mark}")
                        else:
                            print(f"{stock_id:<4} {name:<12} {position:.1f}% {pnl_display:<8} {suggestion:<8} {current_price:<8.2f} {cost_display:<8} {stop_loss:<8.2f} {code or '-':<8} {total_value:<10.0f}{deleted_mark}")
                else:
                    if show_mode:
                        if show_reason:
                            print(f"{stock_id:<4} {name:<12} {position:.1f}% {pnl_display:<8} {mode_simple:<6} {suggestion:<8} {current_price:<8.2f} {stop_loss:<8.2f} {code or '-':<8} {total_value:<10.0f} {reason_display:<20}{deleted_mark}")
                        else:
                            print(f"{stock_id:<4} {name:<12} {position:.1f}% {pnl_display:<8} {mode_simple:<6} {suggestion:<8} {current_price:<8.2f} {stop_loss:<8.2f} {code or '-':<8} {total_value:<10.0f}{deleted_mark}")
                    else:
                        if show_reason:
                            print(f"{stock_id:<4} {name:<12} {position:.1f}% {pnl_display:<8} {suggestion:<8} {current_price:<8.2f} {stop_loss:<8.2f} {code or '-':<8} {total_value:<10.0f} {reason_display:<20}{deleted_mark}")
                        else:
                            print(f"{stock_id:<4} {name:<12} {position:.1f}% {pnl_display:<8} {suggestion:<8} {current_price:<8.2f} {stop_loss:<8.2f} {code or '-':<8} {total_value:<10.0f}{deleted_mark}")
            else:
                if show_cost:
                    if show_mode:
                        if show_reason:
                            print(f"{name:<12} {position:.1f}% {pnl_display:<8} {mode_simple:<6} {suggestion:<8} {current_price:<8.2f} {cost_display:<8} {stop_loss:<8.2f} {code or '-':<8} {total_value:<10.0f} {reason_display:<20}{deleted_mark}")
                        else:
                            print(f"{name:<12} {position:.1f}% {pnl_display:<8} {mode_simple:<6} {suggestion:<8} {current_price:<8.2f} {cost_display:<8} {stop_loss:<8.2f} {code or '-':<8} {total_value:<10.0f}{deleted_mark}")
                    else:
                        if show_reason:
                            print(f"{name:<12} {position:.1f}% {pnl_display:<8} {suggestion:<8} {current_price:<8.2f} {cost_display:<8} {stop_loss:<8.2f} {code or '-':<8} {total_value:<10.0f} {reason_display:<20}{deleted_mark}")
                        else:
                            print(f"{name:<12} {position:.1f}% {pnl_display:<8} {suggestion:<8} {current_price:<8.2f} {cost_display:<8} {stop_loss:<8.2f} {code or '-':<8} {total_value:<10.0f}{deleted_mark}")
                else:
                    if show_mode:
                        if show_reason:
                            print(f"{name:<12} {position:.1f}% {pnl_display:<8} {mode_simple:<6} {suggestion:<8} {current_price:<8.2f} {stop_loss:<8.2f} {code or '-':<8} {total_value:<10.0f} {reason_display:<20}{deleted_mark}")
                        else:
                            print(f"{name:<12} {position:.1f}% {pnl_display:<8} {mode_simple:<6} {suggestion:<8} {current_price:<8.2f} {stop_loss:<8.2f} {code or '-':<8} {total_value:<10.0f}{deleted_mark}")
                    else:
                        if show_reason:
                            print(f"{name:<12} {position:.1f}% {pnl_display:<8} {suggestion:<8} {current_price:<8.2f} {stop_loss:<8.2f} {code or '-':<8} {total_value:<10.0f} {reason_display:<20}{deleted_mark}")
                        else:
                            print(f"{name:<12} {position:.1f}% {pnl_display:<8} {suggestion:<8} {current_price:<8.2f} {stop_loss:<8.2f} {code or '-':<8} {total_value:<10.0f}{deleted_mark}")
        else:
            if show_id:
                if show_cost:
                    if show_mode:
                        if show_reason:
                            print(f"{stock_id:<4} {name:<12} {position:.1f}% {pnl_display:<8} {mode_simple:<6} {suggestion:<8} {current_price:<8.2f} {cost_display:<8} {stop_loss:<8.2f} {code or '-':<8} {reason_display:<20}{deleted_mark}")
                        else:
                            print(f"{stock_id:<4} {name:<12} {position:.1f}% {pnl_display:<8} {mode_simple:<6} {suggestion:<8} {current_price:<8.2f} {cost_display:<8} {stop_loss:<8.2f} {code or '-':<8}{deleted_mark}")
                    else:
                        if show_reason:
                            print(f"{stock_id:<4} {name:<12} {position:.1f}% {pnl_display:<8} {suggestion:<8} {current_price:<8.2f} {cost_display:<8} {stop_loss:<8.2f} {code or '-':<8} {reason_display:<20}{deleted_mark}")
                        else:
                            print(f"{stock_id:<4} {name:<12} {position:.1f}% {pnl_display:<8} {suggestion:<8} {current_price:<8.2f} {cost_display:<8} {stop_loss:<8.2f} {code or '-':<8}{deleted_mark}")
                else:
                    if show_mode:
                        if show_reason:
                            print(f"{stock_id:<4} {name:<12} {position:.1f}% {pnl_display:<8} {mode_simple:<6} {suggestion:<8} {current_price:<8.2f} {stop_loss:<8.2f} {code or '-':<8} {reason_display:<20}{deleted_mark}")
                        else:
                            print(f"{stock_id:<4} {name:<12} {position:.1f}% {pnl_display:<8} {mode_simple:<6} {suggestion:<8} {current_price:<8.2f} {stop_loss:<8.2f} {code or '-':<8}{deleted_mark}")
                    else:
                        if show_reason:
                            print(f"{stock_id:<4} {name:<12} {position:.1f}% {pnl_display:<8} {suggestion:<8} {current_price:<8.2f} {stop_loss:<8.2f} {code or '-':<8} {reason_display:<20}{deleted_mark}")
                        else:
                            print(f"{stock_id:<4} {name:<12} {position:.1f}% {pnl_display:<8} {suggestion:<8} {current_price:<8.2f} {stop_loss:<8.2f} {code or '-':<8}{deleted_mark}")
            else:
                if show_cost:
                    if show_mode:
                        if show_reason:
                            print(f"{name:<12} {position:.1f}% {pnl_display:<8} {mode_simple:<6} {suggestion:<8} {current_price:<8.2f} {cost_display:<8} {stop_loss:<8.2f} {code or '-':<8} {reason_display:<20}{deleted_mark}")
                        else:
                            print(f"{name:<12} {position:.1f}% {pnl_display:<8} {mode_simple:<6} {suggestion:<8} {current_price:<8.2f} {cost_display:<8} {stop_loss:<8.2f} {code or '-':<8}{deleted_mark}")
                    else:
                        if show_reason:
                            print(f"{name:<12} {position:.1f}% {pnl_display:<8} {suggestion:<8} {current_price:<8.2f} {cost_display:<8} {stop_loss:<8.2f} {code or '-':<8} {reason_display:<20}{deleted_mark}")
                        else:
                            print(f"{name:<12} {position:.1f}% {pnl_display:<8} {suggestion:<8} {current_price:<8.2f} {cost_display:<8} {stop_loss:<8.2f} {code or '-':<8}{deleted_mark}")
                else:
                    if show_mode:
                        if show_reason:
                            print(f"{name:<12} {position:.1f}% {pnl_display:<8} {mode_simple:<6} {suggestion:<8} {current_price:<8.2f} {stop_loss:<8.2f} {code or '-':<8} {reason_display:<20}{deleted_mark}")
                        else:
                            print(f"{name:<12} {position:.1f}% {pnl_display:<8} {mode_simple:<6} {suggestion:<8} {current_price:<8.2f} {stop_loss:<8.2f} {code or '-':<8}{deleted_mark}")
                    else:
                        if show_reason:
                            print(f"{name:<12} {position:.1f}% {pnl_display:<8} {suggestion:<8} {current_price:<8.2f} {stop_loss:<8.2f} {code or '-':<8} {reason_display:<20}{deleted_mark}")
                        else:
                            print(f"{name:<12} {position:.1f}% {pnl_display:<8} {suggestion:<8} {current_price:<8.2f} {stop_loss:<8.2f} {code or '-':<8}{deleted_mark}")
            else:
                if show_cost:
                    if show_mode:
                        print(f"{name:<12} {position:.1f}% {pnl_display:<8} {mode_simple:<6} {suggestion:<8} {current_price:<8.2f} {cost_display:<8} {stop_loss:<8.2f} {code or '-':<8} {reason_display:<20}{deleted_mark}")
                    else:
                        print(f"{name:<12} {position:.1f}% {pnl_display:<8} {suggestion:<8} {current_price:<8.2f} {cost_display:<8} {stop_loss:<8.2f} {code or '-':<8} {reason_display:<20}{deleted_mark}")
                else:
                    if show_mode:
                        print(f"{name:<12} {position:.1f}% {pnl_display:<8} {mode_simple:<6} {suggestion:<8} {current_price:<8.2f} {stop_loss:<8.2f} {code or '-':<8} {reason_display:<20}{deleted_mark}")
                    else:
                        print(f"{name:<12} {position:.1f}% {pnl_display:<8} {suggestion:<8} {current_price:<8.2f} {stop_loss:<8.2f} {code or '-':<8} {reason_display:<20}{deleted_mark}")
    
    if show_total:
        if show_cost:
            print("=" * 80)
        else:
            print("=" * 125)
    else:
        if show_cost:
            print("=" * 120)
        else:
            print("=" * 105)

def auto_adjust_mode(position):
    """根据仓位自动调整模式：仓位≤2%→分散，仓位>2%→集中"""
    if position <= 2:
        return "2%分散"
    else:
        return "集中"

def add_stock(name, code, mode, quantity, cost_price, stop_loss, current_price, total_capital=DEFAULT_TOTAL_CAPITAL, hold_reason=None):
    """添加股票（按持有数量输入）"""
    init_db()
    
    # 计算个股市值和仓位
    total_value = calculate_total_value(quantity, current_price)
    position = calculate_position(total_value, total_capital)
    
    print(f"💡 持有数量：{quantity:.0f}")
    print(f"   现价：{current_price:.2f}")
    print(f"   自动计算个股市值：{total_value:.0f}元")
    print(f"   自动计算仓位：{position:.1f}%（总资金：{total_capital:.0f}元）")
    
    # 自动调整模式
    mode = auto_adjust_mode(position)
    print(f"💡 自动调整模式为：{mode}（仓位：{position:.1f}%）")
    
    # 计算盈亏
    pnl, pnl_percent = calculate_pnl(current_price, cost_price, position, total_value)
    
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO stocks (name, code, mode, quantity, position, total_value, 
                           cost_price, stop_loss, current_price, hold_reason, pnl, pnl_percent)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (name, code, mode, quantity, position, total_value, cost_price, stop_loss, current_price, hold_reason, pnl, pnl_percent))
    
    stock_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    print(f"✅ 股票已添加！ID: {stock_id}")
    print(f"   名称: {name}")
    print(f"   模式: {mode}")
    print(f"   仓位: {position:.1f}%")
    print(f"   总值: {total_value:.0f}元")
    print(f"   成本价: {cost_price:.2f}")
    print(f"   止损价: {stop_loss:.2f}")
    print(f"   现价: {current_price:.2f}")
    if hold_reason:
        print(f"   持有理由: {hold_reason}")

def update_stock(stock_id, current_price, hold_reason=None, total_capital=DEFAULT_TOTAL_CAPITAL):
    """更新股票现价和持有理由（自动重新计算个股市值、仓位和盈亏）"""
    init_db()
    
    conn = get_conn()
    cursor = conn.cursor()
    
    # 获取旧数据
    cursor.execute("""
        SELECT cost_price, stop_loss, quantity
        FROM stocks
        WHERE id = ? AND is_deleted = 0
    """, (stock_id,))
    
    stock = cursor.fetchone()
    if not stock:
        print(f"❌ 找不到ID为 {stock_id} 的股票（或已删除）")
        conn.close()
        return
    
    cost_price, stop_loss, quantity = stock
    
    # 自动重新计算个股市值、仓位
    total_value = calculate_total_value(quantity, current_price)
    position = calculate_position(total_value, total_capital)
    
    # 自动重新计算盈亏
    pnl, pnl_percent = calculate_pnl(current_price, cost_price, position, total_value)
    
    # 自动调整模式
    mode = auto_adjust_mode(position)
    
    print(f"💡 自动重新计算：")
    print(f"   持有数量：{quantity:.0f}")
    print(f"   现价：{current_price:.2f}")
    print(f"   个股市值：{total_value:.0f}元")
    print(f"   仓位：{position:.1f}%")
    print(f"   模式：{mode}")
    
    # 更新
    if hold_reason:
        cursor.execute("""
            UPDATE stocks
            SET current_price = ?, hold_reason = ?, 
                total_value = ?, position = ?, mode = ?,
                pnl = ?, pnl_percent = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (current_price, hold_reason, total_value, position, mode, pnl, pnl_percent, stock_id))
    else:
        cursor.execute("""
            UPDATE stocks
            SET current_price = ?, 
                total_value = ?, position = ?, mode = ?,
                pnl = ?, pnl_percent = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (current_price, total_value, position, mode, pnl, pnl_percent, stock_id))
    
    conn.commit()
    conn.close()
    
    print(f"✅ 股票已更新！ID: {stock_id}")
    print(f"   现价: {current_price}")
    print(f"   盈亏: {pnl_percent:.2f}%")
    if hold_reason:
        print(f"   持有理由已更新: {hold_reason}")

def delete_stock(stock_id):
    """软删除股票"""
    init_db()
    
    conn = get_conn()
    cursor = conn.cursor()
    
    # 检查是否存在
    cursor.execute("SELECT name FROM stocks WHERE id = ? AND is_deleted = 0", (stock_id,))
    stock = cursor.fetchone()
    if not stock:
        print(f"❌ 找不到ID为 {stock_id} 的股票（或已删除）")
        conn.close()
        return
    
    name = stock[0]
    
    # 软删除
    cursor.execute("""
        UPDATE stocks
        SET is_deleted = 1, deleted_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (stock_id,))
    
    conn.commit()
    conn.close()
    
    print(f"✅ 股票已删除（软删除）！ID: {stock_id}")
    print(f"   名称: {name}")
    print(f"   注：数据仍保存在数据库中，可通过'历史'命令查看")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        show_help()
        sys.exit(0)

    command = sys.argv[1]

    if command == "列表":
        show_total = len(sys.argv) > 2 and any(p in sys.argv[2:] for p in ["显示总值", "总值", "show-total"])
        show_id = len(sys.argv) > 2 and any(p in sys.argv[2:] for p in ["显示ID", "显示id", "id", "ID"])
        show_cost = len(sys.argv) > 2 and any(p in sys.argv[2:] for p in ["显示成本价", "成本价", "show-cost"])
        show_quantity = len(sys.argv) > 2 and any(p in sys.argv[2:] for p in ["显示数量", "数量", "show-quantity"])
        show_mode = len(sys.argv) > 2 and any(p in sys.argv[2:] for p in ["显示模式", "模式", "show-mode"])
        show_reason = len(sys.argv) > 2 and any(p in sys.argv[2:] for p in ["显示理由", "显示持有理由", "show-reason"])
        show_code = len(sys.argv) > 2 and any(p in sys.argv[2:] for p in ["显示代码", "代码", "show-code"])
        list_stocks(show_deleted=False, show_total=show_total, show_id=show_id, show_cost=show_cost, show_quantity=show_quantity, show_mode=show_mode, show_reason=show_reason, show_code=show_code)
    
    elif command == "历史":
        list_stocks(show_deleted=True)
    
    elif command == "添加":
        if len(sys.argv) < 9:
            print("❌ 参数错误")
            print("用法: /risk 添加 <名称> <代码> <模式> <持有数量> <成本价> <止损价> <现价> [总资金] [持有理由]")
            print("示例: /risk 添加 上证50 000016 集中 200 2457 2457 2960")
            print("      /risk 添加 股票B 000010 集中 5000 1.00 0.80 1.00 100000 \"AI趋势\"")
            sys.exit(1)
        try:
            name = sys.argv[2]
            code = sys.argv[3] if sys.argv[3] != "-" else None
            mode = sys.argv[4]
            quantity = float(sys.argv[5])
            cost_price = float(sys.argv[6])
            stop_loss = float(sys.argv[7])
            current_price = float(sys.argv[8])
            total_capital = float(sys.argv[9]) if len(sys.argv) > 9 and sys.argv[9] and sys.argv[9][0].isdigit() else DEFAULT_TOTAL_CAPITAL
            hold_reason = sys.argv[10] if len(sys.argv) > 10 else (sys.argv[9] if len(sys.argv) > 9 and not sys.argv[9][0].isdigit() else None)
            
            # 兼容旧模式名称
            if mode in ["集中"]:
                mode = "集中"
            elif mode in ["分散"]:
                mode = "2%分散"
            
            if mode not in ["集中", "2%分散"]:
                print("❌ 模式必须是 '集中'/'集中' 或 '分散'/'2%分散'")
                sys.exit(1)
            
            add_stock(name, code, mode, quantity, cost_price, stop_loss, current_price, total_capital, hold_reason)
        except ValueError as e:
            print(f"❌ 参数错误: {e}")
            print("仓位/总值、成本价、止损价、现价、总资金必须是数字")
            sys.exit(1)
    
    elif command == "更新":
        if len(sys.argv) < 4:
            print("❌ 参数错误")
            print("用法: /risk 更新 <id> <现价> [持有理由]")
            print("示例: /risk 更新 1 2980")
            print("      /risk 更新 1 2980 \"继续看好AI趋势\"")
            sys.exit(1)
        try:
            stock_id = int(sys.argv[2])
            current_price = float(sys.argv[3])
            hold_reason = sys.argv[4] if len(sys.argv) > 4 else None
            update_stock(stock_id, current_price, hold_reason)
        except ValueError as e:
            print(f"❌ 参数错误: {e}")
            print("ID和现价必须是数字")
            sys.exit(1)
    
    elif command == "删除":
        if len(sys.argv) != 3:
            print("❌ 参数错误")
            print("用法: /risk 删除 <id>")
            print("示例: /risk 删除 1")
            sys.exit(1)
        try:
            stock_id = int(sys.argv[2])
            delete_stock(stock_id)
        except ValueError as e:
            print(f"❌ 参数错误: {e}")
            print("ID必须是数字")
            sys.exit(1)
    
    elif command in ["集中", "集中"]:
        if len(sys.argv) < 4:
            print("❌ 参数错误")
            print("用法: /risk 集中 <现价> <止损价> [目标风险]")
            print("示例: /risk 集中 2960 2457")
            print("      /risk 集中 2960 2457 1")
            sys.exit(1)
        try:
            current_price = float(sys.argv[2])
            stop_loss = float(sys.argv[3])
            target_risk = float(sys.argv[4]) if len(sys.argv) > 4 else 2
            calculate_concentrated(current_price, stop_loss, target_risk)
        except ValueError as e:
            print(f"❌ 参数错误: {e}")
            print("现价、止损价、目标风险必须是数字")
            sys.exit(1)
    
    elif command in ["分散", "2%分散"]:
        if len(sys.argv) < 4:
            print("❌ 参数错误")
            print("用法: /risk 分散 <现价> <止损价> [目标风险]")
            print("示例: /risk 分散 2960 2457")
            print("      /risk 分散 2960 2457 1")
            sys.exit(1)
        try:
            current_price = float(sys.argv[2])
            stop_loss = float(sys.argv[3])
            target_risk = float(sys.argv[4]) if len(sys.argv) > 4 else 2
            calculate_diversified(current_price, stop_loss, target_risk)
        except ValueError as e:
            print(f"❌ 参数错误: {e}")
            print("现价、止损价、目标风险必须是数字")
            sys.exit(1)
    
    else:
        print(f"❌ 未知命令: {command}")
        print()
        show_help()
        sys.exit(1)
