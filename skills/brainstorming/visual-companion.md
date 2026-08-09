# 視覺夥伴指南

以瀏覽器為基礎的視覺腦力激盪夥伴，用於展示 mockups、圖表與選項。

## 使用時機

逐問題決定，而非逐 session。判斷標準：**使用者「看」會比「讀」更容易理解嗎？**

**內容本身是視覺的，使用瀏覽器：**

- **UI mockups** ——線框圖、佈局、導覽結構、元件設計
- **架構圖** ——系統元件、資料流、關係圖
- **並排的視覺比較** ——比較兩種佈局、兩種配色、兩個設計方向
- **設計潤飾** ——當問題關於外觀與感受、間距、視覺層級
- **空間關係** ——以圖表呈現的狀態機、流程圖、實體關係

**內容是文字或表格的，使用終端機：**

- **需求與範圍問題** ——「X 是什麼意思？」、「哪些功能在範圍內？」
- **概念性的 A/B/C 選擇** ——在以文字描述的做法之間做選擇
- **取捨清單** ——優點／缺點、比較表
- **技術決策** ——API 設計、資料建模、架構做法選擇
- **釐清問題** ——任何答案是一段文字、而非視覺偏好的事物

一個*關於* UI 主題的問題不自動是視覺問題。「你想要哪種精靈？」是概念問題——使用終端機。「這些精靈佈局哪個感覺對？」是視覺問題——使用瀏覽器。

## 運作方式

伺服器監看一個目錄中的 HTML 檔案，並把最新的那份提供給瀏覽器。你把 HTML 內容寫到 `screen_dir`，使用者在其瀏覽器中看到它，並能點擊以選取選項。選取會被記錄到 `state_dir/events`，你可以在下一個回合讀取。

**內容片段 vs 完整文件：** 若你的 HTML 檔案以 `<!DOCTYPE` 或 `<html` 開頭，伺服器會原樣提供它（只注入 helper 腳本）。否則，伺服器會自動把你的內容包進 frame 範本——加上頁首、CSS 主題、連線狀態與所有互動基礎設施。**預設撰寫內容片段。** 只有在你需要完全掌控頁面時才撰寫完整文件。

## 啟動一個 session

```bash
# Start AFTER the user approves the companion. --open auto-opens their browser on
# the first screen; --project-dir persists mockups and enables same-port restart.
scripts/start-server.sh --project-dir /path/to/project --open

# Returns: {"type":"server-started","port":52341,
#           "url":"http://localhost:52341/?key=ab12…",
#           "screen_dir":"/path/to/project/.superpowers/brainstorm/12345-1706000000/content",
#           "state_dir":"/path/to/project/.superpowers/brainstorm/12345-1706000000/state"}
```

從回應中保存 `screen_dir` 與 `state_dir`。使用 `--open` 時，當你推送第一個畫面，瀏覽器會自動開啟——你不需要請使用者開啟它，但仍要分享 URL 作為備援（headless／遠端設定不會自動開啟）。

**URL 含有 session 金鑰（`?key=…`）。** 伺服器會拒絕任何沒有它的請求，所以務必給使用者 `url` 欄位中的**完整** URL——絕不要剝掉查詢字串，也絕不要交出一個裸的 `http://host:port`。金鑰把關 HTTP 與 WebSocket 的存取，因此閒置的瀏覽器分頁或網路上的另一台機器無法讀取畫面或注入事件。首次載入後，瀏覽器會透過 cookie 記住金鑰，因此重新載入與 `/files/*` 資源不需重複它。

**尋找連線資訊：** 伺服器把它的啟動 JSON 寫到 `$STATE_DIR/server-info`。若你在背景啟動伺服器且未擷取 stdout，讀取該檔案以取得 URL 與 port。使用 `--project-dir` 時，在 `<project>/.superpowers/brainstorm/` 檢查 session 目錄。

**注意：** 把專案根目錄以 `--project-dir` 傳入，讓 mockups 保存在 `.superpowers/brainstorm/` 中並在伺服器重啟後存活。沒有它的話，檔案會進到 `/tmp` 並被清理。提醒使用者把 `.superpowers/` 加入 `.gitignore`（若還沒有的話）。

**依平台啟動伺服器：**

**Claude Code：**
```bash
# Default mode works — the script backgrounds the server itself.
scripts/start-server.sh --project-dir /path/to/project --open
```

在 Windows 上，腳本會自動偵測並切換到前景模式（這會阻擋工具呼叫）。在 Bash 工具呼叫上使用 `run_in_background: true`，讓伺服器跨對話回合存活，然後在下一個回合讀取 `$STATE_DIR/server-info` 以取得 URL 與 port。

**Codex：**
```bash
# Codex reaps background processes. The script auto-detects CODEX_CI and
# switches to foreground mode. Run it normally — no extra flags needed.
scripts/start-server.sh --project-dir /path/to/project --open
```

**Gemini CLI：**
```bash
# Use --foreground and set is_background: true on your shell tool call
# so the process survives across turns
scripts/start-server.sh --project-dir /path/to/project --open --foreground
```

**Copilot CLI：**
```bash
# Use --foreground and start the server via the bash tool with mode: "async"
# so the process survives across turns. Capture the returned shellId for
# read_bash / stop_bash if you need to interact with it later.
scripts/start-server.sh --project-dir /path/to/project --open --foreground
```

**其他環境：** 伺服器必須在背景中跨對話回合持續執行。若你的環境會收割分離的 process，使用 `--foreground`，並以你平台的背景執行機制啟動指令。

若你的瀏覽器無法連到該 URL（在遠端／容器化設定中很常見），綁定一個非 loopback 的主機：

```bash
scripts/start-server.sh \
  --project-dir /path/to/project \
  --host 0.0.0.0 \
  --url-host localhost
```

使用 `--url-host` 控制回傳的 URL JSON 中印出哪個主機名稱。

## 迴圈

1. **檢查伺服器存活**，然後**把 HTML 寫入** `screen_dir` 中的一個新檔案：
   - **必要：在參照 URL 或推送畫面之前，先確認伺服器存活。** 檢查 `$STATE_DIR/server-info` 存在、且 `$STATE_DIR/server-stopped` 不存在。若它已關閉，用**相同的 `--project-dir`** 以 `start-server.sh` 重新啟動——它會重用相同的 port，因此使用者已開啟的分頁會自行重新連線（伺服器停機期間它會顯示「paused」覆蓋層），你也不需要寄送新 URL。伺服器在閒置 4 小時後自動結束（可用 `--idle-timeout-minutes` 設定）。
   - 使用語意化檔名：`platform.html`、`visual-style.html`、`layout.html`
   - **絕不重用檔名** ——每個畫面都使用新的檔案
   - 使用你的檔案建立工具——**絕不使用 cat/heredoc**（會把雜訊倒進終端機）
   - 伺服器自動提供最新的檔案

2. **告訴使用者會看到什麼並結束你的回合：**
   - 提醒他們 URL（每一步都要，不只是第一次）
   - 給出畫面上內容的簡短文字摘要（例如「顯示首頁的 3 種佈局選項」）
   - 請他們在終端機中回應：「看一下並讓我知道你的想法。若你願意，可以點擊選取一個選項。」

3. **在你的下一個回合** ——在使用者於終端機回應之後：
   - 若存在，讀取 `$STATE_DIR/events` ——它包含使用者的瀏覽器互動（點擊、選取），以 JSON 行格式呈現
   - 與使用者的終端機文字合併，取得完整樣貌
   - 終端機訊息是主要回饋；`state_dir/events` 提供結構化的互動資料

4. **迭代或前進** ——若回饋改變目前的畫面，寫入一個新檔案（例如 `layout-v2.html`）。只有目前步驟獲得驗證後才移動到下一個問題。

5. **回到終端機時卸載** ——當下一步不需要瀏覽器時（例如釐清問題、取捨討論），推送一個等待畫面以清除過時的內容：

   ```html
   <!-- filename: waiting.html (or waiting-2.html, etc.) -->
   <div style="display:flex;align-items:center;justify-content:center;min-height:60vh">
     <p class="subtitle">Continuing in terminal...</p>
   </div>
   ```

   這能防止使用者在對話已前進時，還盯著一個已解決的選擇。當下一個視覺問題出現時，照常推送新的內容檔案。

6. 重複直到完成。

## 撰寫內容片段

只撰寫會放進頁面內的內容。伺服器會自動把它包進 frame 範本（頁首、主題 CSS、連線狀態與所有互動基礎設施）。

**最小範例：**

```html
<h2>Which layout works better?</h2>
<p class="subtitle">Consider readability and visual hierarchy</p>

<div class="options">
  <div class="option" data-choice="a" onclick="toggleSelect(this)">
    <div class="letter">A</div>
    <div class="content">
      <h3>Single Column</h3>
      <p>Clean, focused reading experience</p>
    </div>
  </div>
  <div class="option" data-choice="b" onclick="toggleSelect(this)">
    <div class="letter">B</div>
    <div class="content">
      <h3>Two Column</h3>
      <p>Sidebar navigation with main content</p>
    </div>
  </div>
</div>
```

就是這樣。不需要 `<html>`、CSS 或 `<script>` 標籤。伺服器會提供所有這些。

## 可用的 CSS 類別

frame 範本為你的內容提供這些 CSS 類別：

### 選項（A/B/C 選擇）

```html
<div class="options">
  <div class="option" data-choice="a" onclick="toggleSelect(this)">
    <div class="letter">A</div>
    <div class="content">
      <h3>Title</h3>
      <p>Description</p>
    </div>
  </div>
</div>
```

**多重選取：** 在容器上加入 `data-multiselect`，讓使用者可以選取多個選項。每次點擊會切換該項目的選取樣式。

```html
<div class="options" data-multiselect>
  <!-- same option markup — users can select/deselect multiple -->
</div>
```

### 卡片（視覺設計）

```html
<div class="cards">
  <div class="card" data-choice="design1" onclick="toggleSelect(this)">
    <div class="card-image"><!-- mockup content --></div>
    <div class="card-body">
      <h3>Name</h3>
      <p>Description</p>
    </div>
  </div>
</div>
```

### Mockup 容器

```html
<div class="mockup">
  <div class="mockup-header">Preview: Dashboard Layout</div>
  <div class="mockup-body"><!-- your mockup HTML --></div>
</div>
```

### 分割檢視（並排）

```html
<div class="split">
  <div class="mockup"><!-- left --></div>
  <div class="mockup"><!-- right --></div>
</div>
```

### 優點／缺點

```html
<div class="pros-cons">
  <div class="pros"><h4>Pros</h4><ul><li>Benefit</li></ul></div>
  <div class="cons"><h4>Cons</h4><ul><li>Drawback</li></ul></div>
</div>
```

### Mock 元素（線框圖建構積木）

```html
<div class="mock-nav">Logo | Home | About | Contact</div>
<div style="display: flex;">
  <div class="mock-sidebar">Navigation</div>
  <div class="mock-content">Main content area</div>
</div>
<button class="mock-button">Action Button</button>
<input class="mock-input" placeholder="Input field">
<div class="placeholder">Placeholder area</div>
```

### 排版與區段

- `h2` ——頁面標題
- `h3` ——區段標題
- `.subtitle` ——標題下方的次要文字
- `.section` ——含底部邊距的內容區塊
- `.label` ——小號大寫標籤文字

## 瀏覽器事件格式

當使用者在瀏覽器中點擊選項時，他們的互動會被記錄到 `$STATE_DIR/events`（每行一個 JSON 物件）。當你推送新畫面時，檔案會自動清空。

```jsonl
{"type":"click","choice":"a","text":"Option A - Simple Layout","timestamp":1706000101}
{"type":"click","choice":"c","text":"Option C - Complex Grid","timestamp":1706000108}
{"type":"click","choice":"b","text":"Option B - Hybrid","timestamp":1706000115}
```

完整的事件串流顯示使用者的探索路徑——他們可能先點擊多個選項才定案。最後的 `choice` 事件通常是最終選取，但點擊模式可以透露出值得追問的猶豫或偏好。

若 `$STATE_DIR/events` 不存在，表示使用者沒有與瀏覽器互動——只使用他們的終端機文字。

## 設計提示

- **把擬真度對齊問題** ——佈局用線框圖，潤飾問題用潤飾
- **在每個頁面上說明問題** ——「哪種佈局感覺更專業？」而不只是「選一個」
- **前進之前先迭代** ——若回饋改變目前的畫面，寫入一個新版本
- 每個畫面**最多 2-4 個選項**
- **在重要時使用真實內容** ——對攝影作品集，使用真實的圖片（Unsplash）。佔位內容會掩蓋設計問題。
- **保持 mockups 簡單** ——聚焦於佈局與結構，而非像素完美的設計

## 檔名

- 使用語意化名稱：`platform.html`、`visual-style.html`、`layout.html`
- 絕不重用檔名——每個畫面都必須是新檔案
- 迭代時：加上版本後綴，例如 `layout-v2.html`、`layout-v3.html`
- 伺服器依修改時間提供最新的檔案

## 清理

```bash
scripts/stop-server.sh $SESSION_DIR
```

若 session 使用了 `--project-dir`，mockup 檔案會保存在 `.superpowers/brainstorm/` 中供日後參照。只有 `/tmp` session 會在停止時被刪除。

## 參考文件

- Frame 範本（CSS 參考）：`scripts/frame-template.html`
- Helper 腳本（用戶端）：`scripts/helper.js`
