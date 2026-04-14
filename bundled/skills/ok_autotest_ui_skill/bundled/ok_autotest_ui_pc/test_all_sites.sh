#!/bin/bash
# 测试所有站点的快速脚本

set -e  # 遇到错误立即退出

echo "======================================"
echo "   多站点测试脚本"
echo "======================================"
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置
TEST_TYPE=${TEST_TYPE:-"smoke"}  # 默认运行冒烟测试
HEADLESS=${HEADLESS:-"true"}
SITES=("ae" "us" "hk")

# 站点名称映射
declare -A SITE_NAMES
SITE_NAMES["ae"]="阿联酋站"
SITE_NAMES["us"]="美国站"
SITE_NAMES["hk"]="香港站"

# 统计
TOTAL_SITES=${#SITES[@]}
PASSED_SITES=0
FAILED_SITES=0
declare -a FAILED_SITE_LIST

echo -e "${YELLOW}测试配置：${NC}"
echo "  测试类型: $TEST_TYPE"
echo "  无头模式: $HEADLESS"
echo "  站点数量: $TOTAL_SITES (${SITES[*]})"
echo ""

# 遍历所有站点
for site in "${SITES[@]}"; do
    echo ""
    echo -e "${BLUE}======================================${NC}"
    echo -e "${BLUE}   测试站点: $site (${SITE_NAMES[$site]})${NC}"
    echo -e "${BLUE}======================================${NC}"
    echo ""
    
    # 设置环境变量
    export SITE=$site
    export HEADLESS=$HEADLESS
    
    # 执行测试（允许失败）
    set +e
    if [ "$TEST_TYPE" == "smoke" ]; then
        pytest -v -m smoke test_cases/
    elif [ "$TEST_TYPE" == "p0" ]; then
        pytest -v -m p0 test_cases/
    else
        pytest -v test_cases/
    fi
    
    EXIT_CODE=$?
    set -e
    
    # 统计结果
    if [ $EXIT_CODE -eq 0 ]; then
        echo ""
        echo -e "${GREEN}✅ $site (${SITE_NAMES[$site]}) 测试通过${NC}"
        PASSED_SITES=$((PASSED_SITES + 1))
    else
        echo ""
        echo -e "${RED}❌ $site (${SITE_NAMES[$site]}) 测试失败${NC}"
        FAILED_SITES=$((FAILED_SITES + 1))
        FAILED_SITE_LIST+=("$site")
    fi
    
    echo ""
done

# 打印总结
echo ""
echo "======================================"
echo "   测试结果总结"
echo "======================================"
echo ""
echo -e "总计站点: ${TOTAL_SITES}"
echo -e "${GREEN}通过站点: ${PASSED_SITES}${NC}"
echo -e "${RED}失败站点: ${FAILED_SITES}${NC}"

if [ ${#FAILED_SITE_LIST[@]} -gt 0 ]; then
    echo ""
    echo -e "${RED}失败的站点列表：${NC}"
    for failed_site in "${FAILED_SITE_LIST[@]}"; do
        echo -e "  - $failed_site (${SITE_NAMES[$failed_site]})"
    done
fi

echo ""
echo "======================================"

# 如果有失败，返回失败退出码
if [ $FAILED_SITES -gt 0 ]; then
    echo -e "${RED}❌ 部分站点测试失败${NC}"
    exit 1
else
    echo -e "${GREEN}🎉 所有站点测试通过！${NC}"
    exit 0
fi

