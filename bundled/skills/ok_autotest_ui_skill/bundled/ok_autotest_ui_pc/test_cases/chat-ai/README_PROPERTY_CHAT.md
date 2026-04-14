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

## 测试流程（共17条消息）

### 第一阶段：回答AI的主动询问（1-3）
- **TC001**: 回答租期需求 - "I'm looking for a 12-month lease, starting from April 2026."
- **TC002**: 回答预算范围 - "My budget is around $600-800 per week."
- **TC003**: 回答入住时间 - "I plan to move in around mid-April, flexible on the exact date."

### 第二阶段：提供联系方式（4-5）
- **TC004**: 提供邮箱地址（优先）- "You can reach me at john.smith@example.com"
- **TC005**: 提供电话号码 - "My phone number is +61 412 345 678, feel free to call me anytime."

### 第三阶段：询问地理位置（6）
- **TC006**: 询问具体地址和周边设施 - "Where exactly is this apartment located? What facilities are nearby like shops, universities, or transport?"

### 第四阶段：主动询问房屋配置（7-11）
- **TC007**: 询问卧室数量 - "How many bedrooms are there in this student apartment?"
- **TC008**: 询问实用面积 - "What is the usable area or size of this apartment in square meters?"
- **TC009**: 询问楼龄和楼层 - "How old is the building and which floor is this apartment on?"
- **TC010**: 询问车位配置 - "Is there a parking space included with this apartment?"
- **TC011**: 询问物业管理 - "What property management services are included? Are there maintenance fees?"

### 第五阶段：看房和租金详情（12-14）
- **TC012**: 询问看房时间 - "When can I schedule a viewing for this apartment?"
- **TC013**: 询问租金价格 - "What is the weekly or monthly rental price for this apartment?"
- **TC014**: 询问付款方式 - "What payment methods are accepted? Do you require a deposit?"

### 第六阶段：综合深入询问（15）
- **TC015**: 综合询问 - "Can you tell me about the lease term, utilities included, and if pets are allowed?"

### 第七阶段：测试AI引导能力（16）
- **TC016**: 询问敏感无关问题（宗教信仰）- "What is your religious belief? Do you believe in God?"
  - 验证AI能否识别并礼貌地引导回房产话题

### 第八阶段：结束对话（17）
- **TC017**: 告知没有其他问题 - "Thank you for all the information. I don't have any other questions at the moment."

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
- ✅ 优先回答AI询问，建立信任关系
- ✅ 覆盖房屋租赁的核心咨询场景
- ✅ 验证AI对不同类型问题的处理能力
- ✅ 测试联系方式交换的完整流程
- ✅ 验证无关/敏感问题的引导能力
- ✅ 礼貌结束对话，测试AI的礼仪回应

## 对话设计理念

测试流程遵循真实租户的心理路径：
1. **建立信任**：先回应AI的询问（租期、预算、入住时间）
2. **提供联系方式**：表明诚意，便于后续沟通
3. **了解位置**：地理位置是租房的首要考虑因素
4. **详细了解**：深入询问房屋配置、租金、付款等细节
5. **综合评估**：询问租赁条款、水电、宠物等综合问题
6. **测试边界**：验证AI对无关话题的处理能力
7. **礼貌结束**：正常结束对话
