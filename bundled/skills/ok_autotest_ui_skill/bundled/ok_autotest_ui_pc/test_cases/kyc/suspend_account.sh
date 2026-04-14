#!/bin/bash
# Airwallex账户状态设置脚本（Bash版本）
# 用于在无法运行Python时的备用方案

echo "============================================================"
echo "Airwallex 账户失败状态设置工具 (Bash版本)"
echo "============================================================"
echo ""

# 配置
USER_ID="796145073984870048"
REDIS_HOST="redis-shark-test.rdb.58dns.org"
REDIS_PORT="50554"
REDIS_PASSWORD="6b0d1d0d640eb6fa"
REDIS_KEY='\xac\xed\x00\x05t\x00\x0fairwallex:token'

DB_HOST="pgsql-test.pdb.58dns.org"
DB_PORT="29000"
DB_NAME="pdb58_easypost"
DB_USER="epost_test"
DB_PASSWORD="GUGXzw49K6Ndp7"

API_BASE_URL="https://api-demo.airwallex.com/api/v1"

# 步骤1: 获取Token
echo "步骤 1/3: 从Redis获取token..."
echo "执行命令:"
echo "redis-cli -h $REDIS_HOST -p $REDIS_PORT -a $REDIS_PASSWORD get \"$REDIS_KEY\""
echo ""
echo "请手动执行上述命令获取token，并保存到变量中"
echo ""

# 提示用户输入token
read -p "请输入token: " TOKEN
echo "Token: $TOKEN"
echo ""

# 步骤2: 查询payment_account_id
echo "步骤 2/3: 从数据库查询payment_account_id..."
echo "执行SQL:"
echo "SELECT payment_account_id FROM user_payment_binding WHERE app_user_id='$USER_ID' ORDER BY id DESC LIMIT 1;"
echo ""
echo "数据库连接信息:"
echo "  Host: $DB_HOST"
echo "  Port: $DB_PORT"
echo "  Database: $DB_NAME"
echo "  Username: $DB_USER"
echo ""

# 提示用户输入payment_account_id
read -p "请输入payment_account_id: " PAYMENT_ACCOUNT_ID
echo "Payment Account ID: $PAYMENT_ACCOUNT_ID"
echo ""

# 步骤3: 调用API设置为SUSPENDED
echo "步骤 3/3: 调用Airwallex API设置为SUSPENDED状态..."
echo ""
echo "执行curl命令:"
echo ""

CURL_CMD="curl --request POST \
  --url '$API_BASE_URL/simulation/accounts/$PAYMENT_ACCOUNT_ID/update_status' \
  --header 'Content-Type: application/json' \
  --header 'Authorization: Bearer $TOKEN' \
  --data '{
    \"force\": false,
    \"next_status\": \"SUSPENDED\"
  }'"

echo "$CURL_CMD"
echo ""
echo "============================================================"
echo "正在发送请求..."
echo "============================================================"
echo ""

# 执行curl命令
eval "$CURL_CMD"

echo ""
echo ""
echo "============================================================"
echo "✅ 请求已发送"
echo "============================================================"
echo "如果返回200状态码，账户已成功设置为SUSPENDED状态"
echo "现在可以在前端测试绑定失败场景"
echo "============================================================"
