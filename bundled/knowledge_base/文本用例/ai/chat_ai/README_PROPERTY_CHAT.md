# 房产详情页 AI 聊天功能测试

## 测试概述

本测试用例用于验证澳大利亚站学生公寓详情页的 AI 聊天功能，通过模拟真实租户对话场景，验证AI的多轮对话能力、信息获取能力和引导能力。

## 测试文件

- **测试脚本**: `test_chat_property_student_apartment.py`
- **测试站点**: AU (https://au.58v5.cn)
- **测试角色**: Buyer（租户）
- **测试账号**: 393049273@qq.com / Qa123456

## 测试目标页面

当前测试页面：
```
https://au.58v5.cn/en/city-new-south-wales/cate-property-student-apartment/%5BOriginalID%3A6529470774541110%5D+2+Bed+2+Bath+1+Carspace+6+Pual+Street+Zetland%2C+Sydney-6574798962022110/?from=
```

房产信息：2卧2浴1车位，Sydney Zetland区学生公寓

## 测试流程（共19条用例）

### 模块一：进入聊天页面（1）
- **TC001**: 点击学生公寓详情页 Contact 按钮应跳转到聊天页面
  - 验证Contact按钮点击后能成功进入聊天页面

### 模块二：AI多轮对话 - 房屋配置询问（2-8）
- **TC002**: 询问卫浴数量 - "How many bathrooms does this apartment have?"
  - 验证AI能基于帖子信息正确回复卫浴数量
- **TC003**: 询问卧室数量 - "How many bedrooms are there in this student apartment?"
  - 验证AI能基于帖子信息正确回复卧室数量
- **TC004**: 询问装潢程度 - "Is the apartment furnished or unfurnished? What furniture is included?"
  - 验证AI能基于帖子信息正确回复装潢程度和家具配置
- **TC005**: 询问实用面积 - "What is the usable area or size of this apartment in square meters?"
  - 验证AI能基于帖子信息正确回复实用面积
- **TC006**: 询问楼龄和楼层 - "How old is the building and which floor is this apartment on?"
  - 验证AI能基于帖子信息正确回复楼龄和楼层
- **TC007**: 询问车位配置 - "Is there a parking space included with this apartment?"
  - 验证AI能基于帖子信息正确回复车位配置
- **TC008**: 询问物业管理 - "What property management services are included? Are there maintenance fees?"
  - 验证AI能基于帖子信息正确回复物业管理信息

### 模块三：AI多轮对话 - 地理位置和交通（9）
- **TC009**: 询问具体地址和周边设施 - "Where exactly is this apartment located? What facilities are nearby like shops, universities, or transport?"
  - 验证AI能正确提供地理位置和周边设施信息

### 模块四：AI多轮对话 - 看房和付款（10-12）
- **TC010**: 询问看房时间 - "When can I schedule a viewing for this apartment?"
  - 验证AI能提供合理的回复或引导联系房东
- **TC011**: 询问付款方式 - "What payment methods are accepted? Do you require a deposit?"
  - 验证AI能提供付款方式相关信息
- **TC012**: 询问租金价格 - "What is the weekly or monthly rental price for this apartment?"
  - 验证AI能基于帖子信息正确回复租金价格

### 模块五：AI对话 - 无关问题测试（13）
- **TC013**: 询问敏感无关问题（宗教信仰）- "What is your religious belief? Do you believe in God?"
  - 验证AI能识别并做出合理回应（引导回主题或礼貌拒绝）

### 模块六：AI询问联系方式（14-17）
- **TC014**: 提供邮箱地址（优先联系方式）- "You can reach me at john.smith@example.com"
  - 验证AI能正确接收并回复邮箱地址
- **TC015**: 提供WhatsApp号码 - "My WhatsApp is +61 423 456 789"
  - 验证AI能正确接收并回复WhatsApp号码
- **TC016**: 提供微信号 - "You can add me on WeChat: johnsmith2026"
  - 验证AI能正确接收并回复微信号
- **TC017**: 提供手机号码（最后联系方式）- "My phone number is +61 412 345 678, feel free to call me anytime."
  - 验证AI能正确接收并回复手机号码

### 模块七：综合对话验证（18-19）
- **TC018**: 综合询问多个问题 - "I'm very interested in this apartment. Can you tell me about the lease term, utilities included, and if pets are allowed?"
  - 验证AI能理解并作出全面回复
- **TC019**: 结束对话 - "Thank you for all the information. I don't have any other questions at the moment."
  - 验证AI能给出礼貌的结束回复

## 运行测试

### 运行所有用例

```bash
# 需要禁用 CI 环境变量，避免强制无头模式
CI=0 HEADLESS=false pytest test_cases/chat-ai/test_chat_property_student_apartment.py -v -s
```

### 运行指定优先级用例

```bash
# 运行 P0 核心用例
CI=0 pytest test_cases/chat-ai/test_chat_property_student_apartment.py -m p0 -v

# 运行 smoke 用例
CI=0 pytest test_cases/chat-ai/test_chat_property_student_apartment.py -m smoke -v

# 运行回归测试用例
CI=0 pytest test_cases/chat-ai/test_chat_property_student_apartment.py -m regression -v
```

### 运行指定模块用例

```bash
# 运行房屋配置相关用例
CI=0 pytest test_cases/chat-ai/test_chat_property_student_apartment.py -k "facilities" -v

# 运行联系方式相关用例
CI=0 pytest test_cases/chat-ai/test_chat_property_student_apartment.py -k "contact_info" -v

# 运行地理位置相关用例
CI=0 pytest test_cases/chat-ai/test_chat_property_student_apartment.py -k "location" -v
```

### 使用不同的房产URL

```bash
CHAT_PROPERTY_DETAIL_URL="https://au.58v5.cn/en/city-xxx/cate-property-xxx/..." \
CI=0 HEADLESS=false \
pytest test_cases/chat-ai/test_chat_property_student_apartment.py -v
```

### 调试选项

```bash
# 测试结束后保持浏览器打开
KEEP_BROWSER_OPEN=1 CI=0 HEADLESS=false \
pytest test_cases/chat-ai/test_chat_property_student_apartment.py -v

# 启动时打开 Playwright Inspector
DEBUG_PAUSE=1 CI=0 \
pytest test_cases/chat-ai/test_chat_property_student_apartment.py -v
```

## 生成 Allure 报告

```bash
# 运行测试并生成报告数据
pytest test_cases/chat-ai/test_chat_property_student_apartment.py --alluredir=reports/allure-results

# 查看报告
allure serve reports/allure-results
```

## 注意事项

1. **对话流程设计**: 测试按真实租户场景设计，先回答AI询问（租期、预算、入住时间），再主动咨询房屋信息
2. **联系方式顺序**: 优先提供邮箱，然后电话号码，符合用户习惯
3. **地理位置优先**: 在提供联系方式后，优先询问位置信息
4. **AI回复时间**: AI回复通常在10-30秒内完成，已设置合理的超时时间
5. **消息间隔**: 每条消息发送后会等待AI回复，确保对话连贯性
6. **帖子可用性**: 如果测试URL的帖子已下架，可通过环境变量或直接修改代码指定新URL
7. **无关问题测试**: 包含宗教信仰等敏感话题，验证AI的引导和过滤能力

## 测试特点

- ✅ 模拟真实用户与AI的完整对话流程
- ✅ 覆盖房屋租赁的核心咨询场景（房屋配置、地理位置、价格、看房等）
- ✅ 验证AI对不同类型问题的处理能力
- ✅ 测试联系方式交换的完整流程（邮箱、WhatsApp、微信、电话）
- ✅ 验证无关/敏感问题的引导能力
- ✅ 礼貌结束对话，测试AI的礼仪回应
- ✅ 所有用例共享同一浏览器session，提升执行效率

## 测试优化说明

本测试使用 **module 级 fixture**，整个测试模块共享同一个浏览器和聊天页面：
- 仅在模块初始化时登录并进入聊天页面一次
- 所有用例共享同一个聊天会话，避免重复导航
- 显著提升测试执行效率和稳定性

## 用例优先级说明

- **P0（Critical）**：核心功能，必须通过（7条）
  - TC001: 进入聊天页面
  - TC002: 询问卫浴数量
  - TC003: 询问卧室数量
  - TC009: 询问地理位置
  - TC010-TC012: 看房和付款
  - TC014: 提供联系方式
  - TC018: 综合问题

- **P1（Normal）**：重要功能（8条）
  - TC004-TC008: 房屋配置详细询问
  - TC013: 无关问题测试
  - TC015-TC017: 其他联系方式
  - TC019: 结束对话

- **P2（Minor）**：次要功能（4条）
  - TC017: 提供手机号码
