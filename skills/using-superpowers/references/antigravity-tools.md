# Antigravity CLI（`agy`）工具對應

技能用行動來表達（「派遣子代理」、「建立 todo」、「讀取檔案」）。在 Antigravity CLI（`agy`）上，這些會對應到下方的工具。

| 技能要求的行動 | Antigravity CLI 的對應 |
|----------------------|----------------------|
| 派遣子代理（`Subagent (general-purpose):` 範本） | 使用內建 `TypeName` 的 `invoke_subagent`——完整能力的工作用 `self`，唯讀用 `research` |
| 任務追蹤（「建立 todo」、「標記完成」） | 一個 **task artifact**——以 `write_to_file` 搭配 `IsArtifact: true` 與 `ArtifactType: "task"`（見 [任務追蹤](#task-tracking)）。**不是** `manage_task`，那是管理背景行程用的。 |

## 任務追蹤

Antigravity **沒有 todo 工具**（`manage_task` 管理背景行程——`list`／`kill`／`status`／`send_input`——它_不是_檢查清單）。當技能要求建立 todo 清單或追蹤任務時，維護一個 **task artifact**：以 `write_to_file`（`IsArtifact: true`、`ArtifactMetadata.ArtifactType: "task"`）儲存的 markdown 檢查清單，邊進行邊用 `replace_file_content`／`multi_replace_file_content` 編輯。

任何多步驟任務開始時，建立列出你計畫中每個步驟的 task artifact。每完成一步，編輯該 artifact 把它標記為完成（`- [x]`）。如果計畫改變，更新檢查清單。保持它為最新——它是你「還剩下什麼」的真相來源；對話變長之後，在開始每一步之前重新讀它。
