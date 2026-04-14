#!/bin/bash
# Messages页面完整测试执行脚本
# 支持运行所有测试用例或按类别筛选

# 设置颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 切换到项目目录
cd /Users/a58/ok_autotest_ui_pc

# 创建必要的目录
mkdir -p screenshots
mkdir -p reports/allure-results

echo ""
echo -e "${BLUE}=========================================="
echo "Messages页面测试套件执行脚本"
echo -e "==========================================${NC}"
echo ""
echo -e "${YELLOW}测试用例概览 (共25个):${NC}"
echo "  TC001-TC008: 基础探索测试 (8个)"
echo "  TC009-TC014: 功能按钮测试 (6个)"
echo "  TC018-TC022: 异常和功能测试 (5个)"
echo "  TC023-TC025: 会话列表基础交互 (3个)"
echo "  TC026-TC028: 会话列表深度实测 (3个，含时间顺序/置顶/免打扰icon)"
echo ""
echo -e "${YELLOW}请选择执行模式:${NC}"
echo "  1) 运行所有测试 (TC001-TC028)"
echo "  2) 仅运行探索测试 (TC001-TC008)"
echo "  3) 仅运行功能测试 (TC009-TC014)"
echo "  4) 仅运行异常测试 (TC018-TC021)"
echo "  5) 按marker运行 (自定义)"
echo "  6) 运行单个测试用例"
echo ""
read -p "请输入选项 [1-6]: " choice

case $choice in
    1)
        echo ""
        echo -e "${GREEN}运行所有Messages测试用例...${NC}"
        python3 -m pytest test_cases/test_messages_complete.py \
            -v \
            --tb=short \
            --alluredir=reports/allure-results \
            --junitxml=reports/junit_messages.xml
        ;;
    2)
        echo ""
        echo -e "${GREEN}运行探索测试 (TC001-TC008)...${NC}"
        python3 -m pytest test_cases/test_messages_complete.py \
            -v \
            --tb=short \
            -m "explore" \
            --alluredir=reports/allure-results \
            --junitxml=reports/junit_explore.xml
        ;;
    3)
        echo ""
        echo -e "${GREEN}运行功能测试 (TC009-TC014)...${NC}"
        python3 -m pytest test_cases/test_messages_complete.py \
            -v \
            --tb=short \
            -m "conversation" \
            --alluredir=reports/allure-results \
            --junitxml=reports/junit_function.xml
        ;;
    4)
        echo ""
        echo -e "${GREEN}运行异常测试 (TC018-TC021)...${NC}"
        python3 -m pytest test_cases/test_messages_complete.py \
            -v \
            --tb=short \
            -m "ae" \
            --alluredir=reports/allure-results \
            --junitxml=reports/junit_exception.xml
        ;;
    5)
        echo ""
        echo -e "${YELLOW}可用的markers:${NC}"
        echo "  - explore: 探索测试"
        echo "  - conversation: 会话功能测试"
        echo "  - ae: 异常和边界测试"
        echo "  - copy: 复制功能测试"
        echo ""
        read -p "请输入marker名称: " marker
        echo ""
        echo -e "${GREEN}运行marker=${marker}的测试...${NC}"
        python3 -m pytest test_cases/test_messages_complete.py \
            -v \
            --tb=short \
            -m "$marker" \
            --alluredir=reports/allure-results \
            --junitxml=reports/junit_custom.xml
        ;;
    6)
        echo ""
        echo -e "${YELLOW}可用的测试用例:${NC}"
        python3 -m pytest test_cases/test_messages_complete.py --collect-only -q | grep "test_"
        echo ""
        read -p "请输入测试用例名称 (例如: test_send_message): " testname
        echo ""
        echo -e "${GREEN}运行测试: ${testname}...${NC}"
        python3 -m pytest test_cases/test_messages_complete.py::${testname} \
            -v \
            --tb=short \
            -s \
            --alluredir=reports/allure-results \
            --junitxml=reports/junit_single.xml
        ;;
    *)
        echo ""
        echo -e "${RED}无效选项，退出${NC}"
        exit 1
        ;;
esac

# 检查测试结果
echo ""
if [ $? -eq 0 ]; then
    echo -e "${GREEN}=========================================="
    echo "✅ 测试执行完成！"
    echo -e "==========================================${NC}"
else
    echo -e "${YELLOW}=========================================="
    echo "⚠️ 部分测试失败或跳过"
    echo -e "==========================================${NC}"
fi

echo ""
echo -e "${BLUE}测试报告位置:${NC}"
echo "  - JUnit报告: reports/junit_*.xml"
echo "  - Allure结果: reports/allure-results/"
echo "  - 截图目录: screenshots/"
echo ""
echo -e "${BLUE}生成Allure报告:${NC}"
echo "  allure serve reports/allure-results"
echo ""
