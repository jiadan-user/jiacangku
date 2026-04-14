# CI环境配置说明

## 问题描述

在CI/CD环境中运行测试时,所有测试用例因登录失败而报错:
- 本地Session文件不存在
- 登录流程超时
- 元素定位失败

## 解决方案

### 1. 自动检测CI环境

测试脚本会自动检测CI环境变量,并采用不同的策略:

```bash
# 在CI环境中设置环境变量
export CI=true
```

### 2. CI环境优化

当检测到CI环境时,脚本会自动:
- ✅ 跳过Session加载,直接执行登录
- ✅ 增加超时时间(30秒 → 60秒)
- ✅ 显式等待页面元素
- ✅ 保存详细的调试截图

### 3. 超时配置

| 环境 | 默认超时 | 等待超时 | 导航超时 |
|------|---------|---------|---------|
| 本地 | 30秒 | 10秒 | 30秒 |
| CI   | 60秒 | 20秒 | 60秒 |

### 4. 错误调试

登录失败时会自动保存截图到 `reports/` 目录:
- `debug_login_button_failed.png` - 登录按钮点击失败
- `debug_email_input_failed.png` - 邮箱输入失败
- `debug_password_input_failed.png` - 密码输入失败
- `debug_login_verification_failed.png` - 登录验证失败
- `debug_login_failed.png` - 整体登录失败

## CI配置示例

### GitHub Actions

```yaml
name: Run Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          playwright install chromium
      
      - name: Run tests
        env:
          CI: true
          HEADLESS: true
        run: |
          pytest test_cases/test_car/test_ae_car_publish.py -v
      
      - name: Upload screenshots
        if: failure()
        uses: actions/upload-artifact@v3
        with:
          name: debug-screenshots
          path: reports/debug_*.png
      
      - name: Upload Allure report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: allure-results
          path: reports/allure-results
```

### GitLab CI

```yaml
test:
  image: mcr.microsoft.com/playwright/python:v1.40.0-focal
  
  variables:
    CI: "true"
    HEADLESS: "true"
  
  script:
    - pip install -r requirements.txt
    - pytest test_cases/test_car/test_ae_car_publish.py -v
  
  artifacts:
    when: always
    paths:
      - reports/
    expire_in: 1 week
```

### Jenkins

```groovy
pipeline {
    agent any
    
    environment {
        CI = 'true'
        HEADLESS = 'true'
    }
    
    stages {
        stage('Setup') {
            steps {
                sh 'pip install -r requirements.txt'
                sh 'playwright install chromium'
            }
        }
        
        stage('Test') {
            steps {
                sh 'pytest test_cases/test_car/test_ae_car_publish.py -v'
            }
        }
    }
    
    post {
        always {
            archiveArtifacts artifacts: 'reports/**', allowEmptyArchive: true
            junit 'reports/junit.xml'
        }
    }
}
```

## 本地测试CI模式

如果想在本地测试CI模式,可以设置环境变量:

```bash
# 模拟CI环境
export CI=true
export HEADLESS=true

# 运行测试
pytest test_cases/test_car/test_ae_car_publish.py -v

# 取消CI模式
unset CI
unset HEADLESS
```

## 常见问题

### Q1: 为什么CI环境不使用Session?

**A:** CI环境每次运行都是全新的容器/虚拟机,没有持久化存储。即使保存Session,下次运行也无法读取。

### Q2: 如何加快CI测试速度?

**A:** 
1. 使用Docker缓存加速依赖安装
2. 并行运行测试 (`pytest -n auto`)
3. 只运行改动相关的测试

### Q3: 登录仍然失败怎么办?

**A:** 
1. 检查CI环境网络连接
2. 查看调试截图 (`reports/debug_*.png`)
3. 增加超时时间
4. 检查测试账号是否有效

### Q4: 如何查看CI环境的详细日志?

**A:** 
1. 使用 `pytest -v -s` 显示详细输出
2. 检查 `reports/junit.xml` 获取测试结果
3. 查看Allure报告获取可视化结果

## 更新日志

- **2026-03-10**: 初始版本,添加CI环境支持
  - 自动检测CI环境
  - 增加超时时间
  - 添加错误调试截图
  - 优化登录流程
