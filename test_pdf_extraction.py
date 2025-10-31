#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PDF文本提取测试工具
用于诊断PDF文本提取问题

使用方法：
python test_pdf_extraction.py <pdf文件路径>
"""

import sys
import os
import PyPDF2
import pdfplumber
import pypdfium2 as pdfium


def test_pypdf2(pdf_path):
    """测试PyPDF2"""
    print("\n" + "="*60)
    print("方法1: PyPDF2")
    print("="*60)
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            print(f"✓ 页数: {len(pdf_reader.pages)}")
            print(f"✓ 是否加密: {pdf_reader.is_encrypted}")

            text = ""
            for i, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                text += page_text
                print(f"  第{i+1}页: {len(page_text)} 个字符")

            print(f"\n总共提取: {len(text)} 个字符")

            if text.strip():
                print("\n前200个字符预览:")
                print("-" * 60)
                print(text[:200])
                print("-" * 60)
                return text
            else:
                print("❌ 提取的文本为空")
                return None

    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        return None


def test_pdfplumber(pdf_path):
    """测试pdfplumber"""
    print("\n" + "="*60)
    print("方法2: pdfplumber（推荐）")
    print("="*60)
    try:
        with pdfplumber.open(pdf_path) as pdf:
            print(f"✓ 页数: {len(pdf.pages)}")

            text = ""
            for i, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
                    print(f"  第{i+1}页: {len(page_text)} 个字符")
                else:
                    print(f"  第{i+1}页: 无文本")

            print(f"\n总共提取: {len(text)} 个字符")

            if text.strip():
                print("\n前200个字符预览:")
                print("-" * 60)
                print(text[:200])
                print("-" * 60)
                return text
            else:
                print("❌ 提取的文本为空")
                return None

    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        return None


def test_pypdfium2(pdf_path):
    """测试pypdfium2"""
    print("\n" + "="*60)
    print("方法3: pypdfium2")
    print("="*60)
    try:
        pdf = pdfium.PdfDocument(pdf_path)
        print(f"✓ 页数: {len(pdf)}")

        text = ""
        for i, page in enumerate(pdf):
            textpage = page.get_textpage()
            page_text = textpage.get_text_range()
            if page_text:
                text += page_text + "\n"
                print(f"  第{i+1}页: {len(page_text)} 个字符")
            else:
                print(f"  第{i+1}页: 无文本")

        pdf.close()

        print(f"\n总共提取: {len(text)} 个字符")

        if text.strip():
            print("\n前200个字符预览:")
            print("-" * 60)
            print(text[:200])
            print("-" * 60)
            return text
        else:
            print("❌ 提取的文本为空")
            return None

    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        return None


def main():
    if len(sys.argv) < 2:
        print("使用方法: python test_pdf_extraction.py <pdf文件路径>")
        sys.exit(1)

    pdf_path = sys.argv[1]

    if not os.path.exists(pdf_path):
        print(f"错误: 文件不存在: {pdf_path}")
        sys.exit(1)

    if not pdf_path.lower().endswith('.pdf'):
        print(f"错误: 不是PDF文件: {pdf_path}")
        sys.exit(1)

    print("="*60)
    print("PDF文本提取测试")
    print("="*60)
    print(f"文件: {pdf_path}")
    print(f"大小: {os.path.getsize(pdf_path)} bytes")

    # 测试三种方法
    results = []
    results.append(("PyPDF2", test_pypdf2(pdf_path)))
    results.append(("pdfplumber", test_pdfplumber(pdf_path)))
    results.append(("pypdfium2", test_pypdfium2(pdf_path)))

    # 总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)

    success_methods = []
    for method, text in results:
        if text and text.strip():
            print(f"✓ {method}: 成功提取 {len(text)} 个字符")
            success_methods.append(method)
        else:
            print(f"❌ {method}: 提取失败或文本为空")

    if success_methods:
        print(f"\n✓ 推荐使用: {success_methods[0]}")

        # 保存最佳结果
        output_file = pdf_path + ".extracted.txt"
        best_text = [text for method, text in results if text and text.strip()][0]
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(best_text)
        print(f"✓ 提取的文本已保存到: {output_file}")
    else:
        print("\n❌ 所有方法都无法提取文本")
        print("\n可能的原因：")
        print("1. PDF是扫描件（图片），需要OCR识别")
        print("2. PDF使用了特殊编码或加密")
        print("3. PDF文件损坏")
        print("\n建议：")
        print("- 在Adobe Reader或浏览器中打开PDF，尝试选择文本")
        print("- 如果无法选择文本，说明是扫描件，需要OCR工具")
        print("- 可以使用在线OCR工具或Adobe Acrobat进行OCR处理")


if __name__ == '__main__':
    main()
