"""
独立脚本：设置Airwallex账户为失败状态（SUSPENDED）
用于快速调试钱包绑定失败场景

使用方法:
    python test_cases/wallet/standalone_suspend_account.py

参数说明:
    --user-id: 用户ID (默认: 796145073984870048)
    --force: 是否强制设置 (默认: False)
    
示例:
    python test_cases/wallet/standalone_suspend_account.py --user-id 796145073984870048
    python test_cases/wallet/standalone_suspend_account.py --user-id 796145073984870048 --force
"""
import sys
import os
import argparse
from datetime import datetime

# Add parent directory to path to import helper
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Lazy import to provide better error messages
AirwallexHelper = None

# Check dependencies early and provide helpful error message
try:
    import redis
    import psycopg2
    import requests
except ModuleNotFoundError as e:
    missing_module = str(e).split("'")[1] if "'" in str(e) else "unknown"
    sys.stderr.write(f"Error: Missing required dependency '{missing_module}'\n")
    sys.stderr.write("\n")
    sys.stderr.write("This script requires the following parameters:\n")
    sys.stderr.write("  --user-id <user_id>           User ID to get payment_account_id from database\n")
    sys.stderr.write("  --payment-account-id <id>     (Optional) Direct payment_account_id\n")
    sys.stderr.write("\n")
    sys.stderr.write("Required dependencies:\n")
    sys.stderr.write("  pip install redis psycopg2-binary requests\n")
    sys.stderr.write("\n")
    sys.stderr.write("Or install all project dependencies:\n")
    sys.stderr.write("  pip install -r requirements.txt\n")
    sys.exit(1)


class SimpleLogger:
    """简单的日志类"""
    
    @staticmethod
    def log(level, message, use_stderr=False):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        output_str = f"[{timestamp}] [{level}] {message}"
        try:
            if use_stderr:
                sys.stderr.write(output_str + "\n")
            else:
                print(output_str)
        except UnicodeEncodeError:
            # Handle encoding issues on Windows
            safe_str = output_str.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore')
            if use_stderr:
                sys.stderr.write(safe_str + "\n")
            else:
                print(safe_str)
    
    @staticmethod
    def info(message):
        SimpleLogger.log("INFO", message)
    
    @staticmethod
    def success(message):
        SimpleLogger.log("SUCCESS", message)
    
    @staticmethod
    def warning(message):
        SimpleLogger.log("WARNING", message)
    
    @staticmethod
    def error(message):
        SimpleLogger.log("ERROR", message, use_stderr=True)


logger = SimpleLogger()


def setup_logger():
    """配置日志输出"""
    pass


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="设置Airwallex账户为失败状态")
    parser.add_argument(
        "--user-id", 
        type=str, 
        default="796145073984870048",
        help="用户ID (默认: 796145073984870048)"
    )
    parser.add_argument(
        "--force", 
        action="store_true",
        help="是否强制设置状态"
    )
    
    args = parser.parse_args()
    
    setup_logger()
    
    # Import helper after argument parsing to provide better error messages
    global AirwallexHelper
    try:
        from helper_airwallex import AirwallexHelper
    except ModuleNotFoundError as e:
        logger.error("=" * 80)
        logger.error("缺少必需的依赖模块")
        logger.error("=" * 80)
        logger.error(f"错误: {str(e)}")
        logger.error("")
        logger.error("请安装依赖:")
        logger.error("  pip install redis psycopg2-binary requests")
        logger.error("")
        logger.error("或者使用项目根目录的 requirements.txt:")
        logger.error("  pip install -r requirements.txt")
        logger.error("=" * 80)
        sys.exit(1)
    except ImportError as e:
        logger.error("=" * 80)
        logger.error(f"导入 helper_airwallex 模块失败: {str(e)}")
        logger.error("=" * 80)
        sys.exit(1)
    
    logger.info("=" * 80)
    logger.info("开始设置Airwallex账户为失败状态 (SUSPENDED)")
    logger.info("=" * 80)
    logger.info(f"用户ID: {args.user_id}")
    logger.info(f"强制模式: {args.force}")
    logger.info("")
    
    try:
        with AirwallexHelper() as helper:
            # Step 1: 从Redis获取token
            logger.info("步骤 1/3: 从Redis获取token...")
            token = helper.get_token_from_redis()
            logger.success("Token获取成功")
            logger.info("")
            
            # Step 2: 从数据库查询payment_account_id
            logger.info("步骤 2/3: 从数据库查询payment_account_id...")
            payment_account_id = helper.get_payment_account_id(args.user_id)
            
            if not payment_account_id:
                logger.error(f"未找到用户 {args.user_id} 的payment_account_id")
                logger.error("请检查用户ID是否正确，或该用户是否已绑定银行账户")
                sys.exit(1)
            
            logger.success(f"Payment Account ID: {payment_account_id}")
            logger.info("")
            
            # Step 3: 调用API设置为SUSPENDED状态
            logger.info("步骤 3/3: 调用Airwallex API设置为SUSPENDED状态...")
            result = helper.suspend_account(payment_account_id, token, force=args.force)
            
            logger.info("")
            logger.info("=" * 80)
            logger.info("API响应结果")
            logger.info("=" * 80)
            logger.info(f"Status Code: {result['status_code']}")
            logger.info(f"Request URL: {result['request_url']}")
            logger.info(f"Request Payload: {result['request_payload']}")
            logger.info(f"Response: {result['response']}")
            logger.info("")
            
            if result["success"]:
                logger.success("=" * 80)
                logger.success("账户状态已成功设置为 SUSPENDED (失败状态)")
                logger.success("=" * 80)
                logger.success("")
                logger.success("现在可以在前端进行以下测试:")
                logger.success("   1. 测试绑定银行账户失败场景")
                logger.success("   2. 验证失败提示信息是否正确显示")
                logger.success("   3. 检查错误处理逻辑")
                logger.success("")
                logger.success(f"测试用户ID: {args.user_id}")
                logger.success(f"Payment Account ID: {payment_account_id}")
                logger.success("")
            else:
                logger.warning("=" * 80)
                logger.warning(f"请求完成，但状态码为: {result['status_code']}")
                logger.warning("=" * 80)
                logger.warning("请检查:")
                logger.warning("  1. Token是否有效")
                logger.warning("  2. Payment Account ID是否正确")
                logger.warning("  3. API权限是否充足")
                logger.warning("")
                
    except Exception as e:
        logger.error("=" * 80)
        logger.error(f"执行失败: {str(e)}")
        logger.error("=" * 80)
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()
