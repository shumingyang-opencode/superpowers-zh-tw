# Pi 工具對應

技能用行動來表達（「派遣子代理」、「建立 todo」、「讀取檔案」）。在 Pi 上，這些會對應到下方的工具。

| 技能要求的行動 | Pi 的對應 |
| --- | --- |
| 派遣子代理（`Subagent (general-purpose):` 範本） | 如果可用，使用已安裝的子代理工具，例如 `pi-subagents` 的 `subagent` |
| 任務追蹤（「建立 todo」、「標記完成」） | 如果可用，使用已安裝的 todo／task 工具，否則在計畫或 `TODO.md` 中追蹤任務 |

## 子代理

Pi 核心未附標準子代理工具。`pi-subagents` 套件是強而有力的選用搭配，提供具備單一代理、鏈式、平行、非同步、分支上下文與 resume／status 工作流的 `subagent` 工具。如果沒有可用的子代理工具，不要捏造 `Task` 呼叫；在目前 session 中循序執行，或說明選用的子代理能力尚未安裝。

## 任務清單

Pi 核心未附標準任務清單工具。如果已安裝 todo／task 擴充，就使用其文件化的工具。否則使用 Superpowers 計畫檔、Markdown 檢查清單，或 repo 本機的 `TODO.md` 來追蹤任務。較舊的 Superpowers 文件可能稱之為 `TodoWrite`；把它視為上述的任務追蹤行動即可。
