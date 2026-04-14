# Airwallex 充值流程配置文件
# 使用方法：复制为 airwallex_config.py 并根据实际环境修改配置

# ============================================================================
# Redis 配置
# ============================================================================
REDIS_CONFIG = {
    'host': 'redis-shark-test.rdb.58dns.org',
    'port': 50554,
    'password': '6b0d1d0d640eb6fa'
}

# ============================================================================
# PostgreSQL 数据库配置
# ============================================================================
PG_CONFIG = {
    'host': 'pgsql-test.pdb.58dns.org',
    'port': 29000,
    'database': 'pdb58_easypost',
    'user': 'epost_test',
    'password': 'GUGXzw49K6Ndp7'
}

# ============================================================================
# Airwallex API 配置
# ============================================================================
AIRWALLEX_API_URL = 'https://api-demo.airwallex.com/api/v1/connected_account_transfers/create'

# ============================================================================
# 充值配置
# ============================================================================
RECHARGE_CONFIG = {
    # 默认充值金额
    'default_amount': '20.01',
    
    # 默认币种
    'default_currency': 'USD',
    
    # 默认充值原因（必须是 Airwallex 允许的枚举值之一）
    # 可选值：
    # - wages_salary: 工资
    # - donation_charitable_contribution: 捐赠
    # - personal_remittance: 个人汇款
    # - transfer_to_own_account: 转账到自己账户
    # - pension: 养老金
    # - family_support: 家庭支持
    # - living_expenses: 生活费用
    # - education_training: 教育培训
    # - travel: 旅行
    # - investment_proceeds: 投资收益
    # - investment_capital: 投资资本
    # - loan_credit_repayment: 贷款偿还
    # - taxes: 税费
    # - goods_purchased: 购买商品
    # - business_expenses: 业务费用
    # - medical_services: 医疗服务
    # - professional_business_services: 专业商业服务
    # - technical_services: 技术服务
    # - other_services: 其他服务
    # - construction: 建筑
    # - freight: 货运
    # - real_estate: 房地产
    # - settlement: 结算
    # - commission: 佣金
    'default_reason': 'travel',
    
    # 目标用户 ID（从数据库查询 payment_account_id）
    'app_user_id': '796133836057336352'
}
