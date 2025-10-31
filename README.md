# 英语作文自动批改系统

一个基于Web的英语作文自动批改系统，可以上传PDF文档，自动识别学生作文，并根据评分标准进行逐句批改，生成Word批改文档。

## 功能特点

- ✅ PDF文档上传（支持拖拽）
- ✅ 自动识别多篇作文
- ✅ 根据评分标准进行批改
- ✅ 逐句错误检测和纠正
- ✅ 生成详细的Word批改文档
- ✅ 提供改善建议

## 安装步骤

### 1. 克隆项目

```bash
git clone <repository-url>
cd essay-grading
```

### 2. 安装Python依赖

```bash
pip install -r requirements.txt
```

### 3. 配置DeepSeek API（必需）

系统必须配置DeepSeek API才能使用，不提供简化批改功能。

方式一：使用环境变量
```bash
export DEEPSEEK_API_KEY='your-deepseek-api-key'
```

方式二：创建 `.env` 文件
```bash
cp .env.example .env
# 然后编辑 .env 文件，填入你的API密钥
```

`.env` 文件内容示例：
```
DEEPSEEK_API_KEY=sk-your-actual-api-key-here
```

获取DeepSeek API密钥：访问 [DeepSeek Platform](https://platform.deepseek.com/api_keys)

**注意**：
- 系统必须配置DeepSeek API密钥才能使用
- DeepSeek API与OpenAI API兼容，使用相同的SDK
- 未配置API密钥时，系统将无法批改作文

### 4. 运行应用

```bash
python app.py
```

应用将在 `http://localhost:5000` 启动。

## 使用方法

1. 在浏览器中打开 `http://localhost:5000`
2. 点击上传区域或拖拽PDF文件
3. 系统会自动识别作文数量
4. 点击"开始批改"按钮
5. 等待处理完成（根据作文数量和长度，可能需要几分钟）
6. 下载生成的Word批改文档

## 项目结构

```
essay-grading/
├── app.py                    # Flask后端主程序
├── templates/
│   └── index.html           # 前端页面
├── requirements.txt         # Python依赖
├── .env.example             # 环境变量模板
├── .gitignore              # Git忽略文件
├── 应用文评分标准.docx      # 评分标准文档（可选）
├── uploads/                 # 临时上传文件夹
│   └── .gitkeep
└── outputs/                 # 生成的Word文档
    └── .gitkeep
```

## 技术栈

- **后端**: Flask (Python 3.7+)
- **前端**: HTML5, CSS3, JavaScript (ES6+)
- **PDF处理**: PyPDF2
- **Word处理**: python-docx
- **AI批改**: DeepSeek API（必需）

## DeepSeek API优势

- ✅ 与OpenAI API完全兼容，使用相同的SDK
- ✅ 性价比更高，价格更实惠
- ✅ 支持中文优化，批改效果更佳
- ✅ 响应速度快，稳定性好

参考文档：https://api-docs.deepseek.com/zh-cn/

## 评分标准

系统支持自定义评分标准。如果项目根目录存在 `应用文评分标准.docx` 文件，系统会自动加载其中的评分标准。

默认评分标准：
1. **内容完整性（25分）**：是否包含所有要求的要点
2. **语法准确性（25分）**：语法错误的数量和严重程度
3. **词汇使用（25分）**：词汇的准确性和丰富性
4. **组织结构（15分）**：文章结构是否清晰、连贯
5. **格式规范（10分）**：是否符合应用文格式要求

## 注意事项

1. **必须配置DeepSeek API**：系统必须配置DeepSeek API密钥才能使用
2. PDF文件需要包含可提取的文本内容（不是扫描图片）
3. 如果PDF是扫描件，需要先使用OCR工具提取文本
4. 评分标准文档 `应用文评分标准.docx` 是可选的，如果不存在会使用默认标准
5. 系统会自动识别多篇作文，识别方式：
   - 通过多个连续空行分割
   - 通过学号、姓名等标识分割
6. 单个PDF文件最大支持16MB

## 自定义批改逻辑

可以在 `app.py` 中修改以下函数来自定义批改逻辑：

- `identify_essays()`: 作文识别逻辑（app.py:67）
- `check_essay_with_ai()`: DeepSeek API批改逻辑，包括提示词和参数（app.py:123）
- `create_word_report()`: Word报告生成逻辑（app.py:201）

## API端点

- `GET /` - 主页
- `POST /upload` - 上传PDF文件
- `POST /grade` - 批改作文
- `GET /download/<filename>` - 下载批改报告
- `GET /health` - 健康检查

## 故障排除

### 问题：系统提示"未配置DeepSeek API密钥"
**解决方案**：确保已正确配置 `.env` 文件或设置环境变量 `DEEPSEEK_API_KEY`

### 问题：PDF无法提取文本
**解决方案**：检查PDF是否为扫描件，如是，需要先进行OCR处理

### 问题：作文识别数量不正确
**解决方案**：调整 `app.py` 中 `identify_essays()` 函数的识别逻辑

### 问题：批改时间过长
**解决方案**：
- DeepSeek API调用需要时间，请耐心等待
- 可以在 `check_essay_with_ai()` 中调整 `max_tokens` 参数

## 开发计划

- [ ] 支持更多文档格式（DOCX输入）
- [ ] 支持OCR自动识别扫描件
- [ ] 批量批改优化
- [ ] 自定义评分标准UI
- [ ] 批改历史记录
- [ ] 用户账号系统

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！

## 联系方式

如有问题或建议，请通过GitHub Issues联系。
