#!/bin/bash
# 英语作文批改系统 - 配置验证脚本
# 用于验证系统是否正确配置并可以运行

echo "========================================"
echo "英语作文批改系统 - 配置验证"
echo "========================================"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查Python
echo "1. 检查Python环境..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓${NC} Python已安装: $PYTHON_VERSION"
else
    echo -e "${RED}✗${NC} Python未安装"
    exit 1
fi
echo ""

# 检查pip
echo "2. 检查pip..."
if command -v pip &> /dev/null || command -v pip3 &> /dev/null; then
    echo -e "${GREEN}✓${NC} pip已安装"
else
    echo -e "${RED}✗${NC} pip未安装"
    exit 1
fi
echo ""

# 检查.env文件
echo "3. 检查.env配置文件..."
if [ -f .env ]; then
    echo -e "${GREEN}✓${NC} .env文件存在"

    # 检查API密钥
    if grep -q "DOUBAO_API_KEY=d0f9bb92" .env; then
        echo -e "${GREEN}✓${NC} 豆包API密钥已配置"
    elif grep -q "DEEPSEEK_API_KEY=" .env && ! grep -q "DEEPSEEK_API_KEY=your" .env; then
        echo -e "${GREEN}✓${NC} DeepSeek API密钥已配置"
    else
        echo -e "${YELLOW}⚠${NC} 未检测到有效的API密钥"
        echo "  请编辑.env文件并配置API密钥"
    fi
else
    echo -e "${RED}✗${NC} .env文件不存在"
    echo "  请运行: cp .env.example .env"
    echo "  然后编辑.env文件配置API密钥"
    exit 1
fi
echo ""

# 检查依赖
echo "4. 检查Python依赖..."
if python3 -c "import flask, PyPDF2, pdfplumber, docx, openai, dotenv" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} 所有依赖已安装"
else
    echo -e "${YELLOW}⚠${NC} 部分依赖未安装"
    echo "  正在安装依赖..."
    pip install -q -r requirements.txt
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC} 依赖安装完成"
    else
        echo -e "${RED}✗${NC} 依赖安装失败"
        exit 1
    fi
fi
echo ""

# 检查目录
echo "5. 检查必要目录..."
for dir in uploads outputs templates; do
    if [ -d "$dir" ]; then
        echo -e "${GREEN}✓${NC} $dir/ 目录存在"
    else
        echo -e "${YELLOW}⚠${NC} $dir/ 目录不存在，正在创建..."
        mkdir -p "$dir"
    fi
done
echo ""

# 测试API
echo "6. 测试API连接..."
echo "  正在运行豆包API测试..."
echo ""
python3 test_doubao_api.py
API_TEST_RESULT=$?
echo ""

if [ $API_TEST_RESULT -eq 0 ]; then
    echo -e "${GREEN}✓${NC} API测试通过"
else
    echo -e "${YELLOW}⚠${NC} API测试未完全通过，但系统可能仍然可用"
    echo "  请查看上面的输出了解详情"
fi
echo ""

# 总结
echo "========================================"
echo "验证总结"
echo "========================================"
echo ""
echo "系统状态检查完成！"
echo ""
echo "下一步操作："
echo "1. 如果所有检查都通过，运行:"
echo "   ${GREEN}python app.py${NC}"
echo ""
echo "2. 然后在浏览器访问:"
echo "   ${GREEN}http://localhost:5000${NC}"
echo ""
echo "3. 如果API测试失败，请:"
echo "   - 检查.env文件中的API密钥是否正确"
echo "   - 访问 https://console.volcengine.com/ark 确认账户状态"
echo "   - 查看 API_SETUP.md 获取详细配置说明"
echo ""
echo "其他有用的命令："
echo "  - 测试PDF提取: ${GREEN}python test_pdf_extraction.py your_file.pdf${NC}"
echo "  - 测试豆包API: ${GREEN}python test_doubao_api.py${NC}"
echo "  - 查看文档: ${GREEN}cat QUICK_START.md${NC}"
echo ""
