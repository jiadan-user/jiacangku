# utils/logger.py
import logging
import os
import stat
from pathlib import Path
from datetime import datetime


def setup_logger(name="AutoTest", level=logging.INFO):
    """
    配置日志记录器（静默执行,带权限容错）
    
    Args:
        name: 日志记录器名称
        level: 日志级别
    
    Returns:
        logger: 配置好的日志记录器
    """
    logger = logging.getLogger(name)
    
    # 避免重复添加 handler
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    
    # 尝试创建日志目录并设置权限
    log_dir = Path("reports/logs")
    try:
        log_dir.mkdir(parents=True, exist_ok=True)
        # 设置目录权限为 775 (rwxrwxr-x)
        os.chmod(log_dir, stat.S_IRWXU | stat.S_IRWXG | stat.S_IROTH | stat.S_IXOTH)
    except (PermissionError, OSError) as e:
        # 如果无法创建目录,只使用控制台输出
        print(f"⚠️ 无法创建日志目录: {e}, 将只输出到控制台")
        log_dir = None
    
    # 日志文件名（按日期）
    if log_dir:
        log_file = log_dir / f"test_{datetime.now().strftime('%Y%m%d')}.log"
        
        # 如果日志文件已存在,检查并修复权限
        if log_file.exists():
            try:
                # 尝试修改文件权限为 664 (rw-rw-r--)
                os.chmod(log_file, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH)
            except (PermissionError, OSError):
                # 如果无法修改权限,尝试删除文件重新创建
                try:
                    log_file.unlink()
                except (PermissionError, OSError):
                    pass
        
        # 尝试创建文件处理器
        try:
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter(
                '%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
            
            # 创建文件后立即设置权限
            try:
                os.chmod(log_file, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH)
            except (PermissionError, OSError):
                pass
                
        except (PermissionError, OSError) as e:
            print(f"⚠️ 无法创建日志文件: {e}, 将只输出到控制台")
    
    # 控制台处理器（只在测试层输出）
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    return logger

