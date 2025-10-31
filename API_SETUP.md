# API配置说明

## 问题诊断

当前配置的DeepSeek API密钥测试失败（Access denied）。

可能的原因：
1. ❌ API密钥无效或已过期
2. ❌ API密钥没有正确的权限
3. ❌ 需要检查账户状态

## 解决方案

### 方案1: 检查并更新DeepSeek API密钥

1. **访问DeepSeek平台**：https://platform.deepseek.com/api_keys

2. **检查API密钥状态**：
   - 确认密钥是否有效
   - 检查是否有使用额度
   - 确认密钥权限

3. **获取新的API密钥**（如果需要）：
   - 登录DeepSeek平台
   - 创建新的API密钥
   - 复制密钥

4. **更新配置**：
   ```bash
   # 编辑 .env 文件
   nano .env

   # 更新内容为：
   DEEPSEEK_API_KEY=你的新密钥
   ```

5. **测试连接**：
   ```bash
   python test_deepseek_api.py
   ```

### 方案2: 使用豆包(Doubao) API

您的消息中提到了豆包API。如果想使用豆包API，需要修改配置：

#### 步骤1: 更新 .env 文件

```bash
# 使用豆包API配置
DOUBAO_API_KEY=d0f9bb92-cfa9-4261-912c-621c3fc6d509
DOUBAO_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
DOUBAO_MODEL=doubao-seed-1-6-251015
```

#### 步骤2: 修改 app.py

需要修改 app.py 中的API配置：

```python
# 在 app.py 第30-43行左右，替换为：

# 检查使用哪个API
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
DOUBAO_API_KEY = os.getenv('DOUBAO_API_KEY')
DOUBAO_BASE_URL = os.getenv('DOUBAO_BASE_URL')
DOUBAO_MODEL = os.getenv('DOUBAO_MODEL')

client = None

if DOUBAO_API_KEY:
    # 使用豆包API
    print("使用豆包API")
    client = OpenAI(
        api_key=DOUBAO_API_KEY,
        base_url=DOUBAO_BASE_URL
    )
    AI_MODEL = DOUBAO_MODEL
elif DEEPSEEK_API_KEY:
    # 使用DeepSeek API
    print("使用DeepSeek API")
    client = OpenAI(
        api_key=DEEPSEEK_API_KEY,
        base_url="https://api.deepseek.com"
    )
    AI_MODEL = "deepseek-chat"
else:
    print("警告: 未配置API密钥")
    AI_MODEL = None
```

然后在批改函数中使用 `AI_MODEL` 变量：

```python
# 在 check_essay_with_ai() 函数中，大约第228行
response = client.chat.completions.create(
    model=AI_MODEL,  # 改为使用变量
    messages=[...],
    ...
)
```

## 快速测试命令

### 测试DeepSeek API
```bash
curl https://api.deepseek.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-7a5c87492473439d833d545a2633f986" \
  -d '{
    "model": "deepseek-chat",
    "messages": [
      {"role": "user", "content": "Hello"}
    ]
  }'
```

### 测试豆包API
```bash
curl https://ark.cn-beijing.volces.com/api/v3/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer d0f9bb92-cfa9-4261-912c-621c3fc6d509" \
  -d '{
    "model": "doubao-seed-1-6-251015",
    "messages": [
      {"role": "user", "content": "Hello"}
    ]
  }'
```

## 推荐操作步骤

### 立即测试（推荐）

1. **先测试哪个API可用**：
   ```bash
   # 测试DeepSeek（在命令行运行上面的curl命令）
   # 或
   # 测试豆包（在命令行运行上面的curl命令）
   ```

2. **根据测试结果配置**：
   - 如果DeepSeek可用 → 更新密钥后使用方案1
   - 如果豆包可用 → 使用方案2

3. **运行系统测试**：
   ```bash
   python test_deepseek_api.py
   ```

4. **启动应用**：
   ```bash
   python app.py
   ```

## 常见问题

### Q: API密钥从哪里获取？
**DeepSeek**: https://platform.deepseek.com/api_keys
**豆包**: https://console.volcengine.com/ark

### Q: 如何知道我的API有没有额度？
访问对应平台的控制台查看账户余额和使用情况。

### Q: 两个API有什么区别？
- **DeepSeek**: 专注于深度学习，中文优化好，价格实惠
- **豆包(Doubao)**: 字节跳动的大模型，支持推理模式

### Q: 推荐使用哪个？
两者都可以，建议先测试哪个API可用，然后选择可用的那个。

## 需要帮助？

如果遇到问题，请提供以下信息：
1. 运行 `python test_deepseek_api.py` 的完整输出
2. 您使用的是哪个API平台（DeepSeek/豆包）
3. API密钥是否是新创建的
