# 技能撰寫最佳實務

> 了解如何撰寫能讓代理發現並成功使用的有效技能。

好的技能簡潔、結構良好，並以真實使用情境測試過。本指南提供實務的撰寫決策，幫助你寫出代理能發現並有效使用的技能。

關於技能運作方式的背景概念，請見 [技能總覽](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)。

## 核心原則

### 簡潔是關鍵

[上下文視窗](https://platform.claude.com/docs/en/build-with-claude/context-windows)是公共財。你的技能與代理需要知道的所有其他事物共享上下文視窗，包括：

* System prompt
* 對話歷史
* 其他技能的 metadata
* 你實際的請求

並非技能中的每個 token 都有立即成本。啟動時，只會預先載入所有技能的 metadata（name 與 description）。代理只在技能變得相關時才會讀取 SKILL.md，而且只在需要時讀取其他檔案。不過，讓 SKILL.md 保持簡潔仍然重要：一旦代理載入它，每個 token 都會與對話歷史及其他上下文競爭。

**預設假設**：代理已經非常聰明

只加入代理尚未擁有的上下文。質疑每一則資訊：

* 「代理真的需要這個解釋嗎？」
* 「我能假設代理已經知道這個嗎？」
* 「這段文字值得它的 token 成本嗎？」

**好範例：簡潔**（約 50 tokens）：

````markdown  theme={null}
## Extract PDF text

Use pdfplumber for text extraction:

```python
import pdfplumber

with pdfplumber.open("file.pdf") as pdf:
    text = pdf.pages[0].extract_text()
```
````

**壞範例：過於冗長**（約 150 tokens）：

```markdown  theme={null}
## Extract PDF text

PDF (Portable Document Format) files are a common file format that contains
text, images, and other content. To extract text from a PDF, you'll need to
use a library. There are many libraries available for PDF processing, but we
recommend pdfplumber because it's easy to use and handles most cases well.
First, you'll need to install it using pip. Then you can use the code below...
```

簡潔版本假設代理知道什麼是 PDF，以及函式庫如何運作。

### 設定適當的自由度

讓具體程度對應任務的脆弱性與變異性。

**高自由度**（文字式指令）：

使用時機：

* 多種做法都成立
* 決策取決於上下文
* 以啟發式方法引導做法

範例：

```markdown  theme={null}
## Code review process

1. Analyze the code structure and organization
2. Check for potential bugs or edge cases
3. Suggest improvements for readability and maintainability
4. Verify adherence to project conventions
```

**中自由度**（帶參數的虛擬碼或腳本）：

使用時機：

* 存在偏好的模式
* 允許一定程度的變異
* 設定會影響行為

範例：

````markdown  theme={null}
## Generate report

Use this template and customize as needed:

```python
def generate_report(data, format="markdown", include_charts=True):
    # Process data
    # Generate output in specified format
    # Optionally include visualizations
```
````

**低自由度**（特定腳本，極少或沒有參數）：

使用時機：

* 操作脆弱且容易出錯
* 一致性至關重要
* 必須遵循特定順序

範例：

````markdown  theme={null}
## Database migration

Run exactly this script:

```bash
python scripts/migrate.py --verify --backup
```

Do not modify the command or add additional flags.
````

**類比**：把代理想像成在探索路徑的機器人：

* **兩側都是懸崖的窄橋**：只有一條安全的前進路線。提供具體的護欄與精確指令（低自由度）。範例：必須以精確順序執行的資料庫遷移。
* **沒有危險的開闊平原**：很多路徑都能通往成功。給一般方向，並信任代理找出最佳路線（高自由度）。範例：由上下文決定最佳做法的程式碼審查。

### 用你打算使用的所有模型測試

技能是模型的附加物，因此有效性取決於底層模型。用你打算與技能一起使用的所有模型來測試你的技能。

**各模型的測試考量**：

* **Claude Haiku**（快速、經濟）：技能提供了足夠的指引嗎？
* **Claude Sonnet**（均衡）：技能清楚且有效率嗎？
* **Claude Opus**（強大推理）：技能有沒有過度解釋？

對 Opus 完美的內容，對 Haiku 可能需要更多細節。若你打算在多個模型上使用技能，目標是寫出對它們全部都適用的指令。

## 技能結構

<Note>
  **YAML Frontmatter**：SKILL.md 的 frontmatter 需要兩個欄位：

  * `name` - 技能的人類可讀名稱（最多 64 字元）
  * `description` - 一行描述技能做什麼以及何時使用（最多 1024 字元）

  完整的技能結構細節，請見[技能總覽](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview#skill-structure)。
</Note>

### 命名慣例

使用一致的命名模式，讓技能更容易被引用與討論。我們建議技能名稱採用**動名詞形式**（動詞 + -ing），因為這能清楚描述技能所提供的活動或能力。

**好的命名範例（動名詞形式）**：

* "Processing PDFs"
* "Analyzing spreadsheets"
* "Managing databases"
* "Testing code"
* "Writing documentation"

**可接受的替代方案**：

* 名詞片語："PDF Processing"、"Spreadsheet Analysis"
* 行動導向："Process PDFs"、"Analyze Spreadsheets"

**避免**：

* 含糊的名稱："Helper"、"Utils"、"Tools"
* 過於泛用："Documents"、"Data"、"Files"
* 技能收藏中不一致的模式

一致的命名能讓你更容易：

* 在文件與對話中引用技能
* 一眼看出技能在做什麼
* 組織並搜尋多個技能
* 維護專業、一致的技能庫

### 撰寫有效的 description

`description` 欄位促成技能的探索，應同時包含技能做什麼與何時使用。

<Warning>
  **永遠以第三人稱撰寫**。description 會被注入 system prompt，不一致的人稱可能導致探索問題。

  * **好：**"Processes Excel files and generates reports"
  * **避免：**"I can help you process Excel files"
  * **避免：**"You can use this to process Excel files"
</Warning>

**要具體並包含關鍵詞**。同時包含技能做什麼，以及具體的觸發條件／上下文來說明何時使用。

每個技能恰好只有一個 description 欄位。description 對技能選擇至關重要：代理會用它從可能有 100+ 個可用技能中選出正確的那個。你的 description 必須提供足夠的細節，讓代理知道何時該選擇這個技能，而 SKILL.md 的其餘部分則提供實作細節。

有效的範例：

**PDF 處理技能：**

```yaml  theme={null}
description: Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction.
```

**Excel 分析技能：**

```yaml  theme={null}
description: Analyze Excel spreadsheets, create pivot tables, generate charts. Use when analyzing Excel files, spreadsheets, tabular data, or .xlsx files.
```

**Git Commit Helper 技能：**

```yaml  theme={null}
description: Generate descriptive commit messages by analyzing git diffs. Use when the user asks for help writing commit messages or reviewing staged changes.
```

避免像這樣的含糊 description：

```yaml  theme={null}
description: Helps with documents
```

```yaml  theme={null}
description: Processes data
```

```yaml  theme={null}
description: Does stuff with files
```

### 漸進揭露模式

SKILL.md 作為一個總覽，在需要時把代理引導到詳細資料，就像入門指南中的目錄。關於漸進揭露如何運作的說明，請見總覽中的[技能如何運作](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview#how-skills-work)。

**實務指引：**

* 讓 SKILL.md 本體保持在 500 行以內以獲得最佳效能
* 接近這個上限時，把內容拆到獨立檔案
* 使用下方的模式來有效地組織指令、程式碼與資源

#### 視覺總覽：從簡單到複雜

基礎技能只從一個包含 metadata 與指令的 SKILL.md 檔案開始：

<img src="https://mintcdn.com/anthropic-claude-docs/4Bny2bjzuGBK7o00/images/agent-skills-simple-file.png?fit=max&auto=format&n=4Bny2bjzuGBK7o00&q=85&s=87782ff239b297d9a9e8e1b72ed72db9" alt="Simple SKILL.md file showing YAML frontmatter and markdown body" data-og-width="2048" width="2048" data-og-height="1153" height="1153" data-path="images/agent-skills-simple-file.png" data-optimize="true" data-opv="3" srcset="https://mintcdn.com/anthropic-claude-docs/4Bny2bjzuGBK7o00/images/agent-skills-simple-file.png?w=280&fit=max&auto=format&n=4Bny2bjzuGBK7o00&q=85&s=c61cc33b6f5855809907f7fda94cd80e 280w, https://mintcdn.com/anthropic-claude-docs/4Bny2bjzuGBK7o00/images/agent-skills-simple-file.png?w=560&fit=max&auto=format&n=4Bny2bjzuGBK7o00&q=85&s=90d2c0c1c76b36e8d485f49e0810dbfd 560w, https://mintcdn.com/anthropic-claude-docs/4Bny2bjzuGBK7o00/images/agent-skills-simple-file.png?w=840&fit=max&auto=format&n=4Bny2bjzuGBK7o00&q=85&s=ad17d231ac7b0bea7e5b4d58fb4aeabb 840w, https://mintcdn.com/anthropic-claude-docs/4Bny2bjzuGBK7o00/images/agent-skills-simple-file.png?w=1100&fit=max&auto=format&n=4Bny2bjzuGBK7o00&q=85&s=f5d0a7a3c668435bb0aee9a3a8f8c329 1100w, https://mintcdn.com/anthropic-claude-docs/4Bny2bjzuGBK7o00/images/agent-skills-simple-file.png?w=1650&fit=max&auto=format&n=4Bny2bjzuGBK7o00&q=85&s=0e927c1af9de5799cfe557d12249f6e6 1650w, https://mintcdn.com/anthropic-claude-docs/4Bny2bjzuGBK7o00/images/agent-skills-simple-file.png?w=2500&fit=max&auto=format&n=4Bny2bjzuGBK7o00&q=85&s=46bbb1a51dd4c8202a470ac8c80a893d 2500w" />

隨著技能成長，你可以打包額外內容，讓代理只在需要時載入：

<img src="https://mintcdn.com/anthropic-claude-docs/4Bny2bjzuGBK7o00/images/agent-skills-bundling-content.png?fit=max&auto=format&n=4Bny2bjzuGBK7o00&q=85&s=a5e0aa41e3d53985a7e3e43668a33ea3" alt="Bundling additional reference files like reference.md and forms.md." data-og-width="2048" width="2048" data-og-height="1327" height="1327" data-path="images/agent-skills-bundling-content.png" data-optimize="true" data-opv="3" srcset="https://mintcdn.com/anthropic-claude-docs/4Bny2bjzuGBK7o00/images/agent-skills-bundling-content.png?w=280&fit=max&auto=format&n=4Bny2bjzuGBK7o00&q=85&s=f8a0e73783e99b4a643d79eac86b70a2 280w, https://mintcdn.com/anthropic-claude-docs/4Bny2bjzuGBK7o00/images/agent-skills-bundling-content.png?w=560&fit=max&auto=format&n=4Bny2bjzuGBK7o00&q=85&s=dc510a2a9d3f14359416b706f067904a 560w, https://mintcdn.com/anthropic-claude-docs/4Bny2bjzuGBK7o00/images/agent-skills-bundling-content.png?w=840&fit=max&auto=format&n=4Bny2bjzuGBK7o00&q=85&s=82cd6286c966303f7dd914c28170e385 840w, https://mintcdn.com/anthropic-claude-docs/4Bny2bjzuGBK7o00/images/agent-skills-bundling-content.png?w=1100&fit=max&auto=format&n=4Bny2bjzuGBK7o00&q=85&s=56f3be36c77e4fe4b523df209a6824c6 1100w, https://mintcdn.com/anthropic-claude-docs/4Bny2bjzuGBK7o00/images/agent-skills-bundling-content.png?w=1650&fit=max&auto=format&n=4Bny2bjzuGBK7o00&q=85&s=d22b5161b2075656417d56f41a74f3dd 1650w, https://mintcdn.com/anthropic-claude-docs/4Bny2bjzuGBK7o00/images/agent-skills-bundling-content.png?w=2500&fit=max&auto=format&n=4Bny2bjzuGBK7o00&q=85&s=3dd4bdd6850ffcc96c6c45fcb0acd6eb 2500w" />

完整的技能目錄結構可能看起來像這樣：

```
pdf/
├── SKILL.md              # Main instructions (loaded when triggered)
├── FORMS.md              # Form-filling guide (loaded as needed)
├── reference.md          # API reference (loaded as needed)
├── examples.md           # Usage examples (loaded as needed)
└── scripts/
    ├── analyze_form.py   # Utility script (executed, not loaded)
    ├── fill_form.py      # Form filling script
    └── validate.py       # Validation script
```

#### 模式 1：帶參考文件的高階指南

````markdown  theme={null}
---
name: PDF Processing
description: Extracts text and tables from PDF files, fills forms, and merges documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction.
---

# PDF Processing

## Quick start

Extract text with pdfplumber:
```python
import pdfplumber
with pdfplumber.open("file.pdf") as pdf:
    text = pdf.pages[0].extract_text()
```

## Advanced features

**Form filling**: See [FORMS.md](FORMS.md) for complete guide
**API reference**: See [REFERENCE.md](REFERENCE.md) for all methods
**Examples**: See [EXAMPLES.md](EXAMPLES.md) for common patterns
````

代理只在需要時才載入 FORMS.md、REFERENCE.md 或 EXAMPLES.md。

#### 模式 2：依領域組織

對涵蓋多個領域的技能，依領域組織內容，避免載入不相關的上下文。當使用者問到銷售指標時，代理只需要讀取銷售相關的 schema，而不需要財務或行銷資料。這能讓 token 使用量維持在低點，並讓上下文保持聚焦。

```
bigquery-skill/
├── SKILL.md (overview and navigation)
└── reference/
    ├── finance.md (revenue, billing metrics)
    ├── sales.md (opportunities, pipeline)
    ├── product.md (API usage, features)
    └── marketing.md (campaigns, attribution)
```

````markdown SKILL.md theme={null}
# BigQuery Data Analysis

## Available datasets

**Finance**: Revenue, ARR, billing → See [reference/finance.md](reference/finance.md)
**Sales**: Opportunities, pipeline, accounts → See [reference/sales.md](reference/sales.md)
**Product**: API usage, features, adoption → See [reference/product.md](reference/product.md)
**Marketing**: Campaigns, attribution, email → See [reference/marketing.md](reference/marketing.md)

## Quick search

Find specific metrics using grep:

```bash
grep -i "revenue" reference/finance.md
grep -i "pipeline" reference/sales.md
grep -i "api usage" reference/product.md
```
````

#### 模式 3：條件式細節

顯示基礎內容，連結到進階內容：

```markdown  theme={null}
# DOCX Processing

## Creating documents

Use docx-js for new documents. See [DOCX-JS.md](DOCX-JS.md).

## Editing documents

For simple edits, modify the XML directly.

**For tracked changes**: See [REDLINING.md](REDLINING.md)
**For OOXML details**: See [OOXML.md](OOXML.md)
```

代理只在使用者需要那些功能時，才讀取 REDLINING.md 或 OOXML.md。

### 避免深層巢狀參考

當檔案從其他被參考的檔案被引用時，代理可能會部分讀取檔案。遇到巢狀參考時，代理可能會用 `head -100` 之類的指令預覽內容，而不是讀取整個檔案，導致資訊不完整。

**讓參考與 SKILL.md 保持一層深度**。所有參考檔案都應直接從 SKILL.md 連結，確保代理在需要時能讀到完整檔案。

**壞範例：太深**：

```markdown  theme={null}
# SKILL.md
See [advanced.md](advanced.md)...

# advanced.md
See [details.md](details.md)...

# details.md
Here's the actual information...
```

**好範例：一層深度**：

```markdown  theme={null}
# SKILL.md

**Basic usage**: [instructions in SKILL.md]
**Advanced features**: See [advanced.md](advanced.md)
**API reference**: See [reference.md](reference.md)
**Examples**: See [examples.md](examples.md)
```

### 用目錄結構化較長的參考檔案

對超過 100 行的參考檔案，在頂端加入目錄。這能確保代理即使透過部分讀取預覽，也能看到可用資訊的完整範圍。

**範例**：

```markdown  theme={null}
# API Reference

## Contents
- Authentication and setup
- Core methods (create, read, update, delete)
- Advanced features (batch operations, webhooks)
- Error handling patterns
- Code examples

## Authentication and setup
...

## Core methods
...
```

代理接著可以讀取完整檔案，或視需要跳到特定章節。

關於這種以檔案系統為基礎的架構如何促成漸進揭露，請見下方進階小節中的[執行環境](#執行環境)一節。

## 工作流與回饋迴圈

### 對複雜任務使用工作流

把複雜操作拆成清楚、依序的步驟。對特別複雜的工作流，提供代理可以複製到回應中並隨進度勾選的檢查清單。

**範例 1：研究綜整工作流**（適用於沒有程式碼的技能）：

````markdown  theme={null}
## Research synthesis workflow

Copy this checklist and track your progress:

```
Research Progress:
- [ ] Step 1: Read all source documents
- [ ] Step 2: Identify key themes
- [ ] Step 3: Cross-reference claims
- [ ] Step 4: Create structured summary
- [ ] Step 5: Verify citations
```

**Step 1: Read all source documents**

Review each document in the `sources/` directory. Note the main arguments and supporting evidence.

**Step 2: Identify key themes**

Look for patterns across sources. What themes appear repeatedly? Where do sources agree or disagree?

**Step 3: Cross-reference claims**

For each major claim, verify it appears in the source material. Note which source supports each point.

**Step 4: Create structured summary**

Organize findings by theme. Include:
- Main claim
- Supporting evidence from sources
- Conflicting viewpoints (if any)

**Step 5: Verify citations**

Check that every claim references the correct source document. If citations are incomplete, return to Step 3.
````

這個範例展示了工作流如何套用於不需要程式碼的分析任務。檢查清單模式適用於任何複雜、多步驟的流程。

**範例 2：PDF 表單填寫工作流**（適用於有程式碼的技能）：

````markdown  theme={null}
## PDF form filling workflow

Copy this checklist and check off items as you complete them:

```
Task Progress:
- [ ] Step 1: Analyze the form (run analyze_form.py)
- [ ] Step 2: Create field mapping (edit fields.json)
- [ ] Step 3: Validate mapping (run validate_fields.py)
- [ ] Step 4: Fill the form (run fill_form.py)
- [ ] Step 5: Verify output (run verify_output.py)
```

**Step 1: Analyze the form**

Run: `python scripts/analyze_form.py input.pdf`

This extracts form fields and their locations, saving to `fields.json`.

**Step 2: Create field mapping**

Edit `fields.json` to add values for each field.

**Step 3: Validate mapping**

Run: `python scripts/validate_fields.py fields.json`

Fix any validation errors before continuing.

**Step 4: Fill the form**

Run: `python scripts/fill_form.py input.pdf fields.json output.pdf`

**Step 5: Verify output**

Run: `python scripts/verify_output.py output.pdf`

If verification fails, return to Step 2.
````

清楚的步驟能防止代理跳過關鍵驗證。檢查清單幫助你與代理在多步驟工作流中追蹤進度。

### 實作回饋迴圈

**常見模式**：執行驗證器 → 修復錯誤 → 重複

這個模式能大幅提升輸出品質。

**範例 1：風格指南符合度**（適用於沒有程式碼的技能）：

```markdown  theme={null}
## Content review process

1. Draft your content following the guidelines in STYLE_GUIDE.md
2. Review against the checklist:
   - Check terminology consistency
   - Verify examples follow the standard format
   - Confirm all required sections are present
3. If issues found:
   - Note each issue with specific section reference
   - Revise the content
   - Review the checklist again
4. Only proceed when all requirements are met
5. Finalize and save the document
```

這展示了使用參考文件而非腳本的驗證迴圈模式。這裡的「validator」是 STYLE\_GUIDE.md，代理透過閱讀與比對來執行檢查。

**範例 2：文件編輯流程**（適用於有程式碼的技能）：

```markdown  theme={null}
## Document editing process

1. Make your edits to `word/document.xml`
2. **Validate immediately**: `python ooxml/scripts/validate.py unpacked_dir/`
3. If validation fails:
   - Review the error message carefully
   - Fix the issues in the XML
   - Run validation again
4. **Only proceed when validation passes**
5. Rebuild: `python ooxml/scripts/pack.py unpacked_dir/ output.docx`
6. Test the output document
```

驗證迴圈能及早捕捉錯誤。

## 內容準則

### 避免對時間敏感的資訊

不要包含會過時的資訊：

**壞範例：對時間敏感**（會變成錯的）：

```markdown  theme={null}
If you're doing this before August 2025, use the old API.
After August 2025, use the new API.
```

**好範例**（使用「舊模式」小節）：

```markdown  theme={null}
## Current method

Use the v2 API endpoint: `api.example.com/v2/messages`

## Old patterns

<details>
<summary>Legacy v1 API (deprecated 2025-08)</summary>

The v1 API used: `api.example.com/v1/messages`

This endpoint is no longer supported.
</details>
```

舊模式小節提供歷史脈絡，而不讓主要內容變得雜亂。

### 使用一致的術語

選擇一個詞，並在整個技能中一致使用：

**好——一致**：

* 永遠用 "API endpoint"
* 永遠用 "field"
* 永遠用 "extract"

**壞——不一致**：

* 混用 "API endpoint"、"URL"、"API route"、"path"
* 混用 "field"、"box"、"element"、"control"
* 混用 "extract"、"pull"、"get"、"retrieve"

一致性幫助代理理解並遵循指令。

## 常見模式

### 範本模式

為輸出格式提供範本。讓嚴格程度對應你的需求。

**對嚴格的需求**（像是 API 回應或資料格式）：

````markdown  theme={null}
## Report structure

ALWAYS use this exact template structure:

```markdown
# [Analysis Title]

## Executive summary
[One-paragraph overview of key findings]

## Key findings
- Finding 1 with supporting data
- Finding 2 with supporting data
- Finding 3 with supporting data

## Recommendations
1. Specific actionable recommendation
2. Specific actionable recommendation
```
````

**對彈性的指引**（當調整有用時）：

````markdown  theme={null}
## Report structure

Here is a sensible default format, but use your best judgment based on the analysis:

```markdown
# [Analysis Title]

## Executive summary
[Overview]

## Key findings
[Adapt sections based on what you discover]

## Recommendations
[Tailor to the specific context]
```

Adjust sections as needed for the specific analysis type.
````

### 範例模式

對輸出品質取決於看到範例的技能，提供輸入／輸出配對，就像一般的 prompt 一樣：

````markdown  theme={null}
## Commit message format

Generate commit messages following these examples:

**Example 1:**
Input: Added user authentication with JWT tokens
Output:
```
feat(auth): implement JWT-based authentication

Add login endpoint and token validation middleware
```

**Example 2:**
Input: Fixed bug where dates displayed incorrectly in reports
Output:
```
fix(reports): correct date formatting in timezone conversion

Use UTC timestamps consistently across report generation
```

**Example 3:**
Input: Updated dependencies and refactored error handling
Output:
```
chore: update dependencies and refactor error handling

- Upgrade lodash to 4.17.21
- Standardize error response format across endpoints
```

Follow this style: type(scope): brief description, then detailed explanation.
````

範例比單獨的描述更能幫助代理理解期望的風格與細節程度。

### 條件式工作流模式

引導代理走過決策點：

```markdown  theme={null}
## Document modification workflow

1. Determine the modification type:

   **Creating new content?** → Follow "Creation workflow" below
   **Editing existing content?** → Follow "Editing workflow" below

2. Creation workflow:
   - Use docx-js library
   - Build document from scratch
   - Export to .docx format

3. Editing workflow:
   - Unpack existing document
   - Modify XML directly
   - Validate after each change
   - Repack when complete
```

<Tip>
  如果工作流變大或因為步驟眾多而變複雜，考慮把它們移到獨立檔案，並告訴代理依手邊的任務讀取適當的檔案。
</Tip>

## 評估與疊代

### 先建立評估

**在撰寫大量文件之前，先建立評估。**這能確保你的技能解決真實問題，而不是把想像中的問題寫成文件。

**評估驅動開發：**

1. **找出缺口**：在沒有技能的情況下，用代表性的任務執行你的代理。記錄具體的失敗或缺漏的上下文
2. **建立評估**：建立三個能測試這些缺口的場景
3. **確立基線**：在沒有技能的情況下衡量代理的表現
4. **撰寫最小指令**：只建立足以處理缺口並通過評估的內容
5. **疊代**：執行評估、與基線比較，並調整

這個方法確保你解決的是實際問題，而不是預測可能永遠不會發生的需求。

**評估結構**：

```json  theme={null}
{
  "skills": ["pdf-processing"],
  "query": "Extract all text from this PDF file and save it to output.txt",
  "files": ["test-files/document.pdf"],
  "expected_behavior": [
    "Successfully reads the PDF file using an appropriate PDF processing library or command-line tool",
    "Extracts text content from all pages in the document without missing any pages",
    "Saves the extracted text to a file named output.txt in a clear, readable format"
  ]
}
```

<Note>
  這個範例展示了一種資料驅動的評估，帶有簡單的測試評分標準。我們目前沒有提供執行這些評估的內建方式。使用者可以建立自己的評估系統。評估是你衡量技能有效性的真相來源。
</Note>

### 與代理一起疊代式開發技能

最有效的技能開發流程涉及代理本身。與一個實例（「Agent A」）合作建立一個會被其他實例（「Agent B」）使用的技能。Agent A 幫你設計並調整指令，Agent B 在真實任務中測試它們。這之所以可行，是因為底層模型既理解如何撰寫有效的代理指令，也知道代理需要哪些資訊。

**建立一個新技能：**

1. **在沒有技能的情況下完成任務**：用正常的 prompt 與 Agent A 一起解決問題。工作過程中，你會自然提供上下文、解釋偏好、分享程序性知識。注意你重複提供了哪些資訊。

2. **找出可重用的模式**：完成任務後，找出你提供的哪些上下文對未來類似的任務有用。

   **範例**：如果你做了一次 BigQuery 分析，你可能提供了資料表名稱、欄位定義、篩選規則（像是「永遠排除測試帳號」），以及常見的查詢模式。

3. **請 Agent A 建立技能**：「建立一個捕捉我們剛剛使用的 BigQuery 分析模式的技能。包含資料表 schema、命名慣例，以及關於篩選測試帳號的規則。」

   <Tip>
     現代代理天生就理解技能格式與結構。你不需要特殊的 system prompt 或「writing skills」技能來獲得建立技能的協助。只要請代理建立技能，它就會產生結構正確的 SKILL.md 內容，帶有適當的 frontmatter 與本體內容。
   </Tip>

4. **檢查簡潔度**：確認 Agent A 沒有加入不必要的解釋。詢問：「移除關於 win rate 是什麼意思的解釋——代理已經知道了。」

5. **改善資訊架構**：請 Agent A 更有效地組織內容。例如：「把這個組織成資料表 schema 放在獨立的參考檔案。我們之後可能會加入更多資料表。」

6. **在類似的任務上測試**：在相關的使用案例上，用 Agent B（一個載入技能的乾淨實例）使用這個技能。觀察 Agent B 是否找到正確資訊、正確套用規則，並成功處理任務。

7. **依觀察疊代**：如果 Agent B 卡住或漏掉某些東西，帶著具體細節回到 Agent A：「當代理使用這個技能時，它忘了用日期篩選 Q4。我們該加一個關於日期篩選模式的小節嗎？」

**對既有技能疊代：**

同樣的階層模式在改善技能時會持續。你在以下之間交替：

* **與 Agent A 合作**（協助調整技能的專家）
* **用 Agent B 測試**（使用技能執行真實工作的代理）
* **觀察 Agent B 的行為**，並把洞察帶回給 Agent A

1. **在真實工作流中使用技能**：給 Agent B（已載入技能）實際任務，而不是測試場景

2. **觀察 Agent B 的行為**：記下它在哪裡卡住、成功，或做出意料之外的選擇

   **範例觀察**：「當我請 Agent B 做區域銷售報告時，它寫了查詢，卻忘了濾掉測試帳號，即使技能提到了這條規則。」

3. **回到 Agent A 尋求改善**：分享目前的 SKILL.md 並描述你觀察到的現象。詢問：「我注意到當我請 Agent B 做區域報告時，它忘了濾掉測試帳號。技能有提到篩選，但可能還不夠顯眼？」

4. **審查 Agent A 的建議**：Agent A 可能建議重新組織讓規則更顯眼、使用更強的語言（像是「MUST filter」而非「always filter」），或重構工作流小節。

5. **套用並測試變更**：用 Agent A 的調整更新技能，然後在類似的請求上再次用 Agent B 測試

6. **依使用情況重複**：當你遇到新的情境時，持續這個觀察-調整-測試循環。每一次疊代都是根據真實的代理行為（而非假設）來改善技能。

**收集團隊回饋：**

1. 與同事分享技能，並觀察他們的使用情況
2. 詢問：技能是否在預期時觸發？指令清楚嗎？缺少什麼？
3. 把回饋納入，以處理你自己使用模式中的盲點

**這個方法為何有效**：Agent A 理解代理的需求，你提供領域專業，Agent B 透過真實使用揭露缺口，而疊代式調整根據觀察到的行為（而非假設）改善技能。

### 觀察代理如何導覽技能

當你對技能疊代時，注意代理在實務中實際如何使用它們。留意：

* **意料之外的探索路徑**：代理是否以你沒預料到的順序讀取檔案？這可能表示你的結構不如你想像中直覺
* **漏掉的連結**：代理是否沒有遵循指向重要檔案的參考？你的連結可能需要更明確或更顯眼
* **過度依賴某些小節**：如果代理重複讀取同一個檔案，考慮那些內容是否應該放進主要 SKILL.md
* **被忽略的內容**：如果代理從未存取某個打包的檔案，它可能是多餘的，或是在主要指令中沒有被清楚提示

根據這些觀察（而非假設）疊代。技能 metadata 中的 `name` 與 `description` 特別關鍵。代理在決定是否要對目前任務觸發這個技能時會用到它們。確保它們清楚描述技能做什麼以及何時該使用。

## 要避免的反模式

### 避免 Windows 風格路徑

一律在檔案路徑中使用正斜線，即使在 Windows 上也是：

* ✓ **好**：`scripts/helper.py`、`reference/guide.md`
* ✗ **避免**：`scripts\helper.py`、`reference\guide.md`

Unix 風格路徑在所有平台上都能運作，而 Windows 風格路徑在 Unix 系統上會造成錯誤。

### 避免提供太多選項

除非必要，否則不要提出多種做法：

````markdown  theme={null}
**Bad example: Too many choices** (confusing):
"You can use pypdf, or pdfplumber, or PyMuPDF, or pdf2image, or..."

**Good example: Provide a default** (with escape hatch):
"Use pdfplumber for text extraction:
```python
import pdfplumber
```

For scanned PDFs requiring OCR, use pdf2image with pytesseract instead."
````

## 進階：帶可執行程式碼的技能

下方小節聚焦於包含可執行腳本的技能。如果你的技能只用 markdown 指令，跳到[有效技能檢查清單](#有效技能檢查清單)。

### 解決問題，不要推給代理

撰寫技能腳本時，要處理錯誤情況，而不是把問題推給代理。

**好範例：明確處理錯誤**：

```python  theme={null}
def process_file(path):
    """Process a file, creating it if it doesn't exist."""
    try:
        with open(path) as f:
            return f.read()
    except FileNotFoundError:
        # Create file with default content instead of failing
        print(f"File {path} not found, creating default")
        with open(path, 'w') as f:
            f.write('')
        return ''
    except PermissionError:
        # Provide alternative instead of failing
        print(f"Cannot access {path}, using default")
        return ''
```

**壞範例：推給代理**：

```python  theme={null}
def process_file(path):
    # Just fail and let the agent figure it out
    return open(path).read()
```

設定參數也應該說明理由並寫上文件，以避免「巫毒常數」（Ousterhout 定律）。如果你不知道正確的值，代理要怎麼決定？

**好範例：自我文件化**：

```python  theme={null}
# HTTP requests typically complete within 30 seconds
# Longer timeout accounts for slow connections
REQUEST_TIMEOUT = 30

# Three retries balances reliability vs speed
# Most intermittent failures resolve by the second retry
MAX_RETRIES = 3
```

**壞範例：魔術數字**：

```python  theme={null}
TIMEOUT = 47  # Why 47?
RETRIES = 5   # Why 5?
```

### 提供公用程式腳本

即使你的代理可以自己寫腳本，預先做好的腳本仍提供優勢：

**公用程式腳本的好處**：

* 比產生的程式碼更可靠
* 節省 tokens（不需要把程式碼放進上下文）
* 節省時間（不需要產生程式碼）
* 確保跨使用情境一致

<img src="https://mintcdn.com/anthropic-claude-docs/4Bny2bjzuGBK7o00/images/agent-skills-executable-scripts.png?fit=max&auto=format&n=4Bny2bjzuGBK7o00&q=85&s=4bbc45f2c2e0bee9f2f0d5da669bad00" alt="Bundling executable scripts alongside instruction files" data-og-width="2048" width="2048" data-og-height="1154" height="1154" data-path="images/agent-skills-executable-scripts.png" data-optimize="true" data-opv="3" srcset="https://mintcdn.com/anthropic-claude-docs/4Bny2bjzuGBK7o00/images/agent-skills-executable-scripts.png?w=280&fit=max&auto=format&n=4Bny2bjzuGBK7o00&q=85&s=9a04e6535a8467bfeea492e517de389f 280w, https://mintcdn.com/anthropic-claude-docs/4Bny2bjzuGBK7o00/images/agent-skills-executable-scripts.png?w=560&fit=max&auto=format&n=4Bny2bjzuGBK7o00&q=85&s=e49333ad90141af17c0d7651cca7216b 560w, https://mintcdn.com/anthropic-claude-docs/4Bny2bjzuGBK7o00/images/agent-skills-executable-scripts.png?w=840&fit=max&auto=format&n=4Bny2bjzuGBK7o00&q=85&s=954265a5df52223d6572b6214168c428 840w, https://mintcdn.com/anthropic-claude-docs/4Bny2bjzuGBK7o00/images/agent-skills-executable-scripts.png?w=1100&fit=max&auto=format&n=4Bny2bjzuGBK7o00&q=85&s=2ff7a2d8f2a83ee8af132b29f10150fd 1100w, https://mintcdn.com/anthropic-claude-docs/4Bny2bjzuGBK7o00/images/agent-skills-executable-scripts.png?w=1650&fit=max&auto=format&n=4Bny2bjzuGBK7o00&q=85&s=48ab96245e04077f4d15e9170e081cfb 1650w, https://mintcdn.com/anthropic-claude-docs/4Bny2bjzuGBK7o00/images/agent-skills-executable-scripts.png?w=2500&fit=max&auto=format&n=4Bny2bjzuGBK7o00&q=85&s=0301a6c8b3ee879497cc5b5483177c90 2500w" />

上方的圖展示了可執行腳本如何與指令檔案並行運作。指令檔案（forms.md）參考腳本，而代理可以在不把內容載入上下文的情況下執行它。

**重要區別**：在你的指令中清楚說明代理應該：

* **執行腳本**（最常見）："Run `analyze_form.py` to extract fields"
* **把它當作參考閱讀**（對複雜邏輯）："See `analyze_form.py` for the field extraction algorithm"

對大多數公用程式腳本，執行是優先選項，因為它更可靠且更有效率。關於腳本執行如何運作的細節，請見下方的[執行環境](#執行環境)小節。

**範例**：

````markdown  theme={null}
## Utility scripts

**analyze_form.py**: Extract all form fields from PDF

```bash
python scripts/analyze_form.py input.pdf > fields.json
```

Output format:
```json
{
  "field_name": {"type": "text", "x": 100, "y": 200},
  "signature": {"type": "sig", "x": 150, "y": 500}
}
```

**validate_boxes.py**: Check for overlapping bounding boxes

```bash
python scripts/validate_boxes.py fields.json
# Returns: "OK" or lists conflicts
```

**fill_form.py**: Apply field values to PDF

```bash
python scripts/fill_form.py input.pdf fields.json output.pdf
```
````

### 使用視覺分析

當輸入可以渲染成圖片時，讓代理分析它們：

````markdown  theme={null}
## Form layout analysis

1. Convert PDF to images:
   ```bash
   python scripts/pdf_to_images.py form.pdf
   ```

2. Analyze each page image to identify form fields
3. The agent can see field locations and types visually
````

<Note>
  在這個範例中，你需要撰寫 `pdf_to_images.py` 腳本。
</Note>

代理的視覺能力有助於理解版面與結構。

### 建立可驗證的中間輸出

當代理執行複雜、開放式的任務時，它們可能犯錯。「計畫-驗證-執行」模式讓代理先用結構化格式建立計畫，再用腳本驗證該計畫，然後才執行，藉此及早捕捉錯誤。

**範例**：想像請代理根據一份試算表更新 PDF 中的 50 個表單欄位。沒有驗證的話，它可能會引用不存在的欄位、建立衝突的值、漏掉必填欄位，或錯誤地套用更新。

**解決方案**：使用上面展示的工作流模式（PDF 表單填寫），但加入一個在套用變更前先被驗證的中間 `changes.json` 檔案。工作流變成：分析 → **建立計畫檔案** → **驗證計畫** → 執行 → 驗證。

**這個模式為何有效：**

* **及早捕捉錯誤**：驗證在變更套用前就發現問題
* **機器可驗證**：腳本提供客觀的驗證
* **可逆的計畫**：代理可以在不觸碰原檔的情況下對計畫疊代
* **清楚的除錯**：錯誤訊息指向特定問題

**使用時機**：批次操作、破壞性變更、複雜的驗證規則、高風險操作。

**實作提示**：讓驗證腳本詳細，帶有特定的錯誤訊息，像是 "Field 'signature\_date' not found. Available fields: customer\_name, order\_total, signature\_date\_signed"，以幫助代理修復問題。

### 打包相依套件

技能在程式碼執行環境中執行，帶有平台特定限制：

* **claude.ai**：可以從 npm 與 PyPI 安裝套件，並從 GitHub 儲存庫拉取
* **Anthropic API**：沒有網路存取，也沒有執行期套件安裝

在 SKILL.md 中列出所需的套件，並確認它們在[程式碼執行工具文件](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool)中可用。

### 執行環境

技能在帶有檔案系統存取、bash 指令與程式碼執行能力的程式碼執行環境中執行。關於這個架構的概念說明，請見總覽中的[技能架構](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview#the-skills-architecture)。

**這如何影響你的撰寫：**

**代理如何存取技能：**

1. **Metadata 預先載入**：啟動時，所有技能 YAML frontmatter 中的 name 與 description 會被載入 system prompt
2. **按需讀取檔案**：代理使用檔案讀取工具，在需要時從檔案系統存取 SKILL.md 與其他檔案
3. **有效率地執行腳本**：公用程式腳本可以透過 bash 執行，而不需要把它們的完整內容載入上下文。只有腳本的輸出消耗 tokens
4. **大型檔案沒有上下文懲罰**：參考檔案、資料或文件在實際讀取前不消耗上下文 tokens

* **檔案路徑很重要**：代理會像導覽檔案系統一樣導覽你的技能目錄。使用正斜線（`reference/guide.md`），不要用反斜線
* **具描述性地命名檔案**：使用能指出內容的名稱：`form_validation_rules.md`，而不是 `doc2.md`
* **為探索而組織**：依領域或功能組織目錄
  * 好：`reference/finance.md`、`reference/sales.md`
  * 壞：`docs/file1.md`、`docs/file2.md`
* **打包完整資源**：包含完整的 API 文件、大量的範例、大型資料集；在存取前沒有上下文懲罰
* **對確定性操作偏好腳本**：撰寫 `validate_form.py`，而不是要求代理產生驗證程式碼
* **讓執行意圖清楚**：
  * "Run `analyze_form.py` to extract fields"（執行）
  * "See `analyze_form.py` for the extraction algorithm"（作為參考閱讀）
* **測試檔案存取模式**：用真實請求測試，確認代理能導覽你的目錄結構

**範例：**

```
bigquery-skill/
├── SKILL.md (overview, points to reference files)
└── reference/
    ├── finance.md (revenue metrics)
    ├── sales.md (pipeline data)
    └── product.md (usage analytics)
```

當使用者問到營收時，代理讀取 SKILL.md、看到指向 `reference/finance.md` 的參考，並呼叫 bash 只讀取那個檔案。sales.md 與 product.md 留在檔案系統上，在需要前不消耗任何上下文 tokens。這個以檔案系統為基礎的模型正是漸進揭露之所以可行的原因。代理可以導覽並選擇性地載入每個任務所需的確切內容。

技術架構的完整細節，請見技能總覽中的[技能如何運作](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview#how-skills-work)。

### MCP 工具參考

如果你的技能使用 MCP（Model Context Protocol）工具，永遠使用完整限定的工具名稱，以避免「tool not found」錯誤。

**格式**：`ServerName:tool_name`

**範例**：

```markdown  theme={null}
Use the BigQuery:bigquery_schema tool to retrieve table schemas.
Use the GitHub:create_issue tool to create issues.
```

其中：

* `BigQuery` 與 `GitHub` 是 MCP server 名稱
* `bigquery_schema` 與 `create_issue` 是這些 server 內的工具名稱

沒有 server 前綴時，代理可能找不到工具，特別是在有多個 MCP server 可用時。

### 避免假設工具已安裝

不要假設套件已可用：

````markdown  theme={null}
**Bad example: Assumes installation**:
"Use the pdf library to process the file."

**Good example: Explicit about dependencies**:
"Install required package: `pip install pypdf`

Then use it:
```python
from pypdf import PdfReader
reader = PdfReader("file.pdf")
```"
````

## 技術備註

### YAML frontmatter 需求

SKILL.md 的 frontmatter 需要 `name`（最多 64 字元）與 `description`（最多 1024 字元）欄位。完整的結構細節請見[技能總覽](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview#skill-structure)。

### Token 預算

讓 SKILL.md 本體保持在 500 行以內以獲得最佳效能。如果你的內容超過這個數字，用先前描述的漸進揭露模式把它拆到獨立檔案。架構細節請見[技能總覽](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview#how-skills-work)。

## 有效技能檢查清單

分享技能之前，驗證：

### 核心品質

* [ ] Description 具體且包含關鍵詞
* [ ] Description 同時包含技能做什麼與何時使用
* [ ] SKILL.md 本體在 500 行以內
* [ ] 額外細節放在獨立檔案（若需要）
* [ ] 沒有對時間敏感的資訊（或放在「舊模式」小節）
* [ ] 全程使用一致的術語
* [ ] 範例具體，而非抽象
* [ ] 檔案參考維持一層深度
* [ ] 適當地使用漸進揭露
* [ ] 工作流有清楚的步驟

### 程式碼與腳本

* [ ] 腳本解決問題，而不是推給代理
* [ ] 錯誤處理明確且有幫助
* [ ] 沒有「巫毒常數」（所有值都有理由）
* [ ] 所需套件列在指令中並驗證可用
* [ ] 腳本有清楚的文件
* [ ] 沒有 Windows 風格路徑（全部用正斜線）
* [ ] 對關鍵操作有驗證／確認步驟
* [ ] 對品質關鍵任務包含回饋迴圈

### 測試

* [ ] 建立至少三個評估
* [ ] 用 Haiku、Sonnet 與 Opus 測試過
* [ ] 用真實使用情境測試過
* [ ] 已納入團隊回饋（若適用）

## 下一步

<CardGroup cols={2}>
  <Card title="Get started with Agent Skills" icon="rocket" href="https://platform.claude.com/docs/en/agents-and-tools/agent-skills/quickstart">
    Create your first Skill
  </Card>

  <Card title="Use Skills in Claude Code" icon="terminal" href="https://code.claude.com/docs/en/skills">
    Create and manage Skills in Claude Code
  </Card>

  <Card title="Use Skills with the API" icon="code" href="https://platform.claude.com/docs/en/build-with-claude/skills-guide">
    Upload and use Skills programmatically
  </Card>
</CardGroup>
