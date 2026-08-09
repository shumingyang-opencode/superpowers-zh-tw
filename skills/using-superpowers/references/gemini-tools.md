# Gemini CLI 工具對應

技能用行動來表達（「派遣子代理」、「建立 todo」、「讀取檔案」）。在 Gemini CLI 上，這些會對應到下方的工具。

| 技能要求的行動 | Gemini CLI 的對應 |
|----------------------|----------------------|
| 讀取檔案 | `read_file` |
| 一次讀取多個檔案 | `read_many_files` |
| 建立新檔案 | `write_file` |
| 編輯檔案 | `replace` |
| 執行 shell 指令 | `run_shell_command` |
| 搜尋檔案內容 | `grep_search` |
| 依名稱尋找檔案 | `glob` |
| 列出檔案與子目錄 | `list_directory` |
| 擷取 URL | `web_fetch` |
| 搜尋網路 | `google_web_search` |
| 呼叫技能 | `activate_skill` |
| 派遣子代理（`Subagent (general-purpose):` 範本） | 使用 `agent_name: "generalist"` 的 `invoke_agent`（可經由 `@generalist` 聊天語法呼叫——見 [子代理支援](#子代理支援)） |
| 多次平行派遣 | 在同一個回應中多次 `invoke_agent` 呼叫 |
| 任務追蹤（「建立 todo」、「標記完成」） | `write_todos`（狀態：pending、in_progress、completed、cancelled、blocked） |

## 指令檔

當技能提到「你的指令檔」時，在 Gemini CLI 上它是 **`GEMINI.md`**。Gemini CLI 階層式載入 `GEMINI.md`：全域在 `~/.gemini/GEMINI.md`，專案層級的檔案在 workspace 目錄及其上層，而當工具存取某目錄中的檔案時，會載入該目錄下的 `GEMINI.md`。

## 個人技能目錄

使用者層級的技能位於 **`~/.gemini/skills/`**，而 **`~/.agents/skills/`** 是跨執行環境的別名（與 Codex 和 Copilot CLI 共用）。當同一個作用域同時存在兩個目錄時，`.agents/skills/` 優先。每個技能是包含 `SKILL.md`（帶有 `name` 與 `description` frontmatter）的子目錄。

## 子代理支援

Gemini CLI 透過 `invoke_agent` 工具派遣子代理，該工具接受 `agent_name` 與 `prompt` 參數。同樣的派遣也以聊天語法捷徑呈現：輸入 `@generalist <prompt>` 等同於以 `agent_name: "generalist"` 呼叫 `invoke_agent`。內建代理名稱包括 `generalist`、`cli_help`、`codebase_investigator`，以及（啟用瀏覽器工具時）`browser_agent`。

技能以 `Subagent (general-purpose):` 派遣，並參照 prompt 範本檔（例如 `superpowers:subagent-driven-development` 的 `./implementer-prompt.md`）或提供內嵌 prompt。在 Gemini CLI 上：

| 技能派遣形式 | Gemini CLI 的對應 |
|---------------------|----------------------|
| 參照 `*-prompt.md` 範本（implementer、task-reviewer、code-reviewer 等） | 填入範本，然後以 `agent_name: "generalist"` 與填入後的 prompt 呼叫 `invoke_agent` |
| 參照 `superpowers:requesting-code-review` 的 `./code-reviewer.md` | 以 `agent_name: "generalist"` 與填入後的審查範本呼叫 `invoke_agent` |
| 內嵌 prompt（未參照範本） | 以 `agent_name: "generalist"` 與你的內嵌 prompt 呼叫 `invoke_agent` |

### 填入 prompt

技能提供帶有 `{WHAT_WAS_IMPLEMENTED}` 或 `[FULL TEXT of task]` 這類佔位符的 prompt 範本。在把完整 prompt 傳給 `invoke_agent` 之前，先填入所有佔位符。prompt 範本本身包含代理的角色、審查準則與預期輸出格式——子代理會遵循它。

### 平行派遣

Gemini CLI 支援平行子代理派遣。在同一個回應中發出多次 `invoke_agent` 呼叫（或在一個 prompt 中多次 `@generalist` 呼叫），即可平行執行獨立的子代理工作。相依的任務保持循序，但不要只是為了維持更簡單的歷史而把獨立的子代理任務序列化。

## 其他 Gemini CLI 工具

這些工具是 Gemini CLI 獨有的：

| 工具 | 用途 |
|------|---------|
| `save_memory`（legacy） | 當 `experimental.memoryV2 = false` 時，跨 session 持久化事實 |
| `get_internal_docs` | 查閱 Gemini CLI 內建的說明文件 |
| `ask_user` | 向使用者提出結構化問題（文字／單選／多選） |
| `enter_plan_mode` / `exit_plan_mode` | 進入與離開唯讀 plan 模式 |
| `update_topic` | 更新目前對話的主題／策略意圖中繼資料 |
| `complete_task` | 告知某個 Gemini 子代理已完成，並把結果回傳給父代理 |
| `tracker_create_task`、`tracker_update_task`、`tracker_get_task`、`tracker_list_tasks`、`tracker_add_dependency`、`tracker_visualize` | 具備相依與視覺化支援的豐富任務追蹤器 |
| `read_mcp_resource`、`list_mcp_resources` | MCP 資源存取 |
