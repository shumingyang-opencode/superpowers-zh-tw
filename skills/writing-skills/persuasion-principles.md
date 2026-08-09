# 技能設計的說服原則

## 總覽

LLM 對說服原則的反應與人類相同。了解這層心理學有助於你設計更有效的技能——不是為了操控，而是確保關鍵做法即使在壓力下也被遵循。

**研究基礎：**Meincke 等人（2025）以 N=28,000 次 AI 對話測試了 7 條說服原則。說服技巧讓遵從率翻倍以上（33% → 72%，p < .001）。

## 七大原則

### 1. 權威
**它是什麼：**對專業、資歷或官方來源的服從。

**在技能中的運作方式：**
- 命令式語氣：「YOU MUST」、「Never」、「Always」
- 不可協商的框架：「No exceptions」
- 消除決策疲勞與合理化藉口

**使用時機：**
- 紀律執行類技能（TDD、驗證需求）
- 安全關鍵的做法
- 已確立的最佳實務

**範例：**
```markdown
✅ Write code before test? Delete it. Start over. No exceptions.
❌ Consider writing tests first when feasible.
```

### 2. 承諾
**它是什麼：**與先前行動、陳述或公開宣言保持一致。

**在技能中的運作方式：**
- 要求宣告：「Announce skill usage」
- 強制明確選擇：「Choose A, B, or C」
- 使用追蹤：檢查清單的待辦事項

**使用時機：**
- 確保技能真的被遵循
- 多步驟流程
- 問責機制

**範例：**
```markdown
✅ When you find a skill, you MUST announce: "I'm using [Skill Name]"
❌ Consider letting your partner know which skill you're using.
```

### 3. 稀缺
**它是什麼：**來自時間限制或有限可用性的急迫感。

**在技能中的運作方式：**
- 有時限的需求：「Before proceeding」
- 順序相依：「Immediately after X」
- 防止拖延

**使用時機：**
- 需要立即驗證的需求
- 對時間敏感的工作流
- 防止「我晚點再做」

**範例：**
```markdown
✅ After completing a task, IMMEDIATELY request code review before proceeding.
❌ You can review code when convenient.
```

### 4. 社會認同
**它是什麼：**順從他人的行為或被視為常態的做法。

**在技能中的運作方式：**
- 普遍模式：「Every time」、「Always」
- 失敗模式：「X without Y = failure」
- 建立規範

**使用時機：**
- 記錄普遍做法
- 提醒常見失敗
- 強化標準

**範例：**
```markdown
✅ Checklists without todo tracking = steps get skipped. Every time.
❌ Some people find a todo list helpful for checklists.
```

### 5. 團結
**它是什麼：**共享的身分認同、「我們感」、內團體歸屬感。

**在技能中的運作方式：**
- 協作式語言：「our codebase」、「we're colleagues」
- 共享目標：「we both want quality」

**使用時機：**
- 協作工作流
- 建立團隊文化
- 非階層式做法

**範例：**
```markdown
✅ We're colleagues working together. I need your honest technical judgment.
❌ You should probably tell me if I'm wrong.
```

### 6. 互惠
**它是什麼：**回報所受好處的義務。

**運作方式：**
- 謹慎使用——可能感覺像操控
- 在技能中很少需要

**避免時機：**
- 幾乎永遠（其他原則更有效）

### 7. 喜好
**它是什麼：**偏好與我們喜歡的人合作。

**運作方式：**
- **不要用於要求遵從**
- 與誠實回饋的文化衝突
- 產生奉承討好

**避免時機：**
- 在紀律執行上永遠避免

## 依技能類型的原則組合

| 技能類型 | 使用 | 避免 |
|------------|-----|-------|
| 紀律執行類 | 權威 + 承諾 + 社會認同 | 喜好、互惠 |
| 指引／技術類 | 適度權威 + 團結 | 重度權威 |
| 協作類 | 團結 + 承諾 | 權威、喜好 |
| 參考文件類 | 僅需清楚明確 | 所有說服技巧 |

## 為何有效：心理學原理

**明確紅線規則減少合理化藉口：**
- 「YOU MUST」消除決策疲勞
- 絕對性語言消除「這是不是例外？」的疑問
- 明確的反合理化反制封閉特定漏洞

**執行意圖創造自動化行為：**
- 清楚的觸發條件 + 必須採取的動作 = 自動執行
- 「When X, do Y」比「generally do Y」更有效
- 降低遵從的認知負荷

**LLM 是類人的：**
- 以包含這些模式的人類文字訓練
- 訓練資料中，權威式語言先於遵從出現
- 承諾序列（陳述 → 行動）經常被建模
- 社會認同模式（everyone does X）建立規範

## 倫理使用

**正當用途：**
- 確保關鍵做法被遵循
- 建立有效的文件
- 防止可預期的失敗

**不正當用途：**
- 為個人利益操控
- 製造虛假的急迫感
- 以罪惡感脅迫遵從

**判準：**如果使用者完全理解這項技巧，它是否仍服務於使用者的真實利益？

## 研究引用

**Cialdini, R. B. (2021).** *Influence: The Psychology of Persuasion (New and Expanded).* Harper Business.
- 說服的七大原則
- 影響力研究的實證基礎

**Meincke, L., Shapiro, D., Duckworth, A. L., Mollick, E., Mollick, L., & Cialdini, R. (2025).** Call Me A Jerk: Persuading AI to Comply with Objectionable Requests. University of Pennsylvania.
- 以 N=28,000 次 LLM 對話測試了 7 條原則
- 使用說服技巧後遵從率從 33% 提升至 72%
- 權威、承諾、稀缺最有效
- 驗證 LLM 行為的類人模型

## 快速參考

設計技能時，問自己：

1. **它是哪種類型？**（紀律 vs. 指引 vs. 參考文件）
2. **我想改變什麼行為？**
3. **適用哪些原則？**（紀律類通常用權威 + 承諾）
4. **我是否混用了太多？**（不要用全部七個）
5. **這是否符合倫理？**（是否服務於使用者的真實利益？）
