# 二手商品详情页 AI 聊天功能测试 - 空调

## 测试概述

本测试用例用于验证阿联酋站二手空调商品详情页的 AI 聊天功能，通过模拟真实买家对话场景，验证AI的多轮对话能力、商品信息获取能力和引导能力。

## 测试文件

- **测试脚本**: `test_chat_marketplace_air_conditioner.py`
- **测试站点**: AE (https://ae.58v5.cn)
- **测试角色**: Buyer（买家）
- **测试账号**: 393049273@qq.com / Qa123456

## 测试目标页面

当前测试页面：
```
https://ae.58v5.cn/en/city-abu-dhabi/cate-air-conditioners/Hisense+1+Ton+Inverter+Split+Air+Conditioner-2034518880336068608/?from=
```

商品信息：Hisense 1吨变频分体式空调，Abu Dhabi地区二手商品

## 测试流程（共22条消息）

### 第一阶段：回答AI的主动询问（TC002-TC003）
- **TC002**: 回答预算范围 - "My budget is around 500-800 AED."
- **TC003**: 回答用途需求 - "I need it for my bedroom, around 15-20 square meters."

### 第二阶段：提供联系方式（TC004-TC005）
- **TC004**: 提供邮箱地址（优先）- "You can reach me at john.smith@example.com"
- **TC005**: 提供电话号码 - "My phone number is +971 50 123 4567, you can call me anytime."

### 第三阶段：主动询问商品信息（TC006-TC012）
- **TC006**: 询问商品图片 - "Do you have more photos of the air conditioner? Can I see the back and sides?"
- **TC007**: 询问物品成色 - "What is the condition of this air conditioner? Any scratches or damages?"
- **TC008**: 询问规格大小 - "What are the exact specifications? Dimensions and cooling capacity?"
- **TC009**: 询问商品数量 - "How many units do you have available? Can I buy multiple units?"
- **TC010**: 询问是否可用 - "Is the air conditioner still working properly? Any issues with cooling?"
- **TC011**: 询问已使用时长 - "How long have you been using this air conditioner? How old is it?"
- **TC012**: 询问是否批发/零售 - "Do you offer wholesale pricing? I might need multiple units for my business."

### 第四阶段：价格协商（TC013-TC014）
- **TC013**: 询问价格并砍价 - "Can you offer a better price? Maybe 600 AED including delivery?"
- **TC014**: 询问是否包邮 - "Is delivery free? Or how much would shipping cost to my area?"

### 第五阶段：交易方式（TC015-TC019）
- **TC015**: 询问是否可用洗衣机置换 - "Would you be interested in a trade? I have a washing machine I could exchange."
- **TC016**: 询问地理位置 - "Where exactly are you located in Abu Dhabi? Which area?"
- **TC017**: 询问看货方式 - "Can I come to see the air conditioner before buying? When is a good time?"
- **TC018**: 询问付款方式 - "What payment methods do you accept? Cash, bank transfer, or online payment?"
- **TC019**: 询问邮寄方式 - "How will you deliver the air conditioner? Do you offer installation?"

### 第六阶段：比价（TC020）
- **TC020**: 比价询问 - "I saw similar Hisense 1 ton AC for 650 AED. Why is yours different?"

### 第七阶段：测试AI引导能力（TC021）
- **TC021**: 询问敏感无关问题（宗教信仰）- "What is your religious belief? Are you Muslim or Christian?"
  - 验证AI能否识别并礼貌地引导回商品话题

### 第八阶段：结束对话（TC022）
- **TC022**: 告知没有其他问题 - "Thank you for all the information. I don't have any other questions at the moment."

## 运行测试

### 运行所有用例

```bash
# 需要禁用 CI 环境变量，避免强制无头模式
CI=0 HEADLESS=false pytest test_cases/chat-ai/test_chat_marketplace_air_conditioner.py -v -s
```

### 运行指定优先级用例

```bash
# 运行 P0 核心用例
CI=0 pytest test_cases/chat-ai/test_chat_marketplace_air_conditioner.py -m p0 -v

# 运行 smoke 用例
CI=0 pytest test_cases/chat-ai/test_chat_marketplace_air_conditioner.py -m smoke -v

# 运行回归测试用例
CI=0 pytest test_cases/chat-ai/test_chat_marketplace_air_conditioner.py -m regression -v
```

### 运行指定模块用例

```bash
# 运行商品信息相关用例
CI=0 pytest test_cases/chat-ai/test_chat_marketplace_air_conditioner.py -k "condition or specs or quantity" -v

# 运行价格协商相关用例
CI=0 pytest test_cases/chat-ai/test_chat_marketplace_air_conditioner.py -k "price or shipping" -v

# 运行交易方式相关用例
CI=0 pytest test_cases/chat-ai/test_chat_marketplace_air_conditioner.py -k "location or viewing or payment or delivery" -v
```

### 使用不同的商品URL

```bash
CHAT_PRODUCT_DETAIL_URL="https://ae.58v5.cn/en/city-xxx/cate-xxx/..." \
CI=0 HEADLESS=false \
pytest test_cases/chat-ai/test_chat_marketplace_air_conditioner.py -v
```

### 调试选项

```bash
# 测试结束后保持浏览器打开
KEEP_BROWSER_OPEN=1 CI=0 HEADLESS=false \
pytest test_cases/chat-ai/test_chat_marketplace_air_conditioner.py -v

# 启动时打开 Playwright Inspector
DEBUG_PAUSE=1 CI=0 \
pytest test_cases/chat-ai/test_chat_marketplace_air_conditioner.py -v
```

## 生成 Allure 报告

```bash
# 运行测试并生成报告数据
CI=0 pytest test_cases/chat-ai/test_chat_marketplace_air_conditioner.py --alluredir=reports/allure-results

# 查看报告
allure serve reports/allure-results
```

## 注意事项

1. **对话流程设计**: 测试按真实买家场景设计，先回答AI询问（预算、用途），再主动咨询商品信息
2. **联系方式顺序**: 优先提供邮箱，然后电话号码，符合用户习惯
3. **商品咨询重点**: 重点关注成色、价格、配送等二手交易核心要素
4. **AI回复时间**: AI回复通常在10-30秒内完成，已设置合理的超时时间
5. **消息间隔**: 每条消息发送后会等待AI回复，确保对话连贯性
6. **商品可用性**: 如果测试URL的商品已下架，可通过环境变量或直接修改代码指定新URL
7. **无关问题测试**: 包含宗教信仰等敏感话题，验证AI的引导和过滤能力

## 测试特点

- ✅ 模拟真实买家与卖家AI的完整对话流程
- ✅ 优先回答AI询问，建立信任关系
- ✅ 覆盖二手商品交易的核心咨询场景
- ✅ 验证AI对价格协商、比价等敏感问题的处理能力
- ✅ 测试置换、批发等特殊交易方式
- ✅ 验证无关/敏感问题的引导能力
- ✅ 礼貌结束对话，测试AI的礼仪回应

## 对话设计理念

测试流程遵循真实买家的心理路径：
1. **建立信任**：先回应AI的询问（预算、用途）
2. **提供联系方式**：表明诚意，便于后续沟通
3. **详细了解商品**：询问图片、成色、规格、使用时长等核心信息
4. **价格协商**：砍价、包邮等典型二手交易行为
5. **确认交易细节**：地理位置、看货、付款、配送方式
6. **比价确认**：货比三家，验证性价比
7. **测试边界**：验证AI对无关话题的处理能力
8. **礼貌结束**：正常结束对话

## 与房产测试的差异

- 商品类型：二手家电 vs 房产租赁
- 关注点：成色、使用时长、是否可用 vs 房屋配置、地理位置
- 交易特点：砍价、包邮、置换 vs 租期、押金、看房
- 对话风格：快速交易导向 vs 长期租赁咨询
