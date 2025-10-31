#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
DeepSeek API测试工具
用于验证API密钥是否正确配置并能正常工作

使用方法：
python test_deepseek_api.py
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_api_connection():
    """测试DeepSeek API连接"""
    print("="*60)
    print("DeepSeek API 连接测试")
    print("="*60)

    # 检查API密钥
    api_key = os.getenv('DEEPSEEK_API_KEY')

    if not api_key:
        print("❌ 错误: 未找到DEEPSEEK_API_KEY环境变量")
        print("\n请确保:")
        print("1. .env 文件存在")
        print("2. .env 文件中包含: DEEPSEEK_API_KEY=your-api-key")
        return False

    print(f"✓ API密钥已配置: {api_key[:15]}...")

    # 初始化客户端
    try:
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
        print("✓ OpenAI客户端初始化成功")
    except Exception as e:
        print(f"❌ 客户端初始化失败: {str(e)}")
        return False

    # 测试简单的API调用
    print("\n正在测试API调用...")
    print("-"*60)

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个友好的助手。"},
                {"role": "user", "content": "请用一句话介绍自己。"}
            ],
            max_tokens=100,
            temperature=0.7
        )

        print("✓ API调用成功!")
        print("\nAPI响应:")
        print("-"*60)
        print(response.choices[0].message.content)
        print("-"*60)

        # 显示使用统计
        if hasattr(response, 'usage'):
            print(f"\n使用统计:")
            print(f"  提示词tokens: {response.usage.prompt_tokens}")
            print(f"  完成tokens: {response.usage.completion_tokens}")
            print(f"  总tokens: {response.usage.total_tokens}")

        return True

    except Exception as e:
        print(f"❌ API调用失败: {str(e)}")
        print("\n可能的原因:")
        print("1. API密钥无效或已过期")
        print("2. 网络连接问题")
        print("3. API服务暂时不可用")
        print("\n请检查:")
        print("- API密钥是否正确")
        print("- 是否有网络连接")
        print("- 访问 https://platform.deepseek.com 查看账户状态")
        return False


def test_essay_grading():
    """测试作文批改功能"""
    print("\n" + "="*60)
    print("作文批改功能测试")
    print("="*60)

    api_key = os.getenv('DEEPSEEK_API_KEY')
    if not api_key:
        print("❌ 跳过: API密钥未配置")
        return False

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com"
    )

    # 测试作文示例
    test_essay = """
Dear Sir/Madam,

I am writing to apply for the position of Marketing Manager. I have five years experience in marketing field and I believe I am suitable for this job.

I graduated from Beijing University in 2018. During my study, I learned many knowledge about marketing and business. After graduation, I worked in ABC Company as a marketing specialist.

I am looking forward to hear from you soon.

Yours sincerely,
Zhang Wei
"""

    print("\n测试作文:")
    print("-"*60)
    print(test_essay)
    print("-"*60)

    print("\n正在批改作文（这可能需要10-30秒）...")

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {
                    "role": "system",
                    "content": "你是一位专业的英语作文批改老师。"
                },
                {
                    "role": "user",
                    "content": f"""请批改以下英语应用文，指出语法错误和改进建议。

作文：
{test_essay}

请简要指出3-5个主要问题。"""
                }
            ],
            max_tokens=1000,
            temperature=0.3
        )

        print("✓ 批改完成!")
        print("\n批改结果:")
        print("="*60)
        print(response.choices[0].message.content)
        print("="*60)

        print(f"\n使用tokens: {response.usage.total_tokens}")

        return True

    except Exception as e:
        print(f"❌ 批改失败: {str(e)}")
        return False


def main():
    """主函数"""
    print("\n🤖 DeepSeek API 测试工具\n")

    # 测试1: API连接
    connection_ok = test_api_connection()

    if not connection_ok:
        print("\n" + "="*60)
        print("总结: API连接测试失败")
        print("="*60)
        return

    # 测试2: 作文批改功能
    grading_ok = test_essay_grading()

    # 总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)

    if connection_ok and grading_ok:
        print("✓ 所有测试通过!")
        print("✓ DeepSeek API配置正确，可以正常使用")
        print("\n您现在可以运行主应用:")
        print("  python app.py")
    elif connection_ok:
        print("✓ API连接正常")
        print("⚠ 作文批改测试失败，但基本功能应该可用")
    else:
        print("❌ API配置有问题，请检查后重试")


if __name__ == '__main__':
    main()
