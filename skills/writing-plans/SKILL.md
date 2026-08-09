---
name: writing-plans
description: 當你有一份多步驟任務的規格或需求，在動任何程式碼之前使用
---

# 撰寫計畫

## 總覽

撰寫全面的實作計畫，並假設工程師對我們的程式碼庫零上下文、品味存疑。記錄他們需要知道的一切：每個任務要動哪些檔案、程式碼、測試、可能需要查閱的文件、如何測試。把整個計畫拆成小塊任務交給他們。DRY。YAGNI。TDD。頻繁 commit。

假設他們是熟練的開發者，但對我們的工具組或問題領域幾乎一無所知。假設他們不太懂好的測試設計。

**開始時宣告：** 「我正使用 writing-plans 技能來建立實作計畫。」

**上下文：** 如果在隔離的 worktree 中工作，它應該已在執行時透過 `superpowers:using-git-worktrees` 技能建立。

**計畫儲存位置：** `docs/superpowers/plans/YYYY-MM-DD-<feature-name>.md`
- （使用者對計畫位置的偏好會覆蓋這個預設）

## 範圍檢查

如果規格涵蓋多個獨立的子系統，它應該在腦力激盪時被拆成子專案規格。如果沒有，建議把它拆成多份獨立計畫 —— 每個子系統一份。每份計畫應該要能獨立產出可運作、可測試的軟體。

## 檔案結構

在定義任務之前，先規劃哪些檔案會被建立或修改，以及每個檔案負責什麼。分解的決策在這裡鎖定。

- 設計邊界清楚、介面定義良好的單元。每個檔案應該有單一清楚的職責。
- 你對能同時放進上下文的程式碼思考得最好，而檔案越聚焦，你的編輯就越可靠。偏好較小、聚焦的檔案，勝過塞太多事的巨型檔案。
- 一起變更的檔案應該住在一起。依職責拆分，而不是依技術層拆分。
- 在既有程式碼庫中，遵循既有模式。如果程式碼庫使用大型檔案，不要單方面重構 —— 但如果你正在修改的檔案已經長到難以掌控，把拆分寫進計畫是合理的。

這個結構支撐任務的分解。每個任務應該產出自足的變更，且可以獨立理解。

## 任務尺寸調校

一個任務是承載自己的測試循環、並值得一個全新審查者關卡的最小單位。在劃分任務邊界時：把設定、配置、脚手架與文件步驟併入需要這些產物的任務；只有在審查者可以有意義地否決一個任務、同時核准其鄰居任務的地方才拆分。每個任務都以一個可獨立測試的產物結束。

## 小塊任務粒度

**每個步驟是單一動作（2-5 分鐘）：**
- 「撰寫失敗的測試」- 步驟
- 「執行它以確認它失敗」- 步驟
- 「撰寫能讓測試通過的最小程式碼」- 步驟
- 「執行測試並確認它們通過」- 步驟
- 「Commit」- 步驟

## 計畫文件標頭

**每份計畫都必須以此標頭開始：**

```markdown
# [Feature Name] Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** [One sentence describing what this builds]

**Architecture:** [2-3 sentences about approach]

**Tech Stack:** [Key technologies/libraries]

## Global Constraints

[The spec's project-wide requirements — version floors, dependency limits,
naming and copy rules, platform requirements — one line each, with exact
values copied verbatim from the spec. Every task's requirements implicitly
include this section.]

---
```

## 任務結構

````markdown
### Task N: [Component Name]

**Files:**
- Create: `exact/path/to/file.py`
- Modify: `exact/path/to/existing.py:123-145`
- Test: `tests/exact/path/to/test.py`

**Interfaces:**
- Consumes: [what this task uses from earlier tasks — exact signatures]
- Produces: [what later tasks rely on — exact function names, parameter
  and return types. A task's implementer sees only their own task; this
  block is how they learn the names and types neighboring tasks use.]

- [ ] **Step 1: Write the failing test**

```python
def test_specific_behavior():
    result = function(input)
    assert result == expected
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/path/test.py::test_name -v`
Expected: FAIL with "function not defined"

- [ ] **Step 3: Write minimal implementation**

```python
def function(input):
    return expected
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/path/test.py::test_name -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/path/test.py src/path/file.py
git commit -m "feat: add specific feature"
```
````

## 禁止占位符

每個步驟都必須包含工程師需要的實際內容。這些都是**計畫失敗**——絕不允許：
- 「TBD」「TODO」「之後再實作」「補上細節」
- 「加入適當的錯誤處理」/「加入驗證」/「處理邊界情況」
- 「為上述撰寫測試」（沒有實際測試程式碼）
- 「類似任務 N」（重複程式碼 —— 工程師可能不依順序閱讀任務）
- 只描述要做什麼、卻不展示怎麼做的步驟（程式碼步驟需要程式碼區塊）
- 引用任何任務中都未定義的型別、函式或方法

## 自我審查

寫完完整計畫後，以全新眼光看待規格，並據此檢查計畫。這是你自己執行的檢查清單 —— 不是子代理派發。

**1. 規格涵蓋：** 略讀規格中的每個段落/需求。你能指出實作它的任務嗎？列出任何缺口。

**2. 占位符掃描：** 搜尋計畫中的紅旗 —— 上方「禁止占位符」一節的任何模式。修正它們。

**3. 型別一致性：** 你在後續任務中使用的型別、方法簽名與屬性名稱，是否與較早任務中定義的一致？任務 3 中叫 `clearLayers()`、任務 7 卻叫 `clearFullLayers()` 的函式就是一個 bug。

如果發現問題，就地修正。不需要重新審查 —— 修好就繼續。如果發現某個規格需求沒有對應任務，就把任務加上去。

## 執行交接

儲存計畫後，提供執行方式的選擇：

**「計畫已完成並儲存至 `docs/superpowers/plans/<filename>.md`。兩種執行方式：**

**1. 子代理驅動（建議）** - 每個任務派發全新子代理，任務之間進行審查，快速迭代

**2. 行內執行** - 使用 executing-plans 在此 session 中執行任務，批次執行並設檢查點

**想用哪一種？」**

**如果選擇子代理驅動：**
- **必要子技能：** 使用 superpowers:subagent-driven-development
- 每個任務全新子代理 + 兩階段審查

**如果選擇行內執行：**
- **必要子技能：** 使用 superpowers:executing-plans
- 批次執行並設審查檢查點
