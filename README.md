> 這是 [obra/superpowers](https://github.com/obra/superpowers) 的**繁體中文翻譯學習站**（`superpowers-zh-tw`）。
> 本 repo 只翻譯自然語言說明，保留技能名稱、指令、路徑、程式碼區塊與工具識別符，以維持安裝與運行行為。
> 英文原文請見上游 repo；安裝方式請依本站[安裝指南](install.html)。
>
> **目前對齊上游 `obra/superpowers` main `44c9b2d`（v6.2.0，2026-07-27）。** 上游有更新時，首頁「待辦事項 · 上游同步」面板會列出待翻譯項目。

# Superpowers · 繁體中文教學站

[Superpowers](https://github.com/obra/superpowers)（MIT License，© 2025 Jesse Vincent）是一套給 coding agent 的**完整軟體開發方法論**：建構在一組可組合的技能之上，加上確保 agent 會使用它們的開場指令。

本站把這套方法論完整中文化，包含兩層：

1. **全量翻譯**（可安裝）— `skills/` 底下的 14 個技能全部翻成繁體中文，指令、路徑、技能名照原樣，裝法跟上游一樣。
2. **深讀教學站**（GitHub Pages）— 中英逐段對照的閱讀站，外加 `docs/teaching/` 的策展式中文深讀解說。

**上線網站：<https://shumingyang-opencode.github.io/superpowers-zh-tw/>**

> **免責聲明**：本站為第三方社群教學站，**與 Jesse Vincent 或 Prime Radiant 無關**，不代表官方立場。Superpowers 為其權利人所有，本站僅在描述性／教學語境使用該名稱。

## 14 個技能

| 技能 | 分類 | 一句話 |
|---|---|---|
| using-superpowers | meta | 開場白：先檢查技能，再行動 |
| brainstorming | process | 動工前把點子敲成設計 |
| using-git-worktrees | process | 開工先開隔離的 worktree |
| writing-plans | process | 把設計拆成 2–5 分鐘的小任務 |
| subagent-driven-development | process | 逐任務派子代理實作，兩階段審查 |
| executing-plans | process | 另開 session 分批執行，人類檢查點 |
| dispatching-parallel-agents | process | 獨立任務平行派出去同時做 |
| requesting-code-review | process | 任務完成、發合併前送審 |
| receiving-code-review | process | 收到意見先想清楚再動手 |
| finishing-a-development-branch | process | 全綠之後決定合併／發 PR／保留 |
| test-driven-development | discipline | 紅 → 綠 → 重構，證據逼出好程式 |
| systematic-debugging | discipline | 四階段根因流程，先鎖住再挖根 |
| verification-before-completion | discipline | 宣告完成前先真的驗證 |
| writing-skills | meta | 寫技能本身也是 TDD |

> `using-superpowers` 另附 4 份 harness 參考文件（`antigravity-tools` / `codex-tools` / `gemini-tools` / `pi-tools`），也已全量中文化，並為每份生成中英對照頁。

## 網站地圖

```
superpowers-zh-tw/
├── index.html              首頁：入口卡 + 上游同步面板 + about 卡
├── map.html                全景圖：基本工作流 highway（開場→動工→計畫→執行→審查→收尾）
├── learning-path.html      學習路線 L0→L4
├── install.html            安裝指南：OpenCode / Claude Code / Codex / Cursor / Gemini / Copilot / Kimi / Antigravity / Factory Droid / Pi
├── about.html              作者 Jesse Vincent / 授權與聲明
├── docs/
│   ├── teaching/           深讀解說（5 頁 + hub）
│   ├── translation/glossary-zh-TW.md  翻譯詞彙表
│   └── upstream-status.json 上游同步狀態
├── assets/site.css         深色×霓虹設計語言
├── skills/                 可安裝的翻譯後技能（14 個，保留上游目錄結構）
├── <skill>/SKILL.html      每個技能的中英逐段對照頁（build 產出）
├── <skill>/<doc>.html      附屬文件逐段對照頁（prompt 範本、參考文件等）
└── scripts/
    ├── build-site.py       生成靜態站
    └── check-upstream.py   每月上游同步檢查
```

## 授權

- 上游 `obra/superpowers` 以 **MIT License** 釋出（Copyright © 2025 Jesse Vincent）。本站照抄上游授權檔：
  - [`LICENSE`](LICENSE) — MIT 全文
  - [`NOTICE`](NOTICE) — 非官方教學站聲明、引用範圍、原創內容授權
- **商標**：Superpowers 與 Prime Radiant 為其各自權利人所有。MIT 授權不含商標授權；本站僅在描述性／教學語境使用該名稱，並於全站 footer 標示「與 Prime Radiant 無關」。

## 上游同步

- 本站對齊上游分支 **`main`**，釘選 commit **`44c9b2d`**（v6.2.0）。
- `.github/workflows/check-upstream.yml` **每月自動**（每月 1 日 00:00 UTC + 手動觸發）檢查上游最新 SHA，並更新首頁的同步面板。

## 開發

```bash
# 1. 建 venv 並裝 markdown
python3 -m venv .venv
.venv/bin/pip install markdown

# 2. 生成靜態站（讀取 skills/ 的繁中 + 從 .site-cache 取英文原文）
.venv/bin/python scripts/build-site.py

# 3. 本機預覽
python3 -m http.server 8000
```

- 上游英文原文快取在 `.site-cache/`（gitignore），重跑不需網路。
- 翻譯詞彙表見 [`docs/translation/glossary-zh-TW.md`](docs/translation/glossary-zh-TW.md)。

## 回饋與貢獻

- 本站是教學站，不是官方文件。發現翻譯錯誤或想補充主題，歡迎開 [issue](https://github.com/shumingyang-opencode/superpowers-zh-tw/issues)。
- 想翻譯新版本的上游變更：先跑 `check-upstream.py` 看待辦，再依翻譯詞彙表逐項處理。

**相關連結**

- 上游 repo：[obra/superpowers](https://github.com/obra/superpowers)（MIT）
- 作者：[Jesse Vincent](https://blog.fsck.com) · [Prime Radiant](https://primeradiant.com)
- 本站 repo：[shumingyang-opencode/superpowers-zh-tw](https://github.com/shumingyang-opencode/superpowers-zh-tw)
- 本站上線：[shumingyang-opencode.github.io/superpowers-zh-tw](https://shumingyang-opencode.github.io/superpowers-zh-tw/)
