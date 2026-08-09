## 子代理派遣需要 multi-agent 支援

在你的 Codex 設定（`~/.codex/config.toml`）加入：

```toml
[features]
multi_agent = true
```

這會為 `dispatching-parallel-agents` 與 `subagent-driven-development` 這類技能啟用 `spawn_agent`、`wait_agent` 與 `close_agent`。使用 subagent-driven-development 時，審查子代理的回報一送回就關閉它。每個實作子代理則保持開啟，直到其任務的審查通過——修復迴圈會續用該實作子代理——然後才關閉。如果你的 harness 無法向已產生的代理再送訊息，就把每一輪修復派成一個新的實作子代理，攜帶 brief、報告檔與審查發現。

## 環境偵測

建立 worktree 或收尾分支的技能，應該先用唯讀 git 指令偵測環境再繼續：

```bash
GIT_DIR=$(cd "$(git rev-parse --git-dir)" 2>/dev/null && pwd -P)
GIT_COMMON=$(cd "$(git rev-parse --git-common-dir)" 2>/dev/null && pwd -P)
BRANCH=$(git branch --show-current)
```

- `GIT_DIR != GIT_COMMON` → 已在關聯的 worktree 中（跳過建立）
- `BRANCH` 為空 → detached HEAD（無法從 sandbox 建立分支／推送／發 PR）

關於各技能如何使用這些訊號，見 `using-git-worktrees` 的第 0 步與 `finishing-a-development-branch` 的第 1 步。

## Codex App 收尾

當 sandbox 阻擋分支／推送操作（在外部管理的 worktree 中處於 detached HEAD），代理提交所有工作並告知使用者改用 App 的原生控制：

- **「Create branch」** — 命名分支，然後透過 App UI 提交／推送／發 PR
- **「Hand off to local」** — 把工作轉移給使用者的本機 checkout

代理仍然可以執行測試、暫存檔案，並輸出建議的分支名稱、commit 訊息與 PR 描述供使用者複製。
