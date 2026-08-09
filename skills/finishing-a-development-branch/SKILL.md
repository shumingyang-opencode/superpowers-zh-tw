---
name: finishing-a-development-branch
description: 當實作完成、所有測試通過，且你需要決定如何整合這份工作成果時使用
---

# 完成開發分支

## 總覽

**核心原則：** 驗證測試 → 偵測環境 → 呈現選項 → 執行選擇 → 清理。

**開始時宣告：** 「我正使用 finishing-a-development-branch 技能來完成這份工作。」

## 第 1 步：驗證測試

執行專案的完整測試套件（`npm test` / `cargo test` / `pytest` / `go test ./...`）。

**如果測試失敗**，回報失敗並停止 —— 選單要在測試全綠之後才會出現：

```
Tests failing (<N> failures). Must fix before completing:

[Show failures]
```

**如果測試通過：** 繼續到第 2 步。

## 第 2 步：偵測環境

```bash
GIT_DIR=$(cd "$(git rev-parse --git-dir)" 2>/dev/null && pwd -P)
GIT_COMMON=$(cd "$(git rev-parse --git-common-dir)" 2>/dev/null && pwd -P)
# Capture now, while still inside the workspace — Step 5 changes directory
# before cleanup (Step 6) needs this value
WORKTREE_PATH=$(git rev-parse --show-toplevel)
```

這決定要顯示哪個選單以及如何清理：

| 狀態 | 選單 | 清理 |
|-------|------|---------|
| `GIT_DIR == GIT_COMMON`（一般 repo） | 標準 3 個選項 | 沒有 worktree 需要清理 |
| `GIT_DIR != GIT_COMMON`，具名分支 | 標準 3 個選項 | 依來源決定（見第 6 步） |
| `GIT_DIR != GIT_COMMON`，detached HEAD | 縮減為 2 個選項（無合併） | 由外部管理 —— 保留原位 |

## 第 3 步：決定基礎分支

基礎分支是這份工作從中分支出來的來源 —— 通常在計畫、對話或分支的上游中提及。如果尚未得知，請詢問：「這個分支是從 <你的最佳猜測> 分出來的 - 正確嗎？」合併前先確認：合併到錯誤的基礎分支要復原的成本很高。

## 第 4 步：呈現選項

**一般 repo 與具名分支 worktree —— 呈現恰好這 3 個選項：**

```
Implementation complete. What would you like to do?

1. Merge back to <base-branch> locally
2. Push and create a Pull Request
3. Keep the branch as-is (I'll handle it later)

Which option?
```

**Detached HEAD —— 呈現恰好這 2 個選項：**

```
Implementation complete. You're on a detached HEAD (externally managed workspace).

1. Push as new branch and create a Pull Request
2. Keep as-is (I'll handle it later)

Which option?
```

照原樣呈現選單 —— 精簡，且每個選項都來自上述清單。唯有當你的人工夥伴明確要求時，才會捨棄這份工作成果（見下方「如果你的人工夥伴要求捨棄工作成果」）。等待他們回答；整合的決定權在他們。

## 第 5 步：執行選擇

### 選項 1：在本機合併

```bash
# Get main repo root for CWD safety
MAIN_ROOT=$(git -C "$(git rev-parse --git-common-dir)/.." rev-parse --show-toplevel)
cd "$MAIN_ROOT"

# Merge first — verify success before removing anything
git checkout <base-branch>
git pull
git merge <feature-branch>

# Verify tests on merged result
<test command>
```

如果合併結果的測試失敗：停下，保留 worktree 與分支原狀並調查 —— 因為尚未 push 任何東西，這個合併是本機操作，可以復原。

一旦合併結果全綠：先清理 worktree（第 6 步），再刪除分支：

```bash
git branch -d <feature-branch>
```

### 選項 2：Push 並建立 PR

```bash
git push -u origin <feature-branch>
# From a detached HEAD, name the new branch on the remote:
# git push origin HEAD:refs/heads/<new-branch>
```

接著對 <base-branch> 建立 pull/merge request，使用 forge 的工具 —— 若有 CLI 就用 CLI，否則用多數 forge 在 push 時列印的建立 URL —— 遵循 repo 的 PR 範本與慣例（若有的話），並把 URL 回報給你的人工夥伴。

保留 worktree —— 你的人工夥伴會在那裡處理 PR 回饋。

### 選項 3：維持原狀

回報：「保留分支 <name>。Worktree 保留於 <path>。」

### 如果你的人工夥伴要求捨棄工作成果

這條路徑只存在於對「丟掉這份工作」的明確請求的回應。先確認：

```
This will permanently delete:
- Branch <name>
- All commits: <commit-list>
- Worktree at <path>

Type 'discard' to confirm.
```

等待該確認詞。當它出現時：

```bash
MAIN_ROOT=$(git -C "$(git rev-parse --git-common-dir)/.." rev-parse --show-toplevel)
cd "$MAIN_ROOT"
```

接著清理 worktree（第 6 步）並強制刪除分支：

```bash
git branch -D <feature-branch>
```

## 第 6 步：清理工作區

**選項 1 與已確認的捨棄會執行此步驟。** 選項 2 與 3 一律保留 worktree。兩者都已切換目錄到主 repo 根目錄 —— 移除 worktree 必須在 worktree 外部執行 —— 並使用第 2 步中、切換目錄之前所捕捉的 `GIT_DIR`/`GIT_COMMON`/`WORKTREE_PATH` 值。

**如果 `GIT_DIR == GIT_COMMON`：** 一般 repo，沒有 worktree 需要清理。結束。

**如果 `WORKTREE_PATH` 位於 `.worktrees/` 或 `worktrees/` 之下：** Superpowers 建立了這個 worktree —— 由我們負責清理：

```bash
git worktree remove "$WORKTREE_PATH"
git worktree prune  # Self-healing: clean up any stale registrations
```

**否則：** 主環境擁有這個工作區 —— 保留原位。如果你的平台提供 workspace-exit 工具，請使用它。

## 快速參考

| 選項 | 合併 | Push | 保留 Worktree | 清理分支 |
|--------|-------|------|---------------|----------------|
| 1. 在本機合併 | 是 | - | - | 是 |
| 2. 建立 PR | - | 是 | 是 | - |
| 3. 維持原狀 | - | - | 是 | - |
| 捨棄（僅限明確請求） | - | - | - | 是（強制） |

## 常見合理化藉口

| 藉口 | 事實 |
|--------|---------|
| 「這個 session 稍早測試通過了」 | 對你即將整合的那棵樹執行測試套件。一次綠色的執行只能證明它跑過的那棵樹。 |
| 「他們顯然想要合併」 | 整合是你的人工夥伴的決定。呈現選單並等待。 |
| 「他們看起來做完了這個功能——我來提議捨棄它」 | 選單照原樣就是完整的。唯有你的人工夥伴親口要求時才會捨棄。 |
| 「『對，把它弄掉』就算確認」 | 只有輸入 `discard` 這個詞才授權刪除。 |
| 「PR 已經開了，worktree 現在只是多餘」 | PR 回饋就是在該 worktree 中修正的。它會一直留到工作落地為止。 |
| 「另一個 worktree 看起來過時了——我一併清理」 | 只清理 `.worktrees/` 或 `worktrees/` 之下的 worktree。其餘都屬於主環境。 |
| 「合併結果的失敗大概是 flaky」 | 合併結果一旦失敗就一切停止。在你調查期間，分支與 worktree 保持原位。 |
| 「基礎分支顯然是 main」 | 確認分叉點，或直接詢問。合併到錯誤的基礎分支要復原的成本很高。 |
| 「push 被拒絕——force-push 就能解決」 | 被拒絕的 push 表示遠端已經移動。調查一下；只有你的人工夥伴明確要求時才 force-push。 |
