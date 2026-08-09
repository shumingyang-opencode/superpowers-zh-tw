---
name: requesting-code-review
description: 當完成任務、實作主要功能，或在合併之前，用於驗證工作成果符合需求時使用
---

# 請求程式碼審查

派發一個程式碼審查子代理，在問題擴大蔓延之前捕捉問題。審查者會取得精確建構的評估上下文 —— 絕不是你 session 的歷史。

**核心原則：** 早點審查，常常審查。

## 何時請求審查

**必須：**
- 子代理驅動開發中每個任務之後
- 完成主要功能之後
- 合併到 main 之前

**非必要但有價值：**
- 卡住時（新的視角）
- 重構之前（基線檢查）
- 修正複雜 bug 之後

## 如何請求

**1. 取得 git SHAs：**
```bash
BASE_SHA=$(git rev-parse HEAD~1)  # or origin/main
HEAD_SHA=$(git rev-parse HEAD)
```

**2. 派發程式碼審查子代理：**

派發一個 `general-purpose` 子代理，填入 [code-reviewer.md](code-reviewer.md) 的範本

**占位符：**
- `{DESCRIPTION}` - 你建構內容的簡短摘要
- `{PLAN_OR_REQUIREMENTS}` - 它應該做什麼
- `{BASE_SHA}` - 起始 commit
- `{HEAD_SHA}` - 結束 commit

**3. 依回饋行動：**
- 立即修正 Critical 問題
- 在繼續前修正 Important 問題
- 記下 Minor 問題稍後處理
- 若審查者錯了，提出異議（附上理由）

## 範例

```
[Just completed Task 2: Add verification function]

You: Let me request code review before proceeding.

BASE_SHA=$(git log --oneline | grep "Task 1" | head -1 | awk '{print $1}')
HEAD_SHA=$(git rev-parse HEAD)

[Dispatch code reviewer subagent]
  DESCRIPTION: Added verifyIndex() and repairIndex() with 4 issue types
  PLAN_OR_REQUIREMENTS: Task 2 from docs/superpowers/plans/deployment-plan.md
  BASE_SHA: a7981ec
  HEAD_SHA: 3df7661

[Subagent returns]:
  Strengths: Clean architecture, real tests
  Issues:
    Important: Missing progress indicators
    Minor: Magic number (100) for reporting interval
  Assessment: Ready to proceed

You: [Fix progress indicators]
[Continue to Task 3]
```

## 常見合理化藉口

| 藉口 | 事實 |
|--------|---------|
| 「我自己審視 diff 就好，不用派發審查者」 | 你是協調者 —— 直接審視 diff 會燒掉你持續推動工作所需的上下文。派發一個審查子代理：diff 與評估都在它的上下文裡，只有發現回傳給你。 |
| 「審查者需要我整個 session 的歷史才能理解變更」 | 給它精確建構的上下文，絕不是你 session 的歷史。這讓審查者專注於工作成果，而不是你的思考過程。 |

## 紅旗

**絕不：**
- 因為「這很簡單」就跳過審查
- 忽略 Critical 問題
- 帶著未修正的 Important 問題繼續
- 與合理的技術回饋爭辯

**如果審查者錯了：**
- 用技術論證提出異議
- 展示證明它能運作的程式碼/測試
- 請求釐清

範本見：[code-reviewer.md](code-reviewer.md)
