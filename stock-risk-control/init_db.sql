-- 股票风险控制策略 - 数据库初始化脚本
-- SQLite数据库（v3，新增持有理由字段）

CREATE TABLE IF NOT EXISTS stocks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    code TEXT,
    mode TEXT NOT NULL CHECK(mode IN ('2%集中', '2%分散')),
    quantity REAL NOT NULL,  -- 持有数量（股/份）
    position REAL NOT NULL,
    total_value REAL NOT NULL,
    cost_price REAL,
    stop_loss REAL NOT NULL,
    current_price REAL NOT NULL,
    hold_reason TEXT,
    pnl REAL,
    pnl_percent REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deleted INTEGER DEFAULT 0 CHECK(is_deleted IN (0, 1)),
    deleted_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_stocks_is_deleted ON stocks(is_deleted);
CREATE INDEX IF NOT EXISTS idx_stocks_created_at ON stocks(created_at);
