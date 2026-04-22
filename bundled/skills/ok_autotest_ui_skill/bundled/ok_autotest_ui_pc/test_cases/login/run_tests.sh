#!/bin/bash
# 登录模块测试执行脚本

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  OK AE站 - 登录模块自动化测试${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 切换到 test_cases/login 目录
cd "$(dirname "$0")"

# 检查 Python 环境
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 未安装${NC}"
    exit 1
fi

# 检查 pytest
if ! python3 -c "import pytest" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  pytest 未安装，正在安装...${NC}"
    pip3 install pytest pytest-playwright allure-pytest
fi

echo -e "${GREEN}✅ 环境检查通过${NC}"
echo ""

# 显示菜单
echo "请选择执行方式："
echo "1. 运行所有登录测试"
echo "2. 只运行需要退登的用例 (TC012, TC013, TC027)"
echo "3. 只运行 P0 优先级用例"
echo "4. 运行欢迎页测试"
echo "5. 运行邮箱密码登录测试"
echo "6. 运行手机号密码登录测试"
echo "7. 生成 Allure 报告"
echo "8. 调试模式（显示详细输出）"
echo ""

read -p "请输入选项 (1-8): " choice

case $choice in
    1)
        echo -e "${BLUE}开始运行所有登录测试...${NC}"
        pytest -v --tb=short
        ;;
    2)
        echo -e "${BLUE}开始运行需要退登的用例...${NC}"
        pytest -v -m need_logout --tb=short
        ;;
    3)
        echo -e "${BLUE}开始运行 P0 优先级用例...${NC}"
        pytest -v -m p0 --tb=short
        ;;
    4)
        echo -e "${BLUE}开始运行欢迎页测试...${NC}"
        pytest test_login_welcome_page.py -v --tb=short
        ;;
    5)
        echo -e "${BLUE}开始运行邮箱密码登录测试...${NC}"
        pytest test_login_email_password.py -v --tb=short
        ;;
    6)
        echo -e "${BLUE}开始运行手机号密码登录测试...${NC}"
        pytest test_login_phone_password.py -v --tb=short
        ;;
    7)
        echo -e "${BLUE}生成 Allure 报告...${NC}"
        if ! command -v allure &> /dev/null; then
            echo -e "${RED}❌ Allure 未安装，请先安装: brew install allure${NC}"
            exit 1
        fi
        
        echo "运行测试并生成数据..."
        pytest --alluredir=./allure-results --clean-alluredir
        
        echo "生成并打开报告..."
        allure serve ./allure-results
        ;;
    8)
        echo -e "${BLUE}调试模式运行...${NC}"
        pytest -v -s --tb=long
        ;;
    *)
        echo -e "${RED}无效选项${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  测试执行完成${NC}"
echo -e "${GREEN}========================================${NC}"
