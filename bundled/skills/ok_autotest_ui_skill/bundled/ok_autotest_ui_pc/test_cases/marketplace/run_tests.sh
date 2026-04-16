#!/bin/bash
# AE站 Marketplace 列表页测试执行脚本（单文件 TC001-TC060）

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

LIST_PAGE_FILE="test_cases/marketplace/test_ae_marketplace_list_page.py"

# 与 ok-ae-Marketplace-ListPage-测试用例-扩展版-20260401.md 对齐的用例子集（pytest -k）
K_BASIC='test_tc001 or test_tc002 or test_tc003 or test_tc004 or test_tc005 or test_tc006 or test_tc026 or test_tc027 or test_tc028 or test_tc029 or test_tc030 or test_tc031 or test_tc032 or test_tc033 or test_tc034 or test_tc035 or test_tc036 or test_tc037 or test_tc038'
K_FILTER='test_tc007 or test_tc008 or test_tc009 or test_tc010 or test_tc011 or test_tc012 or test_tc013 or test_tc014'
K_CARD='test_tc015 or test_tc016 or test_tc017 or test_tc018 or test_tc019 or test_tc020 or test_tc021 or test_tc022 or test_tc023 or test_tc024 or test_tc025'
K_EXTENDED='test_tc039 or test_tc040 or test_tc041 or test_tc042 or test_tc043 or test_tc044 or test_tc045 or test_tc046 or test_tc047 or test_tc048 or test_tc049 or test_tc050 or test_tc051 or test_tc052 or test_tc053 or test_tc054 or test_tc055 or test_tc056 or test_tc057 or test_tc058 or test_tc059 or test_tc060'
K_MEDIA='test_tc055 or test_tc056 or test_tc057 or test_tc058 or test_tc059 or test_tc060'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}AE站 Marketplace 列表页自动化测试${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

show_help() {
    echo "用法: ./run_tests.sh [选项]"
    echo ""
    echo "选项:"
    echo "  smoke         冒烟测试（-m smoke，单文件内带 smoke 标记的用例）"
    echo "  full          完整回归 TC001-TC060（60 条）"
    echo "  basic         TC001-006 + TC026-038（页面进入、搜索与扩展搜索）"
    echo "  filter        TC007-014（筛选与排序）"
    echo "  card          TC015-025（卡片、收藏、分页与会话）"
    echo "  extended      TC039-060（扩展用例：筛选/排序/卡片表现/分页/图片/响应式等）"
    echo "  media         TC055-060（懒加载、图片、响应式、无障碍）"
    echo "  p0            同目录下 P0 标记用例（含详情页等其他脚本时一并选中）"
    echo "  p1            同目录下 P1 标记用例"
    echo "  help          显示此帮助"
    echo ""
    echo "主脚本: ${LIST_PAGE_FILE}"
    echo "用例文档: ok-ae-Marketplace-ListPage-测试用例-扩展版-20260401.md"
}

run_test() {
    local test_type=$1
    local description=$2
    shift 2
    echo -e "${YELLOW}>>> 开始执行: ${description}${NC}"
    echo ""
    cd "${PROJECT_ROOT}"
    pytest "$@" \
        --alluredir=reports/allure-results \
        --html="reports/marketplace_${test_type}_report.html" \
        --self-contained-html
    local exit_code=$?
    if [ $exit_code -eq 0 ]; then
        echo -e "${GREEN}✅ ${description} - 测试通过${NC}"
    else
        echo -e "${RED}❌ ${description} - 测试失败${NC}"
    fi
    echo ""
    return $exit_code
}

generate_allure_report() {
    echo -e "${YELLOW}>>> 生成Allure测试报告...${NC}"
    cd "${PROJECT_ROOT}"
    if command -v allure &> /dev/null; then
        allure generate reports/allure-results -o reports/allure-report --clean
        echo -e "${GREEN}✅ Allure报告: reports/allure-report/index.html${NC}"
    else
        echo -e "${YELLOW}⚠️  未安装 allure 命令，跳过${NC}"
    fi
    echo ""
}

main() {
    local test_mode=${1:-help}
    case $test_mode in
        smoke)
            run_test "smoke" "Marketplace 列表页冒烟测试" -v -s "${LIST_PAGE_FILE}" -m smoke
            generate_allure_report
            ;;
        full)
            run_test "full" "Marketplace 列表页完整回归 TC001-TC060" -v -s "${LIST_PAGE_FILE}"
            generate_allure_report
            ;;
        basic)
            run_test "basic" "列表页 basic（TC001-006 + TC026-038）" -v -s "${LIST_PAGE_FILE}" -k "${K_BASIC}"
            generate_allure_report
            ;;
        filter)
            run_test "filter" "列表页筛选排序（TC007-014）" -v -s "${LIST_PAGE_FILE}" -k "${K_FILTER}"
            generate_allure_report
            ;;
        card)
            run_test "card" "列表页卡片收藏分页（TC015-025）" -v -s "${LIST_PAGE_FILE}" -k "${K_CARD}"
            generate_allure_report
            ;;
        extended)
            run_test "extended" "列表页扩展用例（TC039-060）" -v -s "${LIST_PAGE_FILE}" -k "${K_EXTENDED}"
            generate_allure_report
            ;;
        media)
            run_test "media" "列表页图片与响应式（TC055-060）" -v -s "${LIST_PAGE_FILE}" -k "${K_MEDIA}"
            generate_allure_report
            ;;
        p0)
            run_test "p0" "Marketplace 目录 P0" -v -s "test_cases/marketplace/" -m p0
            generate_allure_report
            ;;
        p1)
            run_test "p1" "Marketplace 目录 P1" -v -s "test_cases/marketplace/" -m p1
            generate_allure_report
            ;;
        help|*)
            show_help
            ;;
    esac
}

main "$@"
