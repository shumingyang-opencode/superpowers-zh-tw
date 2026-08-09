---
name: using-git-worktrees
description: 當開始需要與目前工作區隔離的功能工作，或在執行實作計畫之前使用 —— 透過原生工具或 git worktree 備援方式確保有隔離的工作區
---

# 使用 Git Worktrees

## 總覽

確保工作在隔離的工作區中進行。優先使用你平台的原生 worktree 工具。只有在沒有原生工具可用時，才改用手動 git worktree。

**核心原則：** 先偵測現有的隔離狀態。再用原生工具。最後才回到 git。永遠不要對抗 harness。

**開始時宣告：** 「我正使用 using-git-worktrees 技能來設定隔離的工作區。」

## 第 0 步：偵測現有的隔離狀態

**在建立任何東西之前，檢查你是否已在隔離的工作區中。**

```bash
GIT_DIR=$(cd "$(git rev-parse --git-dir)" 2>/dev/null && pwd -P)
GIT_COMMON=$(cd "$(git rev-parse --git-common-dir)" 2>/dev/null && pwd -P)
BRANCH=$(git branch --show-current)
```

**子模組防護：** `GIT_DIR != GIT_COMMON` 在 git 子模組內部也成立。在得出「已在 worktree 中」的結論之前，先確認你不位於子模組中：

```bash
# If this returns a path, you're in a submodule, not a worktree — treat as normal repo
git rev-parse --show-superproject-working-tree 2>/dev/null
```

**如果 `GIT_DIR != GIT_COMMON`（且不是子模組）：** 你已在一個連結的 worktree 中。跳到第 2 步（專案設定）。不要再建立 worktree。

回報分支狀態：
- 在分支上：「已位於隔離工作區 `<path>`，分支 `<name>`。」
- Detached HEAD：「已位於隔離工作區 `<path>`（detached HEAD，外部管理）。完成時需建立分支。」

**如果 `GIT_DIR == GIT_COMMON`（或在子模組中）：** 你位於一般的 repo checkout 中。

使用者是否已在你的指令中表明其 worktree 偏好？如果沒有，在建立 worktree 前先徵求同意：

> 「你要我設定一個隔離的 worktree 嗎？它會保護你目前的分支不受變更影響。」

尊重任何已宣告的偏好，不再詢問。如果使用者婉拒同意，就原地工作並跳到第 2 步。

## 第 1 步：建立隔離工作區

**你有兩種機制。依這個順序嘗試。**

### 1a. 原生 Worktree 工具（首選）

使用者已要求隔離工作區（第 0 步的同意）。你已有建立 worktree 的方式嗎？可能是名為 `EnterWorktree`、`WorktreeCreate` 的工具、`/worktree` 指令，或 `--worktree` 旗標。如果有，就使用它並跳到第 2 步。

原生工具會自動處理目錄位置、分支建立與清理。當你有原生工具卻用 `git worktree add`，會建立你的 harness 看不見也無法管理的幽靈狀態。

只有在沒有原生 worktree 工具可用時，才繼續到第 1b 步。

### 1b. Git Worktree 備援

**只有當第 1a 步不適用時才使用** —— 你沒有可用的原生 worktree 工具。手動用 git 建立 worktree。

#### 目錄選擇

依這個優先序。使用者的明確偏好永遠勝過觀察到的檔案系統狀態。

1. **檢查你的指令中是否有宣告的 worktree 目錄偏好。** 如果使用者已指定，直接使用，不再詢問。

2. **檢查既有的專案內 worktree 目錄：**
   ```bash
   ls -d .worktrees 2>/dev/null     # Preferred (hidden)
   ls -d worktrees 2>/dev/null      # Alternative
   ```
   如果有就使用。如果兩者都存在，`.worktrees` 優先。

3. **如果沒有其他指引可用**，預設使用專案根目錄的 `.worktrees/`。

#### 安全性驗證（僅限專案內目錄）

**建立 worktree 前必須驗證目錄已被忽略：**

```bash
git check-ignore -q .worktrees 2>/dev/null || git check-ignore -q worktrees 2>/dev/null
```

**如果未被忽略：** 加入 .gitignore、commit 這個變更，然後繼續。

**為什麼關鍵：** 防止不小心把 worktree 內容 commit 進 repo。

#### 建立 Worktree

```bash
# Determine path based on chosen location
path="$LOCATION/$BRANCH_NAME"

git worktree add "$path" -b "$BRANCH_NAME"
cd "$path"
```

**Sandbox 備援：** 如果 `git worktree add` 因權限錯誤（sandbox 拒絕）而失敗，告訴使用者 sandbox 封鎖了 worktree 建立，你改在目前目錄工作。然後原地執行設定與基線測試。

## 第 2 步：專案設定

自動偵測並執行適當的設定：

```bash
# Node.js
if [ -f package.json ]; then npm install; fi

# Rust
if [ -f Cargo.toml ]; then cargo build; fi

# Python
if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
if [ -f pyproject.toml ]; then poetry install; fi

# Go
if [ -f go.mod ]; then go mod download; fi
```

## 第 3 步：驗證乾淨的基線

執行測試以確保工作區以乾淨狀態開始：

```bash
# Use project-appropriate command
npm test / cargo test / pytest / go test ./...
```

**如果測試失敗：** 回報失敗，詢問要繼續還是調查。

**如果測試通過：** 回報就緒。

### 回報

```
Worktree ready at <full-path>
Tests passing (<N> tests, 0 failures)
Ready to implement <feature-name>
```

## 快速參考

| 情境 | 動作 |
|-----------|--------|
| 已在連結的 worktree 中 | 跳過建立（第 0 步） |
| 在子模組中 | 視為一般 repo（第 0 步防護） |
| 有原生 worktree 工具 | 使用它（第 1a 步） |
| 沒有原生工具 | Git worktree 備援（第 1b 步） |
| `.worktrees/` 存在 | 使用它（驗證已忽略） |
| `worktrees/` 存在 | 使用它（驗證已忽略） |
| 兩者都存在 | 使用 `.worktrees/` |
| 都不存在 | 檢查指令檔，然後預設 `.worktrees/` |
| 目錄未被忽略 | 加入 .gitignore + commit |
| 建立時權限錯誤 | Sandbox 備援，原地工作 |
| 基線測試失敗 | 回報失敗 + 詢問 |
| 沒有 package.json/Cargo.toml | 跳過依賴安裝 |

## 常見合理化藉口

| 藉口 | 事實 |
|--------|---------|
| 「我顯然不在 worktree 裡——不必檢查」 | 執行第 0 步。harness 建立的隔離狀態與子模組都會騙過肉眼；偵測指令才能定案。 |
| 「`git worktree add` 比找原生工具快」 | 原生工具（例如 `EnterWorktree`）負責放置、分支與清理。繞過它是最常見的錯誤 #1 —— 它會建立你的 harness 看不見也無法管理的幽靈狀態。 |
| 「worktree 目錄肯定已經被忽略了」 | 執行 `git check-ignore`。未被忽略的 worktree 目錄會把整棵樹 commit 進 repo。 |
| 「任何目錄名都行」 | 明確的指令勝過既有的專案內目錄，既有的專案內目錄勝過 `.worktrees/` 預設。 |
| 「工作區是全新的——基線測試可以晚點跑」 | 骯髒的基線會讓之後每個失敗都變得不明確。現在就跑測試；要不要在失敗中繼續前進是你的人工夥伴的決定。 |
