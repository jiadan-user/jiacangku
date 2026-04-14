# Airwallex账户状态设置脚本（PowerShell版本）
# 用于Windows环境下的快速操作

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Airwallex 账户失败状态设置工具 (PowerShell版本)" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# 配置
$USER_ID = "796145073984870048"
$REDIS_HOST = "redis-shark-test.rdb.58dns.org"
$REDIS_PORT = "50554"
$REDIS_PASSWORD = "6b0d1d0d640eb6fa"
$REDIS_KEY = '\xac\xed\x00\x05t\x00\x0fairwallex:token'

$DB_HOST = "pgsql-test.pdb.58dns.org"
$DB_PORT = "29000"
$DB_NAME = "pdb58_easypost"
$DB_USER = "epost_test"
$DB_PASSWORD = "GUGXzw49K6Ndp7"

$API_BASE_URL = "https://api-demo.airwallex.com/api/v1"

# 步骤1: 获取Token
Write-Host "步骤 1/3: 从Redis获取token..." -ForegroundColor Yellow
Write-Host "执行命令:"
Write-Host "redis-cli -h $REDIS_HOST -p $REDIS_PORT -a $REDIS_PASSWORD get `"$REDIS_KEY`"" -ForegroundColor Gray
Write-Host ""
Write-Host "请手动执行上述命令获取token，或直接输入token" -ForegroundColor Yellow
Write-Host ""

# 提示用户输入token
$TOKEN = Read-Host "请输入token"
Write-Host "Token: $TOKEN" -ForegroundColor Green
Write-Host ""

# 步骤2: 查询payment_account_id
Write-Host "步骤 2/3: 从数据库查询payment_account_id..." -ForegroundColor Yellow
Write-Host "执行SQL:"
Write-Host "SELECT payment_account_id FROM user_payment_binding WHERE app_user_id='$USER_ID' ORDER BY id DESC LIMIT 1;" -ForegroundColor Gray
Write-Host ""
Write-Host "数据库连接信息:"
Write-Host "  Host: $DB_HOST" -ForegroundColor Gray
Write-Host "  Port: $DB_PORT" -ForegroundColor Gray
Write-Host "  Database: $DB_NAME" -ForegroundColor Gray
Write-Host "  Username: $DB_USER" -ForegroundColor Gray
Write-Host ""

# 提示用户输入payment_account_id
$PAYMENT_ACCOUNT_ID = Read-Host "请输入payment_account_id"
Write-Host "Payment Account ID: $PAYMENT_ACCOUNT_ID" -ForegroundColor Green
Write-Host ""

# 步骤3: 调用API设置为SUSPENDED
Write-Host "步骤 3/3: 调用Airwallex API设置为SUSPENDED状态..." -ForegroundColor Yellow
Write-Host ""

$url = "$API_BASE_URL/simulation/accounts/$PAYMENT_ACCOUNT_ID/update_status"
$headers = @{
    "Content-Type" = "application/json"
    "Authorization" = "Bearer $TOKEN"
}
$body = @{
    "force" = $false
    "next_status" = "SUSPENDED"
} | ConvertTo-Json

Write-Host "请求URL: $url" -ForegroundColor Gray
Write-Host "请求Body: $body" -ForegroundColor Gray
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "正在发送请求..." -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

try {
    $response = Invoke-RestMethod -Uri $url -Method Post -Headers $headers -Body $body -ContentType "application/json"
    
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Green
    Write-Host "✅ 请求成功" -ForegroundColor Green
    Write-Host "============================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "响应内容:" -ForegroundColor Green
    $response | ConvertTo-Json -Depth 10
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Green
    Write-Host "✅ 账户已成功设置为SUSPENDED状态" -ForegroundColor Green
    Write-Host "============================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "🎯 现在可以在前端进行以下测试:" -ForegroundColor Cyan
    Write-Host "   1. 测试绑定银行账户失败场景" -ForegroundColor Cyan
    Write-Host "   2. 验证失败提示信息是否正确显示" -ForegroundColor Cyan
    Write-Host "   3. 检查错误处理逻辑" -ForegroundColor Cyan
    Write-Host ""
} catch {
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Red
    Write-Host "❌ 请求失败" -ForegroundColor Red
    Write-Host "============================================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "错误信息:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "响应内容:" -ForegroundColor Red
        Write-Host $responseBody -ForegroundColor Red
    }
    Write-Host ""
    Write-Host "请检查:" -ForegroundColor Yellow
    Write-Host "  1. Token是否有效" -ForegroundColor Yellow
    Write-Host "  2. Payment Account ID是否正确" -ForegroundColor Yellow
    Write-Host "  3. API权限是否充足" -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "按任意键退出..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
