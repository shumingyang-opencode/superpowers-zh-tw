# 縱深防禦驗證

## 概述

當你修好一個由無效資料造成的 bug 時，只在一處加入驗證，感覺上就足夠了。但這個單一檢查可能被不同的程式路徑、重構或模擬繞過。

**核心原則：** 在資料流經的「每一層」都做驗證。讓這個 bug 在結構上變得不可能發生。

## 為什麼要多層

單一驗證：「我們修好了這個 bug」
多層驗證：「我們讓這個 bug 不可能發生」

不同的層次捕捉不同的情況：
- 進入點驗證捕捉大部分的 bug
- 業務邏輯捕捉邊角情況
- 環境守衛防止與特定情境相關的危險
- 除錯日誌在其他層失守時派上用場

## 四層架構

### 第一層：進入點驗證
**目的：** 在 API 邊界拒絕明顯無效的輸入

```typescript
function createProject(name: string, workingDirectory: string) {
  if (!workingDirectory || workingDirectory.trim() === '') {
    throw new Error('workingDirectory cannot be empty');
  }
  if (!existsSync(workingDirectory)) {
    throw new Error(`workingDirectory does not exist: ${workingDirectory}`);
  }
  if (!statSync(workingDirectory).isDirectory()) {
    throw new Error(`workingDirectory is not a directory: ${workingDirectory}`);
  }
  // ... proceed
}
```

### 第二層：業務邏輯驗證
**目的：** 確保資料對這項操作來說是合理的

```typescript
function initializeWorkspace(projectDir: string, sessionId: string) {
  if (!projectDir) {
    throw new Error('projectDir required for workspace initialization');
  }
  // ... proceed
}
```

### 第三層：環境守衛
**目的：** 防止在特定情境下執行危險操作

```typescript
async function gitInit(directory: string) {
  // In tests, refuse git init outside temp directories
  if (process.env.NODE_ENV === 'test') {
    const normalized = normalize(resolve(directory));
    const tmpDir = normalize(resolve(tmpdir()));

    if (!normalized.startsWith(tmpDir)) {
      throw new Error(
        `Refusing git init outside temp dir during tests: ${directory}`
      );
    }
  }
  // ... proceed
}
```

### 第四層：除錯儀器
**目的：** 擷取上下文以供事後調查

```typescript
async function gitInit(directory: string) {
  const stack = new Error().stack;
  logger.debug('About to git init', {
    directory,
    cwd: process.cwd(),
    stack,
  });
  // ... proceed
}
```

## 套用這個模式

當你發現一個 bug 時：

1. **追蹤資料流** —— 壞值從哪裡來？用到哪裡？
2. **列出所有檢查點** —— 列出資料流經的每一處
3. **在每一層加入驗證** —— 進入點、業務、環境、除錯
4. **測試每一層** —— 試著繞過第一層，驗證第二層會攔住它

## 來自 session 的範例

Bug：空的 `projectDir` 導致 `git init` 執行在原始碼目錄

**資料流：**
1. 測試設定 → 空字串
2. `Project.create(name, '')`
3. `WorkspaceManager.createWorkspace('')`
4. `git init` 在 `process.cwd()` 執行

**加入的四層：**
- 第一層：`Project.create()` 驗證非空/存在/可寫
- 第二層：`WorkspaceManager` 驗證 projectDir 非空
- 第三層：測試中 `WorktreeManager` 拒絕在 tmpdir 之外執行 git init
- 第四層：git init 之前記錄堆疊追蹤

**結果：** 全部 1847 個測試通過，bug 無法重現

## 關鍵領悟

四層都是必要的。測試過程中，每一層都捕捉了其他層漏掉的 bug：
- 不同的程式路徑繞過了進入點驗證
- 模擬繞過了業務邏輯檢查
- 不同平台上的邊角情況需要環境守衛
- 除錯日誌辨識出結構性的誤用

**不要只停在一個驗證點。** 在每一層都加入檢查。
