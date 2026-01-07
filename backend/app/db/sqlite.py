import sqlite3
from sqlite3 import Connection, Cursor
import json
from datetime import datetime

# SQLite 数据库连接
conn: Connection = None

# 初始化数据库
async def init_sqlite_db():
    """初始化SQLite数据库"""
    global conn
    # 创建连接
    conn = sqlite3.connect('ai_reviewer.db', check_same_thread=False)
    
    # 启用外键约束
    conn.execute("PRAGMA foreign_keys = ON")
    
    # 开启事务模式
    conn.isolation_level = None
    
    # 创建游标
    cursor = conn.cursor()
    
    # 创建业务场景表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS business_scenes (
        _id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    ''')
    
    # 创建规则表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS rules (
        _id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        scene_id TEXT NOT NULL,
        description TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (scene_id) REFERENCES business_scenes(_id)
    )
    ''')
    
    # 创建审核项表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS audit_items (
        _id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        rule_id TEXT NOT NULL,
        type TEXT NOT NULL,
        criteria TEXT NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (rule_id) REFERENCES rules(_id)
    )
    ''')
    
    # 创建审核任务表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS audit_tasks (
        _id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        scene_id TEXT NOT NULL,
        use_knowledge_base BOOLEAN NOT NULL DEFAULT 0,
        status TEXT NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        completed_at TEXT
    )
    ''')
    
    # 创建审核结果表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS audit_results (
        _id TEXT PRIMARY KEY,
        task_id TEXT NOT NULL,
        rule_id TEXT NOT NULL,
        audit_item_id TEXT NOT NULL,
        content TEXT NOT NULL,
        result TEXT NOT NULL,
        reason TEXT,
        ai_generated BOOLEAN NOT NULL DEFAULT 0,
        edited_by TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (task_id) REFERENCES audit_tasks(_id),
        FOREIGN KEY (rule_id) REFERENCES rules(_id),
        FOREIGN KEY (audit_item_id) REFERENCES audit_items(_id)
    )
    ''')
    
    # 创建版式模板表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS templates (
        _id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        variables TEXT NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    ''')
    
    # 提交事务
    conn.commit()
    
    # 关闭游标
    cursor.close()
    
    print("SQLite数据库初始化完成")

# 关闭数据库连接
async def close_sqlite_db():
    """关闭SQLite数据库连接"""
    global conn
    if conn:
        conn.close()
        conn = None
        print("SQLite数据库连接已关闭")

# 获取数据库连接
async def get_db():
    """获取数据库连接"""
    global conn
    if not conn:
        await init_sqlite_db()
    return conn

# 通用查询函数
async def query(query: str, params: tuple = ()):
    """执行查询并返回所有结果"""
    conn = await get_db()
    cursor = conn.cursor()
    cursor.execute(query, params)
    results = cursor.fetchall()
    cursor.close()
    return results

# 通用执行函数
async def execute(query: str, params: tuple = ()):
    """执行SQL语句"""
    conn = await get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("BEGIN TRANSACTION")
        cursor.execute(query, params)
        cursor.execute("COMMIT")
        affected_rows = cursor.rowcount
        cursor.close()
        return affected_rows
    except Exception as e:
        cursor.execute("ROLLBACK")
        cursor.close()
        raise e

# 通用插入函数
async def insert(table: str, data: dict):
    """插入数据"""
    conn = await get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("BEGIN TRANSACTION")
        
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data.values()])
        values = tuple(data.values())
        
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        cursor.execute(query, values)
        
        cursor.execute("COMMIT")
        cursor.close()
        
        return cursor.lastrowid
    except Exception as e:
        cursor.execute("ROLLBACK")
        cursor.close()
        raise e

# 通用更新函数
async def update(table: str, data: dict, where: str, where_params: tuple = ()):
    """更新数据"""
    conn = await get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("BEGIN TRANSACTION")
        
        set_clause = ', '.join([f"{col} = ?" for col in data.keys()])
        values = tuple(data.values()) + where_params
        
        query = f"UPDATE {table} SET {set_clause} WHERE {where}"
        cursor.execute(query, values)
        
        cursor.execute("COMMIT")
        affected_rows = cursor.rowcount
        cursor.close()
        
        return affected_rows
    except Exception as e:
        cursor.execute("ROLLBACK")
        cursor.close()
        raise e

# 通用删除函数
async def delete(table: str, where: str, where_params: tuple = ()):
    """删除数据"""
    conn = await get_db()
    cursor = conn.cursor()
    
    try:
        # 启用外键约束
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # 开始事务
        cursor.execute("BEGIN TRANSACTION")
        
        query = f"DELETE FROM {table} WHERE {where}"
        cursor.execute(query, where_params)
        affected_rows = cursor.rowcount
        
        # 提交事务
        cursor.execute("COMMIT")
        cursor.close()
        
        return affected_rows
    except Exception as e:
        # 回滚事务
        cursor.execute("ROLLBACK")
        cursor.close()
        raise e
