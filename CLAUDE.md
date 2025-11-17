# CLAUDE.md - AI Assistant Guide for Essay Grading System

This document provides comprehensive guidance for AI assistants working with the English Essay Automated Grading System codebase.

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Codebase Structure](#codebase-structure)
- [Key Architectural Patterns](#key-architectural-patterns)
- [Development Workflows](#development-workflows)
- [Code Conventions](#code-conventions)
- [Testing Strategy](#testing-strategy)
- [Common Tasks](#common-tasks)
- [Important Constraints](#important-constraints)
- [Troubleshooting Guide](#troubleshooting-guide)

---

## 📖 Project Overview

**Name**: English Essay Automated Grading System (英语作文自动批改系统)
**Type**: Flask-based web application
**Primary Language**: Python 3.7+
**Purpose**: Automated grading of English essays using AI, with PDF upload, multi-essay recognition, and Word report generation

### Core Functionality
1. PDF upload and text extraction (3-tier fallback strategy)
2. Multi-essay identification and segmentation
3. AI-powered grading using DeepSeek or Doubao APIs
4. Professional Word document report generation
5. 5-dimensional scoring system with detailed feedback

---

## 🏗️ Codebase Structure

```
essay-grading/
├── app.py (566 lines)                    # Main Flask application - CRITICAL FILE
├── test_doubao_api.py (215 lines)        # Doubao API testing utility
├── test_deepseek_api.py (198 lines)      # DeepSeek API testing utility
├── test_pdf_extraction.py (187 lines)    # PDF extraction diagnostic tool
├── create_criteria.py (41 lines)         # Grading criteria document generator
├── verify_setup.sh (128 lines)           # System verification script
├── templates/
│   └── index.html (523 lines)            # Single-page web application
├── uploads/                              # Temporary PDF storage (auto-created)
├── outputs/                              # Generated Word reports (auto-created)
├── requirements.txt                      # Python dependencies (9 packages)
├── .env                                  # API credentials (git-ignored)
├── .env.example                          # Environment template
├── 应用文评分标准.docx                    # Grading criteria (optional, Chinese)
└── Documentation/
    ├── README.md                         # Main documentation (Chinese)
    ├── API_SETUP.md                      # API configuration guide
    ├── QUICK_START.md                    # Quick start guide
    └── CURRENT_SETUP.md                  # Current system status
```

### File Importance Matrix

| File | Criticality | Modify Frequency | Dependencies |
|------|-------------|------------------|--------------|
| `app.py` | **CRITICAL** | High | Flask, OpenAI, python-docx, pdfplumber |
| `index.html` | High | Medium | None (standalone) |
| `test_*.py` | Medium | Low | OpenAI, PDF libraries |
| `.env` | **CRITICAL** | Low | None (credentials) |
| `requirements.txt` | High | Low | All Python code |

---

## 🎯 Key Architectural Patterns

### 1. **Three-Tier PDF Extraction (Fallback Pattern)**

**Location**: `app.py:extract_text_from_pdf()` (lines ~47-93)

```python
# Priority order: pdfplumber → pypdfium2 → PyPDF2
# Each method has try-except with detailed logging
```

**Pattern**: Progressive degradation with comprehensive error handling

**Key Points**:
- **pdfplumber** is the primary method (most accurate)
- **pypdfium2** is the secondary fallback
- **PyPDF2** is the last resort
- Each extraction logs character count per page
- All methods preserve text formatting

**When modifying**:
- Test all three methods independently using `test_pdf_extraction.py`
- Log character counts to detect extraction issues
- Never remove fallback methods without replacement

### 2. **Dual API Provider System**

**Location**: `app.py` (lines ~30-62)

```python
# Priority: Doubao (if configured) → DeepSeek (fallback)
if DOUBAO_API_KEY:
    client = OpenAI(api_key=DOUBAO_API_KEY, base_url=DOUBAO_BASE_URL)
    AI_MODEL = DOUBAO_MODEL
elif DEEPSEEK_API_KEY:
    client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")
    AI_MODEL = "deepseek-chat"
```

**Pattern**: Provider abstraction with OpenAI-compatible SDK

**Key Points**:
- Both providers use the same `openai` Python SDK
- Only the `base_url` and `api_key` differ
- Model names are provider-specific
- Graceful degradation if no API configured

**When adding new providers**:
1. Add environment variables in `.env.example`
2. Update client initialization logic
3. Create corresponding test script (`test_<provider>_api.py`)
4. Update documentation (README.md, API_SETUP.md)

### 3. **Multi-Essay Segmentation**

**Location**: `app.py:identify_essays()` (lines ~95-121)

**Strategy**: Dual recognition methods
1. **Method 1**: Multi-line breaks (`\n\s*\n\s*\n`)
2. **Method 2**: Identifier patterns (学号/姓名/Student ID/Name)

**Validation**: Minimum 100 characters per essay

**Important**: This logic is fragile and may need adjustment based on PDF formatting

### 4. **JSON-Based AI Response Parsing**

**Location**: `app.py:check_essay_with_ai()` (lines ~164-249)

**Pattern**: Structured prompt → JSON parsing with fallback

**Key Components**:
- Temperature: 0.3 (deterministic)
- Max tokens: 4000
- JSON schema enforcement in prompt
- Fallback to raw text if JSON parsing fails

**Critical**: The prompt engineering at lines ~177-208 defines the response structure

---

## 💻 Development Workflows

### Workflow 1: Adding a New Feature

**Standard Process**:

1. **Read existing code first**
   ```bash
   # Never modify without reading
   Read: app.py, relevant test files, documentation
   ```

2. **Test current functionality**
   ```bash
   python app.py  # Verify it works before changes
   bash verify_setup.sh  # Run full system check
   ```

3. **Make incremental changes**
   - Modify one component at a time
   - Preserve existing error handling patterns
   - Add logging statements for debugging

4. **Test thoroughly**
   ```bash
   # Test relevant component
   python test_pdf_extraction.py sample.pdf
   python test_doubao_api.py
   ```

5. **Update documentation**
   - Update README.md if user-facing
   - Update this CLAUDE.md if architecture changes
   - Update API_SETUP.md if API-related

### Workflow 2: Debugging PDF Extraction Issues

**Step-by-step diagnostic**:

1. **Run diagnostic tool**
   ```bash
   python test_pdf_extraction.py problem.pdf
   ```

2. **Check server logs**
   - Look for "提取的字符数" (character count) messages
   - Identify which extraction method succeeded

3. **Use debug endpoint**
   ```
   http://localhost:5000/debug/filename.pdf
   ```

4. **Common fixes**:
   - Scanned PDFs → Need OCR (out of scope)
   - Encrypted PDFs → Remove protection first
   - Encoding issues → Try different extraction method

### Workflow 3: API Configuration Changes

**Safe modification process**:

1. **Update .env file**
   ```bash
   cp .env .env.backup  # Always backup first
   nano .env
   ```

2. **Test API connectivity**
   ```bash
   python test_doubao_api.py
   # or
   python test_deepseek_api.py
   ```

3. **If adding new provider**:
   - Modify `app.py` lines 30-62 (API initialization)
   - Modify `app.py` lines 164-249 (grading function)
   - Create `test_<provider>_api.py`
   - Update `.env.example`

4. **Verify with health check**
   ```bash
   python app.py &
   curl http://localhost:5000/health
   ```

---

## 📐 Code Conventions

### Python Code Style

**Current Style** (be consistent):
- **Indentation**: 4 spaces (not tabs)
- **String quotes**: Single quotes for strings, double for JSON/messages
- **Line length**: ~80-100 characters (not strictly enforced)
- **Comments**: Chinese comments in code, English in git commits

**Function Naming**:
- Snake_case: `extract_text_from_pdf()`, `check_essay_with_ai()`
- Descriptive names that indicate action

**Error Handling Pattern**:
```python
try:
    # Attempt operation
    result = risky_operation()
    app.logger.info(f"Success: {details}")
    return result
except SpecificException as e:
    app.logger.error(f"Failed: {str(e)}")
    # Attempt fallback or return graceful error
    return fallback_method()
```

**Logging Pattern** (IMPORTANT):
```python
# Use app.logger throughout app.py
app.logger.info("Informational message")
app.logger.warning("Warning message")
app.logger.error("Error message with details")

# Always log:
# - API calls (start and completion)
# - PDF extraction attempts and results
# - Essay count recognition
# - File operations
```

### Frontend Conventions

**JavaScript Style** (index.html):
- Modern ES6+ syntax (arrow functions, async/await)
- No external frameworks (vanilla JS)
- Error messages in Chinese (user-facing)
- Progressive enhancement

**API Communication**:
```javascript
// Always use fetch with error handling
const response = await fetch('/endpoint', {
    method: 'POST',
    body: formData
});
const data = await response.json();
// Always check response.ok before proceeding
```

---

## 🧪 Testing Strategy

### Test File Purposes

| Test File | Purpose | When to Run |
|-----------|---------|-------------|
| `verify_setup.sh` | **Full system check** | First setup, major changes |
| `test_doubao_api.py` | Doubao API connectivity | After API config changes |
| `test_deepseek_api.py` | DeepSeek API connectivity | After API config changes |
| `test_pdf_extraction.py` | PDF extraction diagnosis | PDF upload issues |

### Testing Checklist for Code Changes

**Before committing changes to app.py**:

- [ ] Run `python app.py` and verify startup without errors
- [ ] Test `/health` endpoint returns correct status
- [ ] Upload a sample PDF and verify text extraction
- [ ] Test essay recognition with known multi-essay PDF
- [ ] Verify grading produces Word document
- [ ] Check all error messages are user-friendly
- [ ] Ensure logging is comprehensive

**Before committing API changes**:

- [ ] Run appropriate `test_*_api.py` script
- [ ] Verify token usage is logged
- [ ] Test with actual essay grading request
- [ ] Check JSON response parsing works
- [ ] Ensure fallback to raw text works

**Before committing frontend changes**:

- [ ] Test in modern browser (Chrome/Firefox)
- [ ] Verify drag-and-drop upload works
- [ ] Test error message display
- [ ] Confirm progress indicators appear
- [ ] Check download links function correctly

---

## 🔧 Common Tasks

### Task 1: Adding a New Grading Criterion

**Files to modify**:
1. `app.py:load_grading_criteria()` - Add new criterion to defaults
2. `create_criteria.py` - Update template generator
3. `应用文评分标准.docx` - Add to document (or regenerate)

**Code location**: `app.py` lines ~123-162

**Pattern**:
```python
criteria_text += """
6. 新标准名称（权重分）：
   - 标准描述
   - 评分细则
"""
```

**Testing**: Run full grading cycle, verify new criterion appears in output

### Task 2: Adjusting Essay Segmentation Logic

**File**: `app.py:identify_essays()`

**Current logic** (lines ~95-121):
- Method 1: Split on `\n\s*\n\s*\n` (3+ line breaks)
- Method 2: Split on identifier patterns

**To modify**:
1. Adjust regex patterns
2. Test with `test_pdf_extraction.py` to see raw text
3. Adjust minimum character threshold (currently 100)

**Testing**:
```bash
# Upload PDF via web interface
# Check essay count matches expectation
# Use /debug/filename.pdf to see segmentation
```

### Task 3: Changing AI Model Parameters

**File**: `app.py:check_essay_with_ai()`

**Adjustable parameters** (line ~220):
```python
response = client.chat.completions.create(
    model=AI_MODEL,
    messages=[...],
    temperature=0.3,      # ← Modify for creativity (0.0-2.0)
    max_tokens=4000,      # ← Modify for response length
    top_p=1.0,           # ← Modify for nucleus sampling
    frequency_penalty=0,  # ← Add to reduce repetition
    presence_penalty=0    # ← Add to encourage diversity
)
```

**Impact**:
- **Temperature** ↑ = More creative/variable grading
- **Temperature** ↓ = More consistent/strict grading
- **max_tokens** ↑ = Longer responses (costs more)

**Test after changes**: Run `test_doubao_api.py` to verify

### Task 4: Modifying Word Report Format

**File**: `app.py:create_word_report()`

**Location**: Lines ~251-326

**Current structure**:
1. Overall score (large, blue)
2. Dimensional scores table
3. Sentence-by-sentence corrections (red errors, green fixes)
4. Comments section
5. Suggestions section
6. Original text

**Color coding**:
```python
from docx.shared import RGBColor
red = RGBColor(255, 0, 0)      # Errors
green = RGBColor(0, 128, 0)    # Corrections
blue = RGBColor(0, 0, 255)     # Scores
```

**To add new section**:
```python
doc.add_heading('新章节标题', level=2)
para = doc.add_paragraph('内容')
para.runs[0].font.color.rgb = RGBColor(r, g, b)
```

### Task 5: Adding New API Provider

**Step-by-step guide**:

1. **Add environment variables** (`.env.example`):
   ```bash
   NEWPROVIDER_API_KEY=your-key
   NEWPROVIDER_BASE_URL=https://api.provider.com/v1
   NEWPROVIDER_MODEL=model-name
   ```

2. **Modify app.py initialization** (lines ~30-62):
   ```python
   NEWPROVIDER_API_KEY = os.getenv('NEWPROVIDER_API_KEY')
   NEWPROVIDER_BASE_URL = os.getenv('NEWPROVIDER_BASE_URL')
   NEWPROVIDER_MODEL = os.getenv('NEWPROVIDER_MODEL')

   if NEWPROVIDER_API_KEY:
       client = OpenAI(
           api_key=NEWPROVIDER_API_KEY,
           base_url=NEWPROVIDER_BASE_URL
       )
       AI_MODEL = NEWPROVIDER_MODEL
   elif DOUBAO_API_KEY:
       # ... existing code
   ```

3. **Create test script**:
   ```bash
   cp test_doubao_api.py test_newprovider_api.py
   # Modify to use new environment variables
   ```

4. **Update health check** (`app.py:health()`):
   ```python
   api_provider = "NewProvider" if NEWPROVIDER_API_KEY else ...
   ```

5. **Update documentation**:
   - README.md: Add to "技术栈" and "API配置" sections
   - API_SETUP.md: Add configuration guide
   - CURRENT_SETUP.md: Update current status

---

## ⚠️ Important Constraints

### Critical Files - Modify with Caution

**app.py**:
- Lines 30-62: API initialization (breaks entire app if wrong)
- Lines 47-93: PDF extraction (fragile, affects all uploads)
- Lines 164-249: AI grading logic (affects output quality)
- Lines 251-326: Word generation (affects final output)

**Always test thoroughly after modifying these sections**

### Do NOT Modify Without Reason

1. **uploads/ and outputs/ directory names**: Hard-coded in multiple places
2. **Flask route paths**: Frontend JavaScript depends on exact paths
3. **JSON response structure**: Frontend parsing depends on exact keys
4. **Environment variable names**: Used in multiple files

### Configuration Files

**.env file**:
- **Never commit** to git (already in .gitignore)
- Contains sensitive API keys
- Always provide `.env.example` as template

**requirements.txt**:
- Pin major versions for stability
- Test after any dependency updates
- Current versions are known to work together

### API Rate Limits and Costs

**DeepSeek API**:
- Rate limit: ~50 requests/minute (varies by account)
- Cost: ~$0.001-0.002 per essay
- Timeout: 30 seconds per request

**Doubao API**:
- Rate limit: Varies by account tier
- Cost: Token-based pricing
- Timeout: 30 seconds per request

**Implications**:
- Batch processing should include delays
- Handle rate limit errors gracefully
- Log token usage for cost tracking

### File Size Limits

**Current constraints**:
- Max file size: 16MB (set in `app.py`)
- Flask's default: 16MB
- Werkzeug default: 16MB

**To change**:
```python
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32MB
```

**Warning**: Large files may timeout during processing

---

## 🔍 Troubleshooting Guide

### Issue: API Key Not Recognized

**Symptoms**:
- "未配置API密钥" error
- Health check shows `api_configured: false`

**Diagnosis**:
```bash
# Check .env file exists
ls -la .env

# Check environment loading
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('DOUBAO_API_KEY'))"
```

**Solutions**:
1. Verify `.env` file is in project root
2. Check no extra spaces in `.env` file
3. Restart Flask app after `.env` changes
4. Check file is not named `.env.txt` or similar

### Issue: PDF Extraction Returns Empty Text

**Symptoms**:
- Essay count shows 0
- Debug page shows empty or minimal text

**Diagnosis**:
```bash
python test_pdf_extraction.py problem.pdf
```

**Check output for**:
- All three methods return 0 characters → Scanned PDF (needs OCR)
- Some methods work → Use working method exclusively
- Extraction works but app doesn't → Essay segmentation issue

**Solutions**:
1. **Scanned PDF**: Use OCR tool first (out of scope for this app)
2. **Encrypted PDF**: Remove password protection
3. **Method-specific issue**: Force use of working method in app.py
4. **Segmentation issue**: Check `identify_essays()` logic

### Issue: JSON Parsing Fails

**Symptoms**:
- Grading completes but Word doc is malformed
- Logs show "JSON解析失败" messages

**Diagnosis**:
- Check API response in logs
- May be model-specific formatting issue

**Solutions**:
1. **Adjust prompt** (lines ~177-208): Add more JSON format examples
2. **Increase temperature**: May help with consistent formatting
3. **Add response validation**: Parse and fix common JSON errors
4. **Fallback gracefully**: Current code already falls back to raw text

### Issue: Word Document Generation Fails

**Symptoms**:
- Grading succeeds but download fails
- 500 error on `/download/<filename>`

**Diagnosis**:
```bash
# Check outputs directory
ls -la outputs/

# Check permissions
ls -ld outputs/
```

**Solutions**:
1. Verify `outputs/` directory exists and is writable
2. Check disk space: `df -h`
3. Verify python-docx installation: `pip show python-docx`
4. Check for unicode issues in essay text

### Issue: Application Won't Start

**Symptoms**:
- `python app.py` fails immediately
- Import errors or configuration errors

**Diagnosis**:
```bash
# Check Python version
python --version  # Should be 3.7+

# Check dependencies
pip install -r requirements.txt

# Run verification
bash verify_setup.sh
```

**Solutions**:
1. **Missing dependencies**: Run `pip install -r requirements.txt`
2. **Port conflict**: Change port in `app.py` (last line)
3. **Import errors**: Check Python version compatibility
4. **Config errors**: Verify `.env` file format

---

## 📚 Additional Resources

### Key Functions Reference

| Function | Location | Purpose |
|----------|----------|---------|
| `extract_text_from_pdf()` | app.py:47 | Three-tier PDF text extraction |
| `identify_essays()` | app.py:95 | Multi-essay segmentation |
| `load_grading_criteria()` | app.py:123 | Load grading standards |
| `check_essay_with_ai()` | app.py:164 | AI grading API call |
| `create_word_report()` | app.py:251 | Word document generation |

### Flask Routes Reference

| Route | Method | Purpose | Parameters |
|-------|--------|---------|------------|
| `/` | GET | Serve web interface | None |
| `/upload` | POST | Upload PDF, extract text | file (multipart) |
| `/grade` | POST | Grade essays, generate reports | filename (form) |
| `/download/<filename>` | GET | Download Word report | filename (path) |
| `/debug/<filename>` | GET | View extracted text | filename (path) |
| `/health` | GET | System health check | None |

### Environment Variables Reference

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `DOUBAO_API_KEY` | No* | None | Doubao API authentication |
| `DOUBAO_BASE_URL` | No | None | Doubao API endpoint |
| `DOUBAO_MODEL` | No | None | Doubao model name |
| `DEEPSEEK_API_KEY` | No* | None | DeepSeek API authentication |

*At least one API key required for full functionality

### External Documentation

- **Flask**: https://flask.palletsprojects.com/
- **python-docx**: https://python-docx.readthedocs.io/
- **pdfplumber**: https://github.com/jsvine/pdfplumber
- **OpenAI Python SDK**: https://github.com/openai/openai-python
- **DeepSeek API**: https://api-docs.deepseek.com/
- **Doubao API**: https://console.volcengine.com/ark

---

## 🎯 Best Practices for AI Assistants

### When Asked to Modify Code

1. **Always read the relevant file first** - Never modify based on assumptions
2. **Check current configuration** - Run `bash verify_setup.sh` to understand state
3. **Test before and after** - Ensure changes don't break existing functionality
4. **Preserve error handling** - Don't simplify away try-except blocks
5. **Maintain logging** - Add logging for new features, preserve existing logs
6. **Update documentation** - Modify relevant .md files when changing behavior

### When Debugging Issues

1. **Start with diagnostic tools** - Use `test_*.py` scripts before modifying code
2. **Check logs first** - Flask app logs provide detailed information
3. **Isolate the problem** - Test individual components (PDF → extraction → grading → report)
4. **Use debug endpoints** - `/debug/` and `/health` provide runtime information
5. **Verify configuration** - Many issues stem from `.env` misconfiguration

### When Adding Features

1. **Follow existing patterns** - Mimic error handling, logging, and structure
2. **Test incrementally** - Add small pieces and test each one
3. **Consider backward compatibility** - Don't break existing PDFs or workflows
4. **Document thoroughly** - Update CLAUDE.md and user-facing documentation
5. **Add corresponding tests** - Create or update test scripts

---

## 📝 Version History

- **Current Version**: Configured with Doubao API support
- **Key Milestones**:
  - Multi-provider API support (DeepSeek + Doubao)
  - Three-tier PDF extraction
  - Comprehensive testing tools
  - Detailed documentation

---

## 🤝 Contributing Guidelines

When making changes to this codebase:

1. **Test with `verify_setup.sh`** before committing
2. **Update this CLAUDE.md** if architectural changes are made
3. **Maintain backward compatibility** with existing `.env` configurations
4. **Add logging** for new features to aid debugging
5. **Keep documentation in sync** - Update all relevant .md files

---

**Last Updated**: 2025-11-17
**Maintained By**: AI Assistants working with this codebase

For questions about this codebase, refer to:
- README.md (user documentation)
- API_SETUP.md (API configuration)
- This file (development guidance)
