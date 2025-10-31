import os
import re
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import PyPDF2
from docx import Document
from docx.shared import RGBColor, Pt
from docx.enum.text import WD_COLOR_INDEX
from openai import OpenAI
from dotenv import load_dotenv
import json

# 加载环境变量
load_dotenv()

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'

# 确保目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# DeepSeek API配置
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
if not DEEPSEEK_API_KEY:
    print("警告: 未配置DEEPSEEK_API_KEY，系统无法正常工作")

# 初始化DeepSeek客户端（使用OpenAI SDK，但指向DeepSeek API）
client = None
if DEEPSEEK_API_KEY:
    client = OpenAI(
        api_key=DEEPSEEK_API_KEY,
        base_url="https://api.deepseek.com"
    )


def extract_text_from_pdf(pdf_path):
    """从PDF中提取文本"""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
    except Exception as e:
        raise Exception(f"PDF文本提取失败: {str(e)}")


def identify_essays(text):
    """
    识别多篇作文
    假设作文之间有明显的分隔（如多个空行、学号、姓名等）
    """
    # 尝试通过多个换行符分割
    essays = []

    # 方法1: 通过多个连续空行分割
    parts = re.split(r'\n\s*\n\s*\n', text)

    for i, part in enumerate(parts):
        part = part.strip()
        if len(part) > 100:  # 假设作文至少100字符
            essays.append({
                'id': i + 1,
                'content': part
            })

    # 如果只识别到一篇，尝试其他方法
    if len(essays) <= 1:
        # 方法2: 尝试通过学号或姓名模式分割
        pattern = r'(?=学号[:：]|姓名[:：]|Name[:：]|Student ID[:：])'
        parts = re.split(pattern, text)
        essays = []
        for i, part in enumerate(parts):
            part = part.strip()
            if len(part) > 100:
                essays.append({
                    'id': i + 1,
                    'content': part
                })

    # 如果还是只有一篇，就把整个文本作为一篇作文
    if len(essays) == 0:
        essays.append({
            'id': 1,
            'content': text.strip()
        })

    return essays


def load_grading_criteria():
    """加载评分标准"""
    criteria_file = '应用文评分标准.docx'

    # 如果文件不存在，返回默认标准
    if not os.path.exists(criteria_file):
        return """
评分标准：
1. 内容完整性（25分）：是否包含所有要求的要点
2. 语法准确性（25分）：语法错误的数量和严重程度
3. 词汇使用（25分）：词汇的准确性和丰富性
4. 组织结构（15分）：文章结构是否清晰、连贯
5. 格式规范（10分）：是否符合应用文格式要求
"""

    try:
        doc = Document(criteria_file)
        criteria = ""
        for para in doc.paragraphs:
            criteria += para.text + "\n"
        return criteria
    except Exception as e:
        return f"评分标准加载失败: {str(e)}"


def check_essay_with_ai(essay_content, criteria):
    """使用DeepSeek API批改作文"""
    if not client:
        return {
            'success': False,
            'error': '未配置DeepSeek API密钥'
        }

    prompt = f"""你是一位专业的英语作文批改老师。请根据以下评分标准，对学生的英语作文进行详细批改。

评分标准：
{criteria}

学生作文：
{essay_content}

请提供以下内容（使用JSON格式）：
1. 总体评分（满分100分）
2. 各项得分（内容、语法、词汇、结构、格式）
3. 逐句批改（对每个句子指出错误和改进建议）
4. 总体评语和改善建议

JSON格式示例：
{{
    "overall_score": 85,
    "scores": {{
        "content": 22,
        "grammar": 20,
        "vocabulary": 21,
        "structure": 13,
        "format": 9
    }},
    "sentence_corrections": [
        {{
            "original": "原句内容",
            "errors": "错误说明",
            "correction": "修改建议"
        }}
    ],
    "overall_comment": "总体评语",
    "suggestions": "改善建议"
}}
"""

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一位专业的英语作文批改老师，擅长发现语法错误、提供建设性意见。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=4000
        )

        result_text = response.choices[0].message.content

        # 尝试解析JSON
        try:
            # 提取JSON部分（可能被包裹在其他文本中）
            json_match = re.search(r'\{[\s\S]*\}', result_text)
            if json_match:
                result = json.loads(json_match.group())
            else:
                result = json.loads(result_text)
        except json.JSONDecodeError:
            # 如果JSON解析失败，返回原始文本
            result = {
                'raw_response': result_text,
                'overall_score': 0,
                'scores': {},
                'sentence_corrections': [],
                'overall_comment': result_text,
                'suggestions': '请手动查看批改结果'
            }

        return {
            'success': True,
            'result': result
        }

    except Exception as e:
        return {
            'success': False,
            'error': f'API调用失败: {str(e)}'
        }


def create_word_report(essay, grading_result, output_path):
    """生成Word批改报告"""
    doc = Document()

    # 添加标题
    title = doc.add_heading('英语作文批改报告', 0)

    # 添加作文编号
    doc.add_heading(f'作文 #{essay["id"]}', level=1)

    result = grading_result['result']

    # 添加总体评分
    doc.add_heading('总体评分', level=2)
    score_para = doc.add_paragraph()
    score_run = score_para.add_run(f'总分: {result.get("overall_score", "N/A")}/100')
    score_run.font.size = Pt(14)
    score_run.font.bold = True
    score_run.font.color.rgb = RGBColor(0, 112, 192)

    # 添加各项得分
    if 'scores' in result and result['scores']:
        doc.add_heading('各项得分', level=2)
        scores_table = doc.add_table(rows=1, cols=2)
        scores_table.style = 'Light Grid Accent 1'
        header_cells = scores_table.rows[0].cells
        header_cells[0].text = '评分项'
        header_cells[1].text = '得分'

        score_names = {
            'content': '内容完整性',
            'grammar': '语法准确性',
            'vocabulary': '词汇使用',
            'structure': '组织结构',
            'format': '格式规范'
        }

        for key, value in result['scores'].items():
            row_cells = scores_table.add_row().cells
            row_cells[0].text = score_names.get(key, key)
            row_cells[1].text = str(value)

    # 添加逐句批改
    if 'sentence_corrections' in result and result['sentence_corrections']:
        doc.add_heading('逐句批改', level=2)
        for i, correction in enumerate(result['sentence_corrections'], 1):
            doc.add_paragraph(f'句子 {i}:', style='Heading 3')

            # 原句
            original_para = doc.add_paragraph()
            original_para.add_run('原句: ').bold = True
            original_para.add_run(correction.get('original', ''))

            # 错误说明
            if correction.get('errors'):
                error_para = doc.add_paragraph()
                error_run = error_para.add_run('错误: ')
                error_run.bold = True
                error_run.font.color.rgb = RGBColor(192, 0, 0)
                error_para.add_run(correction['errors'])

            # 修改建议
            if correction.get('correction'):
                correction_para = doc.add_paragraph()
                correction_run = correction_para.add_run('修改建议: ')
                correction_run.bold = True
                correction_run.font.color.rgb = RGBColor(0, 176, 80)
                correction_para.add_run(correction['correction'])

            doc.add_paragraph()  # 空行

    # 添加总体评语
    if result.get('overall_comment'):
        doc.add_heading('总体评语', level=2)
        doc.add_paragraph(result['overall_comment'])

    # 添加改善建议
    if result.get('suggestions'):
        doc.add_heading('改善建议', level=2)
        doc.add_paragraph(result['suggestions'])

    # 添加原文
    doc.add_page_break()
    doc.add_heading('原文', level=2)
    doc.add_paragraph(essay['content'])

    # 保存文档
    doc.save(output_path)


@app.route('/')
def index():
    """首页"""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    """处理文件上传"""
    if 'file' not in request.files:
        return jsonify({'error': '没有文件上传'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400

    if not file.filename.endswith('.pdf'):
        return jsonify({'error': '只支持PDF文件'}), 400

    try:
        # 保存上传的文件
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # 提取文本
        text = extract_text_from_pdf(filepath)

        if not text.strip():
            return jsonify({'error': 'PDF文件为空或无法提取文本（可能是扫描件）'}), 400

        # 识别作文
        essays = identify_essays(text)

        return jsonify({
            'success': True,
            'filename': filename,
            'essay_count': len(essays),
            'message': f'成功识别 {len(essays)} 篇作文'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/grade', methods=['POST'])
def grade_essays():
    """批改作文"""
    if not client:
        return jsonify({'error': '未配置DeepSeek API密钥，无法批改作文'}), 500

    data = request.json
    filename = data.get('filename')

    if not filename:
        return jsonify({'error': '缺少文件名'}), 400

    try:
        # 读取PDF文件
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        text = extract_text_from_pdf(filepath)

        # 识别作文
        essays = identify_essays(text)

        # 加载评分标准
        criteria = load_grading_criteria()

        # 批改每篇作文
        results = []
        for essay in essays:
            grading_result = check_essay_with_ai(essay['content'], criteria)

            if grading_result['success']:
                # 生成Word报告
                output_filename = f"批改报告_{filename.replace('.pdf', '')}_{essay['id']}.docx"
                output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)

                create_word_report(essay, grading_result, output_path)

                results.append({
                    'essay_id': essay['id'],
                    'success': True,
                    'output_file': output_filename,
                    'score': grading_result['result'].get('overall_score', 'N/A')
                })
            else:
                results.append({
                    'essay_id': essay['id'],
                    'success': False,
                    'error': grading_result.get('error', '批改失败')
                })

        return jsonify({
            'success': True,
            'results': results
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/download/<filename>')
def download_file(filename):
    """下载批改报告"""
    try:
        filepath = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        return send_file(filepath, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 404


@app.route('/health')
def health_check():
    """健康检查"""
    return jsonify({
        'status': 'ok',
        'deepseek_configured': client is not None
    })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
