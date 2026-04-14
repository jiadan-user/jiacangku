#!/bin/bash

# run_post_category.sh
# Post分类选择页测试执行脚本

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 打印带颜色的标题
print_title() {
    echo -e "${CYAN}========================================${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}========================================${NC}"
}

# 打印成功消息
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# 打印错误消息
print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# 打印警告消息
print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# 打印信息消息
print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# 清屏
clear

print_title "OK阿联酋站 - Post分类选择页测试"

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    print_error "Python3 未安装"
    exit 1
fi

print_success "Python3 环境检查通过"

# 检查pytest
if ! python3 -c "import pytest" &> /dev/null; then
    print_error "pytest 未安装，请运行: pip install pytest"
    exit 1
fi

print_success "pytest 环境检查通过"

# 创建必要的目录
mkdir -p screenshots
mkdir -p allure-results
mkdir -p test-results

print_success "目录创建完成"

# 显示菜单
echo ""
print_title "请选择测试模式"
echo -e "${YELLOW}1)${NC} 运行所有测试（15个用例）"
echo -e "${YELLOW}2)${NC} 只运行P0用例（8个关键用例）"
echo -e "${YELLOW}3)${NC} 只运行搜索功能测试（5个用例）"
echo -e "${YELLOW}4)${NC} 只运行分类卡片测试（6个用例）"
echo -e "${YELLOW}5)${NC} 运行单个测试用例"
echo -e "${YELLOW}6)${NC} 生成Allure报告"
echo -e "${YELLOW}0)${NC} 退出"
echo ""

read -p "请输入选项 [0-6]: " choice

case $choice in
    1)
        print_title "运行所有测试（15个用例）"
        pytest test_cases/test_post_category.py \
            -v \
            --tb=short \
            --alluredir=allure-results \
            --junitxml=test-results/junit-post-category.xml \
            -m "post"
        ;;
    2)
        print_title "运行P0用例（8个关键用例）"
        pytest test_cases/test_post_category.py \
            -v \
            --tb=short \
            --alluredir=allure-results \
            --junitxml=test-results/junit-post-p0.xml \
            -k "test_access_post_category_page or test_search_marketplace or test_click_jobs_card or test_click_property_card or test_click_marketplace_card or test_click_services_card or test_click_community_card or test_click_cars_card"
        ;;
    3)
        print_title "运行搜索功能测试（5个用例）"
        pytest test_cases/test_post_category.py \
            -v \
            --tb=short \
            --alluredir=allure-results \
            --junitxml=test-results/junit-post-search.xml \
            -m "search"
        ;;
    4)
        print_title "运行分类卡片测试（6个用例）"
        pytest test_cases/test_post_category.py \
            -v \
            --tb=short \
            --alluredir=allure-results \
            --junitxml=test-results/junit-post-cards.xml \
            -k "test_click"
        ;;
    5)
        print_title "运行单个测试用例"
        echo ""
        echo "可用的测试用例："
        echo "  TC001: test_access_post_category_page"
        echo "  TC002: test_click_search_box"
        echo "  TC003: test_search_marketplace"
        echo "  TC004: test_search_job"
        echo "  TC005: test_clear_search_box"
        echo "  TC006: test_click_jobs_card"
        echo "  TC007: test_click_property_card"
        echo "  TC008: test_click_marketplace_card"
        echo "  TC009: test_click_services_card"
        echo "  TC010: test_click_community_card"
        echo "  TC011: test_click_cars_card"
        echo "  TC012: test_search_no_results"
        echo "  TC013: test_search_special_chars"
        echo "  TC014: test_click_suggestion_item"
        echo "  TC015: test_browser_back"
        echo ""
        read -p "请输入测试用例名称: " test_name
        
        pytest test_cases/test_post_category.py::$test_name \
            -v \
            --tb=short \
            --alluredir=allure-results \
            --junitxml=test-results/junit-single.xml
        ;;
    6)
        print_title "生成Allure报告"
        if command -v allure &> /dev/null; then
            allure generate allure-results -o allure-report --clean
            print_success "Allure报告生成完成"
            print_info "查看报告: allure open allure-report"
        else
            print_error "Allure 未安装"
            print_info "安装方法: brew install allure (macOS)"
        fi
        ;;
    0)
        print_info "退出测试"
        exit 0
        ;;
    *)
        print_error "无效的选项"
        exit 1
        ;;
esac

# 显示测试结果
echo ""
if [ $? -eq 0 ]; then
    print_success "测试执行完成"
    print_info "查看截图: screenshots/"
    print_info "查看JUnit报告: test-results/"
    print_info "生成Allure报告: ./run_post_category.sh 选项6"
else
    print_error "测试执行失败"
    exit 1
fi
