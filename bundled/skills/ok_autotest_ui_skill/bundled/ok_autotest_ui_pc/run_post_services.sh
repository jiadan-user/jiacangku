#!/bin/bash
# run_post_services.sh
# OK阿联酋站 - Services发布页测试套件执行脚本

echo "=========================================="
echo "OK阿联酋站 - Services发布页测试套件"
echo "=========================================="

# 清理旧报告
rm -rf reports/allure-results
mkdir -p reports/allure-results
mkdir -p reports/logs
mkdir -p screenshots/test_services

# 执行测试
pytest test_cases/test_post_services.py \
    -v \
    -s \
    --tb=short \
    --alluredir=reports/allure-results \
    --junitxml=reports/junit_services.xml \
    -m "services and ae"

# 生成Allure报告
if [ -d "reports/allure-results" ]; then
    echo ""
    echo "=========================================="
    echo "生成 Allure 报告..."
    echo "=========================================="
    allure generate reports/allure-results -o reports/allure-report --clean
    echo "报告已生成: reports/allure-report/index.html"
fi

echo ""
echo "=========================================="
echo "测试执行完成"
echo "=========================================="
