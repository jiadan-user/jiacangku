# 发布职位测试模块

## 🎯 特殊配置

### 无头模式（Headless Mode）

**本模块强制使用无头模式**，运行测试时不会弹出浏览器窗口，不影响日常工作。

```bash
# 直接运行，不会弹出浏览器
pytest test_cases/publish_job/ -v

# 其他测试模块不受影响，仍会弹出浏览器（如果配置为有头模式）
pytest test_cases/other_module/ -v
```

### 为什么只在这里使用无头模式？

- ✅ **发布职位测试**：测试用例多（36个），运行时间长（约12分钟），适合无头模式
- 🔍 **其他测试**：可能需要观察浏览器行为，保持有头模式方便调试

### 如何临时使用有头模式（调试用）

如果你需要看到浏览器窗口来调试某个测试：

**方法1：临时修改 conftest.py**
```python
# test_cases/publish_job/conftest.py
page = browser_manager.start_browser(
    browser_type=config['browser']['type'],
    headless=False,  # 临时改为 False
    base_url=config['base_url'],
    viewport=config['browser']['viewport']
)
```

**方法2：运行单个测试时使用父级配置**
```bash
# 删除或重命名 publish_job/conftest.py，使用父级配置
mv test_cases/publish_job/conftest.py test_cases/publish_job/conftest.py.bak
pytest test_cases/publish_job/test_xxx.py::test_specific_case -v
mv test_cases/publish_job/conftest.py.bak test_cases/publish_job/conftest.py
```

## 📊 测试用例列表

### 核心流程（4个）
- TC001: 三步向导完整发布职位
- TC002: 使用默认值发布
- TC003: Make another post 导航
- TC004: View my post 导航

### Step1 表单校验（7个）
- TC005: 空字段校验
- TC006: Job Title 100字符边界
- TC007: Job Title 101字符截断
- TC008: Job Title 全空格校验
- TC009: Job Function 为空校验
- TC010: 仅填写 Min Amount 校验
- TC013: 仅填写 Max Amount 校验

### Step1 扩展测试（4个）
- TC014: Max Amount 小于 Min Amount 禁用
- TC015: Show Salary 开关
- TC016: Industry 多选
- TC017: Experience 多选

### Step2 表单校验（4个）
- TC026: Job Description 为空校验
- TC027: Job Description 10000字符边界
- TC028: Job Description 10001字符截断
- TC029: Job Highlights 可选字段

### Step3 功能测试（4个）
- TC034: Experience 枚举值
- TC035: Language 多选
- TC038: Step2 Back 导航
- TC039: Step3 Back 导航

### 安全与UI测试（5个）
- TC040: 未登录用户重定向
- TC041: Step1 进度指示器
- TC042: Step3 按钮文本为 Post
- TC043: 成功页面内容
- TC044: 地图提示文本

### 国际化与兼容性（4个）
- TC059: Chrome 兼容性
- TC061: 1280x768 分辨率
- TC062: AE 站点国际化
- TC063: Job Title 多语言字符

### 冒烟测试（4个）
- 登录并访问发布页面
- Job Title 输入
- 必填字段校验
- 页面元素完整性

## 🚀 快速开始

### 运行所有测试
```bash
cd /Users/weijingjing02/gitsp/ok_autotest_ui_pc
pytest test_cases/publish_job/ -v --alluredir=allure-results
```

### 运行特定分类
```bash
# 只运行冒烟测试
pytest test_cases/publish_job/ -v -m smoke

# 只运行 P0 优先级测试
pytest test_cases/publish_job/ -v -m p0

# 只运行核心流程测试
pytest test_cases/publish_job/test_publish_job_core_flow.py -v
```

### 后台运行（不阻塞终端）
```bash
pytest test_cases/publish_job/ -v > /tmp/pytest_publish.log 2>&1 &
echo "测试正在后台运行，PID: $!"

# 查看进度
tail -f /tmp/pytest_publish.log

# 查看结果
tail -100 /tmp/pytest_publish.log | grep -E "(passed|failed)"
```

## 📝 测试数据

### 测试账号
- 邮箱: `weijingjing02@58.com`
- 密码: `Ok123456`
- 站点: US (https://uspub.58v5.cn)

### 自动登录
测试会自动处理：
- ✅ Cookie 同意弹窗
- ✅ 登录弹窗（两步登录流程）
- ✅ 页面加载等待

## 🔧 配置文件

### 本地配置（publish_job/conftest.py）
- 强制无头模式
- 自动截图（失败时）
- 日志记录

### 全局配置（test_cases/conftest.py）
- 其他测试模块使用
- 可通过环境变量控制

### 站点配置（config/config.yaml）
- 浏览器类型
- 视口大小
- 超时设置

## 📈 测试报告

### Allure 报告
```bash
# 生成报告
pytest test_cases/publish_job/ -v --alluredir=allure-results

# 查看报告
allure serve allure-results
```

### HTML 报告
```bash
pytest test_cases/publish_job/ -v --html=reports/publish_job_report.html --self-contained-html
```

### 截图
失败的测试会自动截图，保存在：
```
reports/screenshots/FAILED_<test_name>_<timestamp>.png
```

## 🐛 调试技巧

### 查看详细日志
```bash
pytest test_cases/publish_job/ -v -s --log-cli-level=INFO
```

### 运行单个测试
```bash
pytest test_cases/publish_job/test_publish_job_smoke.py::test_login_and_access_publish_page -v -s
```

### 失败时进入调试器
```bash
pytest test_cases/publish_job/ -v --pdb
```

## 📞 常见问题

### Q: 为什么看不到浏览器窗口？
A: 本模块强制使用无头模式。如需调试，请临时修改 `conftest.py` 中的 `headless=False`

### Q: 测试运行很慢怎么办？
A: 无头模式已经是最快的方式。可以考虑并行运行：
```bash
pytest test_cases/publish_job/ -v -n 4  # 4个并行进程
```

### Q: 如何只运行失败的测试？
A: 使用 pytest 的 `--lf` 参数：
```bash
pytest test_cases/publish_job/ -v --lf
```

---

**最后更新**: 2026-03-02
**维护者**: QA Team

