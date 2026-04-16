# utils/db_client.py
"""
PostgreSQL 数据库客户端工具
封装 psycopg2 连接，提供执行 SQL 的静默工具方法
"""
import psycopg2
from utils.logger import setup_logger

logger = setup_logger()

# ============================================================
# 数据库连接配置
# ============================================================
_PG_CONFIG = {
    "host": "pgsql-test.pdb.58dns.org",
    "port": 29000,
    "dbname": "pdb58_easypost",
    "user": "epost_test",
    "password": "GUGXzw49K6Ndp7",
    "connect_timeout": 10,
    "options": "-c client_encoding=UTF8",
}


def _get_connection():
    """建立并返回 PostgreSQL 连接（调用方负责关闭）"""
    return psycopg2.connect(**_PG_CONFIG)


def execute_update(sql: str, params: tuple = None) -> int:
    """
    执行 INSERT / UPDATE / DELETE 语句

    Args:
        sql: SQL 语句（使用 %s 占位符）
        params: 参数元组

    Returns:
        int: 受影响行数

    Raises:
        Exception: 数据库操作失败时抛出
    """
    conn = None
    try:
        conn = _get_connection()
        with conn.cursor() as cur:
            cur.execute(sql, params)
            rowcount = cur.rowcount
        conn.commit()
        return rowcount
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"DB execute_update 失败: {e} | SQL: {sql} | params: {params}")
        raise
    finally:
        if conn:
            conn.close()


def execute_query(sql: str, params: tuple = None) -> list:
    """
    执行 SELECT 语句

    Args:
        sql: SQL 语句（使用 %s 占位符）
        params: 参数元组

    Returns:
        list[tuple]: 查询结果行列表
    """
    conn = None
    try:
        conn = _get_connection()
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()
    except Exception as e:
        logger.error(f"DB execute_query 失败: {e} | SQL: {sql} | params: {params}")
        raise
    finally:
        if conn:
            conn.close()
