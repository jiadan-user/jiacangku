#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PostgreSQL 数据库操作工具 - 支付流水状态更新

用途: 更新 payment_flow 表的状态
"""
import sys
import argparse
import psycopg2
from datetime import datetime

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# PostgreSQL 配置
PG_CONFIG = {
    'host': 'pgsql-test.pdb.58dns.org',
    'port': 29000,
    'database': 'pdb58_easypost',
    'user': 'epost_test',
    'password': 'GUGXzw49K6Ndp7'
}


def clear_withdrawal_restriction_by_user(app_user_id='796133836057336352'):
    """
    根据 app_user_id 清除提现限制
    
    Args:
        app_user_id (str): 用户ID（默认: 796133836057336352）
        
    Returns:
        bool: 是否更新成功
    """
    print("=" * 80)
    print("PostgreSQL 清除提现限制工具")
    print("=" * 80)
    print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"用户ID: {app_user_id}")
    print("=" * 80)
    
    conn = None
    try:
        # 连接数据库
        print(f"\n连接数据库: {PG_CONFIG['host']}:{PG_CONFIG['port']}/{PG_CONFIG['database']}")
        conn = psycopg2.connect(
            host=PG_CONFIG['host'],
            port=PG_CONFIG['port'],
            database=PG_CONFIG['database'],
            user=PG_CONFIG['user'],
            password=PG_CONFIG['password']
        )
        print("✓ 数据库连接成功")
        
        cursor = conn.cursor()
        
        # 执行复杂SQL更新
        print(f"\n执行清除提现限制...")
        update_sql = """
            UPDATE payment_flow
            SET status = 1
            WHERE payment_no = (
                SELECT payment_no
                FROM payment_flow
                WHERE payer_id = (
                    SELECT payment_account_id
                    FROM user_payment_binding
                    WHERE app_user_id = %s
                    ORDER BY id DESC
                    LIMIT 1
                )
                AND payee_id = (
                    SELECT payment_account_id
                    FROM user_payment_binding
                    WHERE app_user_id = %s
                    ORDER BY id DESC
                    LIMIT 1
                )
                ORDER BY id DESC
                LIMIT 1
            )
            RETURNING payment_no, status
        """
        
        print(f"SQL: {update_sql}")
        print(f"参数: app_user_id={app_user_id}")
        
        cursor.execute(update_sql, (app_user_id, app_user_id))
        result = cursor.fetchone()
        rows_affected = cursor.rowcount
        
        # 提交事务
        conn.commit()
        
        if rows_affected > 0 and result:
            print(f"✓ 清除成功！影响行数: {rows_affected}")
            print(f"  payment_no: {result[0]}")
            print(f"  更新后 status: {result[1]}")
        else:
            print("⚠️  未找到匹配的记录，可能没有需要清除的提现限制")
        
        print("\n" + "=" * 80)
        print("清除完成")
        print("=" * 80)
        
        cursor.close()
        return True
        
    except psycopg2.Error as e:
        if conn:
            conn.rollback()
        print(f"\n✗ 数据库错误: {e}")
        print(f"错误详情: {e.pgerror if hasattr(e, 'pgerror') else str(e)}")
        return False
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"\n✗ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if conn:
            conn.close()
            print("\n数据库连接已关闭")


def update_payment_flow_status(payment_no, status=1):
    """
    更新 payment_flow 表的状态
    
    Args:
        payment_no (str): 支付单号（Reference_ID）
        status (int): 目标状态（默认为 1）
        
    Returns:
        bool: 是否更新成功
    """
    print("=" * 80)
    print("PostgreSQL 支付流水状态更新工具")
    print("=" * 80)
    print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    conn = None
    try:
        # 连接数据库
        print(f"\n连接数据库: {PG_CONFIG['host']}:{PG_CONFIG['port']}/{PG_CONFIG['database']}")
        conn = psycopg2.connect(
            host=PG_CONFIG['host'],
            port=PG_CONFIG['port'],
            database=PG_CONFIG['database'],
            user=PG_CONFIG['user'],
            password=PG_CONFIG['password']
        )
        print("✓ 数据库连接成功")
        
        cursor = conn.cursor()
        
        # 先查询当前记录
        print(f"\n查询当前记录...")
        select_sql = "SELECT payment_no, status FROM payment_flow WHERE payment_no = %s"
        cursor.execute(select_sql, (payment_no,))
        result = cursor.fetchone()
        
        if result is None:
            print(f"✗ 未找到 payment_no = '{payment_no}' 的记录")
            return False
        
        current_status = result[1]
        print(f"✓ 找到记录")
        print(f"  payment_no: {result[0]}")
        print(f"  当前 status: {current_status}")
        
        if current_status == status:
            print(f"\n⚠️  状态已经是 {status}，无需更新")
            return True
        
        # 执行更新
        print(f"\n执行更新...")
        update_sql = "UPDATE payment_flow SET status = %s WHERE payment_no = %s"
        print(f"SQL: {update_sql}")
        print(f"参数: status={status}, payment_no={payment_no}")
        
        cursor.execute(update_sql, (status, payment_no))
        rows_affected = cursor.rowcount
        
        # 提交事务
        conn.commit()
        
        print(f"✓ 更新成功！影响行数: {rows_affected}")
        
        # 再次查询确认
        print(f"\n确认更新结果...")
        cursor.execute(select_sql, (payment_no,))
        result = cursor.fetchone()
        
        if result:
            new_status = result[1]
            print(f"✓ 确认成功")
            print(f"  payment_no: {result[0]}")
            print(f"  更新后 status: {new_status}")
            
            print("\n" + "=" * 80)
            print("更新完成")
            print("=" * 80)
            print(f"payment_no: {payment_no}")
            print(f"状态变更: {current_status} → {new_status}")
            print("=" * 80)
        
        cursor.close()
        return True
        
    except psycopg2.Error as e:
        if conn:
            conn.rollback()
        print(f"\n✗ 数据库错误: {e}")
        print(f"错误详情: {e.pgerror if hasattr(e, 'pgerror') else str(e)}")
        return False
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"\n✗ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if conn:
            conn.close()
            print("\n数据库连接已关闭")


def query_payment_flow(payment_no):
    """
    查询 payment_flow 记录（不更新）
    
    Args:
        payment_no (str): 支付单号
        
    Returns:
        dict: 记录信息
    """
    print("=" * 80)
    print("PostgreSQL 支付流水查询工具")
    print("=" * 80)
    
    conn = None
    try:
        print(f"\n连接数据库: {PG_CONFIG['host']}:{PG_CONFIG['port']}/{PG_CONFIG['database']}")
        conn = psycopg2.connect(
            host=PG_CONFIG['host'],
            port=PG_CONFIG['port'],
            database=PG_CONFIG['database'],
            user=PG_CONFIG['user'],
            password=PG_CONFIG['password']
        )
        print("✓ 数据库连接成功")
        
        cursor = conn.cursor()
        
        print(f"\n查询记录...")
        sql = """
            SELECT payment_no, status, amount, currency, 
                   create_time, update_time 
            FROM payment_flow 
            WHERE payment_no = %s
        """
        cursor.execute(sql, (payment_no,))
        result = cursor.fetchone()
        
        if result is None:
            print(f"✗ 未找到 payment_no = '{payment_no}' 的记录")
            return None
        
        print(f"✓ 查询成功")
        print("\n" + "=" * 80)
        print("记录详情")
        print("=" * 80)
        print(f"payment_no: {result[0]}")
        print(f"status: {result[1]}")
        print(f"amount: {result[2]}")
        print(f"currency: {result[3]}")
        print(f"create_time: {result[4]}")
        print(f"update_time: {result[5]}")
        print("=" * 80)
        
        cursor.close()
        return {
            'payment_no': result[0],
            'status': result[1],
            'amount': result[2],
            'currency': result[3],
            'create_time': result[4],
            'update_time': result[5]
        }
        
    except Exception as e:
        print(f"\n✗ 错误: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        if conn:
            conn.close()


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='PostgreSQL 支付流水状态更新工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 更新支付单号状态为 1（默认）
  python %(prog)s --payment-no PMT20260304172445
  
  # 更新支付单号状态为指定值
  python %(prog)s --payment-no PMT20260304172445 --status 2
  
  # 仅查询，不更新
  python %(prog)s --payment-no PMT20260304172445 --query-only
  
  # 清除用户提现限制
  python %(prog)s --clear-withdrawal-restriction --app-user-id 796133836057336352
  
  # 使用不同的数据库
  python %(prog)s --payment-no PMT20260304172445 \
      --host your-db.example.com \
      --port 5432 \
      --database your_db \
      --user your_user \
      --password your_pass
        """
    )
    
    parser.add_argument(
        '--payment-no',
        type=str,
        help='支付单号（Reference_ID）'
    )
    
    parser.add_argument(
        '--status',
        type=int,
        default=1,
        help='目标状态值（默认: 1）'
    )
    
    parser.add_argument(
        '--query-only',
        action='store_true',
        help='仅查询，不更新'
    )
    
    parser.add_argument(
        '--clear-withdrawal-restriction',
        action='store_true',
        help='清除用户的提现限制'
    )
    
    parser.add_argument(
        '--app-user-id',
        type=str,
        default='796133836057336352',
        help='用户ID（用于清除提现限制，默认: 796133836057336352）'
    )
    
    parser.add_argument(
        '--host',
        type=str,
        default=PG_CONFIG['host'],
        help=f'数据库主机地址（默认: {PG_CONFIG["host"]}）'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=PG_CONFIG['port'],
        help=f'数据库端口（默认: {PG_CONFIG["port"]}）'
    )
    
    parser.add_argument(
        '--database',
        type=str,
        default=PG_CONFIG['database'],
        help=f'数据库名（默认: {PG_CONFIG["database"]}）'
    )
    
    parser.add_argument(
        '--user',
        type=str,
        default=PG_CONFIG['user'],
        help=f'数据库用户（默认: {PG_CONFIG["user"]}）'
    )
    
    parser.add_argument(
        '--password',
        type=str,
        default=PG_CONFIG['password'],
        help='数据库密码'
    )
    
    return parser.parse_args()


def main():
    """主函数"""
    args = parse_arguments()
    
    # 更新全局配置
    global PG_CONFIG
    PG_CONFIG = {
        'host': args.host,
        'port': args.port,
        'database': args.database,
        'user': args.user,
        'password': args.password
    }
    
    if args.clear_withdrawal_restriction:
        # 清除提现限制模式
        success = clear_withdrawal_restriction_by_user(args.app_user_id)
        return 0 if success else 1
    elif args.query_only:
        # 仅查询模式
        if not args.payment_no:
            print("错误: --query-only 需要指定 --payment-no")
            return 1
        result = query_payment_flow(args.payment_no)
        return 0 if result else 1
    else:
        # 更新模式
        if not args.payment_no:
            print("错误: 需要指定 --payment-no 或使用 --clear-withdrawal-restriction")
            return 1
        success = update_payment_flow_status(args.payment_no, args.status)
        return 0 if success else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
