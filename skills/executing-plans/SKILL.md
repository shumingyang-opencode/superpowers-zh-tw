---
name: executing-plans
description: 當你有一份書面的實作計畫，需要在另一個 session 中執行並設有審查檢查點時使用
---

# 執行計畫

## 總覽

載入計畫、批判性審查、執行所有任務、完成後回報。

**開始時宣告：** 「我正使用 executing-plans 技能來實作這個計畫。」

**注意：** 告訴你的人工夥伴，Superpowers 在能使用子代理（Claude Code、Codex CLI、Codex App、Copilot CLI 與 Gemini CLI 皆符合；請參閱 `../using-superpowers/references/` 中各平台的工具參考）時會運作得更好。如果可以使用子代理，請改用 superpowers:subagent-driven-development，而不要使用此技能。

## 流程

### 第 1 步：載入並審查計畫
1. 確保有隔離的工作區：使用 superpowers:using-git-worktrees 建立一個或驗證現有的
2. 讀取計畫檔
3. 批判性審查 —— 找出對計畫的任何疑問或顧慮
4. 若有顧慮：開始前先與你的人工夥伴提出
5. 若無顧慮：為計畫項目建立 todos 並繼續進行

### 第 2 步：執行任務

對每個任務：
1. 標記為 in_progress
2. 精確依循每個步驟（計畫已切成小而專注的步驟）
3. 依指定執行驗證
4. 標記為 completed

### 第 3 步：完成開發

所有任務完成並驗證後：
- 宣告：「我正使用 finishing-a-development-branch 技能來完成這份工作。」
- **必要子技能：** 使用 superpowers:finishing-a-development-branch
- 依循該技能驗證測試、呈現選項、執行選擇

## 何時停下尋求協助

**遇到以下情況立即停止執行：**
- 卡住（缺少依賴、測試失敗、指示不明）
- 計畫有阻礙開始的關鍵缺口
- 不理解某個指示
- 驗證持續失敗

**寧可詢問釐清，也不要亂猜。**

## 何時回到較早的步驟

**遇到以下情況回到審查（第 1 步）：**
- 夥伴根據你的回饋更新計畫
- 根本做法需要重新思考

**不要硬闖卡點** - 停下來詢問。

## 記住
- 先批判性審查計畫
- 精確依循計畫步驟
- 不要跳過驗證
- 計畫提到時參照技能
- 卡住就停下，不要亂猜
- 未經使用者明確同意，絕不在 main/master 分支上開始實作
