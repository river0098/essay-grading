# 快速开始指南

## ⚠️ 当前状态

测试了两个DeepSeek API密钥，都返回 **403 Access denied** 错误。

## 🔍 问题分析

可能的原因：
1. **API密钥未激活或已过期**
2. **账户余额不足**
3. **API密钥权限不正确**
4. **需要使用正确的API端点**

## ✅ 推荐解决方案

### 方案1: 获取有效的DeepSeek API密钥

1. **访问DeepSeek控制台**：
   - 网址：https://platform.deepseek.com/
   - 文档：https://api-docs.deepseek.com/zh-cn/

2. **检查以下事项**：
   - ✓ 账户是否已注册并登录
   - ✓ 是否有可用余额（可能需要充值）
   - ✓ API密钥是否已创建且处于激活状态
   - ✓ API密钥是否有正确的权限

3. **创建新的API密钥**：
   - 在控制台 → API Keys 页面
   - 点击"创建新密钥"
   - 复制密钥（只显示一次！）
   - 保存到安全位置

4. **更新配置**：
   ```bash
   # 编辑 .env 文件
   nano .env

   # 更新为新密钥
   DEEPSEEK_API_KEY=your-new-key-here
   ```

5. **测试连接**：
   ```bash
   python test_deepseek_api.py
   ```

### 方案2: 使用豆包(Doubao) API（备选）

如果DeepSeek API不可用，可以使用豆包API：

1. **获取豆包API密钥**：
   - 访问：https://console.volcengine.com/ark
   - 注册并创建API密钥

2. **配置豆包API**：
   ```bash
   # 编辑 .env 文件
   nano .env

   # 添加豆包配置（会自动优先使用）
   DOUBAO_API_KEY=your-doubao-key
   DOUBAO_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
   DOUBAO_MODEL=doubao-seed-1-6-251015
   ```

3. **测试运行**：
   ```bash
   python app.py
   ```

### 方案3: 使用其他OpenAI兼容的API

系统支持任何OpenAI兼容的API，您可以配置：
- OpenAI官方API
- Azure OpenAI
- 国内其他大模型API（如阿里通义千问、智谱AI等）

## 🚀 立即开始

### 步骤1: 安装依赖

```bash
pip install -r requirements.txt
```

### 步骤2: 配置API密钥

选择以下任一方式：

#### 方式A: 使用.env文件（推荐）
```bash
# 创建 .env 文件
cp .env.example .env

# 编辑并添加你的API密钥
nano .env
```

#### 方式B: 使用环境变量
```bash
export DEEPSEEK_API_KEY='your-key-here'
# 或
export DOUBAO_API_KEY='your-key-here'
```

### 步骤3: 测试API

```bash
# 测试API连接
python test_deepseek_api.py

# 测试PDF提取
python test_pdf_extraction.py sample.pdf
```

### 步骤4: 运行应用

```bash
# 启动应用
python app.py

# 访问浏览器
# http://localhost:5000
```

## 📝 完整的配置文件示例

创建 `.env` 文件，内容如下：

```bash
# 选项1: 使用DeepSeek API
DEEPSEEK_API_KEY=sk-your-deepseek-key

# 选项2: 使用豆包API（如果配置，将优先使用）
# DOUBAO_API_KEY=your-doubao-key
# DOUBAO_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
# DOUBAO_MODEL=doubao-seed-1-6-251015

# 选项3: 使用OpenAI API
# DEEPSEEK_API_KEY=sk-your-openai-key
# 然后修改 app.py 中的 base_url 为 https://api.openai.com/v1
```

## 🔧 验证配置

运行健康检查：

```bash
# 方法1: 使用测试脚本
python test_deepseek_api.py

# 方法2: 启动应用后访问健康检查端点
curl http://localhost:5000/health
```

成功的响应示例：
```json
{
  "status": "ok",
  "api_configured": true,
  "api_provider": "DeepSeek",
  "api_model": "deepseek-chat"
}
```

## ❓ 常见问题

### Q1: 我没有API密钥怎么办？
**答**：您需要注册以下任一平台并获取API密钥：
- DeepSeek: https://platform.deepseek.com
- 豆包: https://console.volcengine.com/ark
- OpenAI: https://platform.openai.com

### Q2: API密钥如何收费？
**答**：
- **DeepSeek**: 按token使用量计费，价格较低
- **豆包**: 按请求计费，有免费额度
- **OpenAI**: 按token计费，相对较贵

每次批改大约消耗500-2000 tokens，成本约0.01-0.05元人民币。

### Q3: 可以在没有API密钥的情况下测试系统吗？
**答**：不可以。AI批改功能是核心功能，必须配置API密钥。但您可以测试PDF提取功能：
```bash
python test_pdf_extraction.py your_file.pdf
```

### Q4: 测试脚本一直提示 Access denied？
**答**：这说明API密钥无效。请：
1. 确认密钥是从官方平台复制的
2. 检查账户是否有余额
3. 尝试创建新的API密钥
4. 联系API提供商的客服支持

## 📚 更多资源

- **完整文档**: README.md
- **API配置详细说明**: API_SETUP.md
- **PDF提取问题**: README.md (故障排除章节)
- **DeepSeek文档**: https://api-docs.deepseek.com/zh-cn/

## 💡 下一步

1. ✅ 获取有效的API密钥
2. ✅ 配置到 .env 文件
3. ✅ 运行测试脚本验证
4. ✅ 启动应用并测试批改功能

有任何问题，请查看 API_SETUP.md 获取更详细的说明。
