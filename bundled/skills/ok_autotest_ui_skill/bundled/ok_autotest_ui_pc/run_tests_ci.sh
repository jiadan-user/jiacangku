#!/bin/bash
# CI/Jenkins 专用测试运行脚本

set -e  # 遇到错误立即退出

echo "======================================"
echo "   Jenkins CI 自动化测试"
echo "======================================"
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 环境变量配置（可被Jenkins覆盖）
SITE=${SITE:-"us"}  # 默认美国站
TEST_TYPE=${TEST_TYPE:-"all"}
BASE_URL=${BASE_URL:-""}  # 留空表示使用站点默认URL
HEADLESS=${HEADLESS:-"true"}
PARALLEL_WORKERS=${PARALLEL_WORKERS:-"4"}
RETRY_TIMES=${RETRY_TIMES:-"2"}

# 站点名称映射
case $SITE in
    "ae")
        SITE_NAME="阿联酋站"
        ;;
    "sg")
        SITE_NAME="新加坡站"
        ;;
    "au")
        SITE_NAME="澳大利亚站"
        ;;
    "us")
        SITE_NAME="美国站"
        ;;
    "hk")
        SITE_NAME="香港站"
        ;;
    *)
        echo -e "${RED}❌ 未知的站点: $SITE${NC}"
        echo "可用站点: ae (阿联酋), sg (新加坡), au (澳大利亚), us (美国), hk (香港)"
        exit 1
        ;;
esac

echo -e "${YELLOW}配置信息：${NC}"
echo "  测试站点: $SITE ($SITE_NAME)"
echo "  测试类型: $TEST_TYPE"
echo "  测试环境: ${BASE_URL:-'使用站点默认URL'}"
echo "  无头模式: $HEADLESS"
echo "  并行数量: $PARALLEL_WORKERS"
echo "  失败重试: $RETRY_TIMES 次"
echo ""

# 1. 清理旧报告
echo -e "${YELLOW}[1/4] 清理旧报告...${NC}"
rm -rf reports/allure-results/*
rm -rf reports/allure-report/*
rm -rf reports/screenshots/*
rm -rf reports/logs/*
mkdir -p reports/{allure-results,screenshots,logs}
echo -e "${GREEN}✅ 清理完成${NC}"
echo ""

# 2. 激活虚拟环境
echo -e "${YELLOW}[2/4] 激活虚拟环境...${NC}"
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ 虚拟环境不存在，请先运行：${NC}"
    echo "   python3 -m venv venv"
    echo "   source venv/bin/activate"
    echo "   pip install -r requirements.txt"
    echo "   playwright install chromium"
    exit 1
fi

source venv/bin/activate
echo -e "${GREEN}✅ 虚拟环境激活${NC}"
echo ""

# 3. 运行测试
echo -e "${YELLOW}[3/4] 运行测试...${NC}"

# 构建pytest命令
PYTEST_CMD="pytest -v"

# 根据测试类型选择用例
case $TEST_TYPE in
    "smoke")
        PYTEST_CMD="$PYTEST_CMD -m smoke"
        echo "  执行冒烟测试"
        ;;
    "p0")
        PYTEST_CMD="$PYTEST_CMD -m p0"
        echo "  执行P0用例"
        ;;
    "login")
        PYTEST_CMD="$PYTEST_CMD -m login"
        echo "  执行登录模块测试"
        ;;
    "all")
        PYTEST_CMD="$PYTEST_CMD test_cases/"
        echo "  执行所有测试"
        ;;
    *)
        echo -e "${RED}❌ 未知的测试类型: $TEST_TYPE${NC}"
        exit 1
        ;;
esac

# 添加报告和重试配置
PYTEST_CMD="$PYTEST_CMD \
    --alluredir=reports/allure-results \
    --clean-alluredir \
    --junitxml=reports/junit.xml \
    --reruns=$RETRY_TIMES \
    --reruns-delay=2 \
    -n $PARALLEL_WORKERS"

# 导出环境变量
export SITE=$SITE
export HEADLESS=$HEADLESS
if [ -n "$BASE_URL" ]; then
    export BASE_URL=$BASE_URL
fi

# 执行测试（不因失败退出）
echo ""
echo "执行命令: $PYTEST_CMD"
echo ""

set +e  # 暂时允许命令失败
$PYTEST_CMD
TEST_EXIT_CODE=$?
set -e

echo ""
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ 所有测试通过${NC}"
else
    echo -e "${YELLOW}⚠️  部分测试失败（退出码: $TEST_EXIT_CODE）${NC}"
fi
echo ""

# 4. 生成报告统计
echo -e "${YELLOW}[4/4] 生成测试统计...${NC}"

# 统计测试结果
if [ -f "reports/junit.xml" ]; then
    STATS=$(python - <<'PY'
import xml.etree.ElementTree as ET

root = ET.parse("reports/junit.xml").getroot()
tests = failures = errors = skipped = 0

def _to_int(value):
    try:
        return int(float(value or 0))
    except (TypeError, ValueError):
        return 0

if root.tag == "testsuite":
    suites = [root]
else:
    suites = root.findall(".//testsuite")

for suite in suites:
    tests += _to_int(suite.attrib.get("tests"))
    failures += _to_int(suite.attrib.get("failures"))
    errors += _to_int(suite.attrib.get("errors"))
    skipped += _to_int(suite.attrib.get("skipped"))

passed = max(tests - failures - errors - skipped, 0)
print(f"{tests} {passed} {failures} {errors} {skipped}")
PY
)
    read -r TOTAL PASSED FAILED ERRORS SKIPPED <<< "$STATS"

    echo "  总数: $TOTAL"
    echo "  通过: $PASSED"
    echo "  失败: $FAILED"
    echo "  错误: $ERRORS"
    echo "  跳过: $SKIPPED"
fi

# 统计截图数量
SCREENSHOT_COUNT=$(ls -1 reports/screenshots/*.png 2>/dev/null | wc -l)
echo "  失败截图: $SCREENSHOT_COUNT 张"

echo -e "${GREEN}✅ 统计完成${NC}"
echo ""

echo "======================================"
echo "   测试执行完成"
echo "======================================"
echo ""
echo "📊 报告位置："
echo "  - Allure结果: reports/allure-results/"
echo "  - JUnit报告: reports/junit.xml"
echo "  - 失败截图: reports/screenshots/"
echo "  - 测试日志: reports/logs/"
echo ""
echo "💡 查看Allure报告："
echo "  allure serve reports/allure-results"
echo ""

# 返回测试退出码
exit $TEST_EXIT_CODE
