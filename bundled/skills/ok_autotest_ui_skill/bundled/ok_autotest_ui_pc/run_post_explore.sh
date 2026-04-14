#!/bin/bash
# Post页面功能探索测试执行脚本

# 设置颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 切换到项目目录
cd "$(dirname "$0")"

# 创建必要的目录
mkdir -p screenshots
mkdir -p reports/allure-results

echo ""
echo -e "${BLUE}=================================="
echo "Post页面功能探索测试"
echo -e "==================================${NC}"
echo ""
echo -e "${YELLOW}测试环境:${NC} OK阿联酋站"
echo -e "${YELLOW}目标页面:${NC} Post页面 (发布页面)"
echo -e "${YELLOW}测试账号:${NC} gaosong01@58.com"
echo ""
echo -e "${YELLOW}请选择测试模式:${NC}"
echo "  1) 运行完整探索测试"
echo "  2) 仅运行页面结构探索"
echo "  3) 仅运行图片上传探索"
echo ""
read -p "请输入选项 [1-3, 默认: 1]: " choice
choice=${choice:-1}

echo ""
echo -e "${BLUE}=================================="
echo "开始执行测试..."
echo -e "==================================${NC}"
echo ""

case $choice in
    1)
        echo -e "${GREEN}运行完整探索测试...${NC}"
        python3 -m pytest test_cases/test_post_explore.py \
            -v \
            -s \
            --tb=short \
            --alluredir=reports/allure-results \
            --junitxml=reports/junit_post_explore.xml
        ;;
    2)
        echo -e "${GREEN}运行页面结构探索...${NC}"
        python3 -m pytest test_cases/test_post_explore.py::test_post_page_explore \
            -v \
            -s \
            --tb=short \
            --alluredir=reports/allure-results \
            --junitxml=reports/junit_post_structure.xml
        ;;
    3)
        echo -e "${GREEN}运行图片上传探索...${NC}"
        python3 -m pytest test_cases/test_post_explore.py::test_post_image_upload_explore \
            -v \
            -s \
            --tb=short \
            --alluredir=reports/allure-results \
            --junitxml=reports/junit_post_upload.xml
        ;;
    *)
        echo -e "${RED}无效选择，运行完整探索测试...${NC}"
        python3 -m pytest test_cases/test_post_explore.py \
            -v \
            -s \
            --tb=short \
            --alluredir=reports/allure-results \
            --junitxml=reports/junit_post_explore.xml
        ;;
esac

# 检查测试结果
echo ""
if [ $? -eq 0 ]; then
    echo -e "${GREEN}=================================="
    echo "✅ 测试执行完成！"
    echo -e "==================================${NC}"
else
    echo -e "${YELLOW}=================================="
    echo "⚠️ 部分测试失败或跳过"
    echo -e "==================================${NC}"
fi

echo ""
echo -e "${BLUE}测试报告位置:${NC}"
echo "  - 控制台日志: 上方输出"
echo "  - JUnit报告: reports/junit_post_*.xml"
echo "  - Allure结果: reports/allure-results/"
echo "  - 截图目录: screenshots/post_*.png"
echo ""
echo -e "${BLUE}生成Allure报告:${NC}"
echo "  allure serve reports/allure-results"
echo ""
