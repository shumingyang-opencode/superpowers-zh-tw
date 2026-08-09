---
name: verification-before-completion
description: 當你正要宣稱工作已完成、已修正或通過，在 commit 或建立 PR 之前使用 —— 要求執行驗證指令並確認輸出，之後才能作出任何成功的宣稱；永遠先有證據再有斷言
---

# 完成前的驗證

## 總覽

**核心原則：** 先有證據，再有宣稱，永遠如此。

**違反這條規則的字面意義，就是違反它的精神。**

## 鐵律

```
NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE
```

如果你沒有在這一則訊息中執行驗證指令，你就不能宣稱它通過。

## 守門函式

```
BEFORE claiming any status or expressing satisfaction:

1. IDENTIFY: What command proves this claim?
2. RUN: Execute the FULL command (fresh, complete)
3. READ: Full output, check exit code, count failures
4. VERIFY: Does output confirm the claim?
   - If NO: State actual status with evidence
   - If YES: State claim WITH evidence
5. ONLY THEN: Make the claim

Skip any step = lying, not verifying
```

## 常見失敗

| 宣稱 | 需要 | 不足夠 |
|-------|----------|----------------|
| 測試通過 | 測試指令輸出：0 失敗 | 之前跑過、「應該會過」 |
| Linter 乾淨 | Linter 輸出：0 錯誤 | 部分檢查、推論 |
| 建置成功 | 建置指令：exit 0 | Linter 通過、日誌看起來正常 |
| Bug 已修正 | 測試原始症狀：通過 | 改了程式碼、假定已修好 |
| 回歸測試有效 | 驗證過紅 → 綠循環 | 測試通過一次 |
| 代理已完成 | VCS diff 顯示變更 | 代理回報「成功」 |
| 需求已滿足 | 逐行檢查清單 | 測試通過 |

## 紅旗 - 停下

- 使用「應該」「大概」「似乎」
- 在驗證之前表達滿意（「太棒了！」「完美！」「完成了！」等）
- 在未驗證的情況下即將 commit/push/PR
- 相信代理的成功回報
- 依賴部分驗證
- 心想「就這麼一次」
- 累了，想讓工作結束
- **任何暗示成功、但其實沒執行驗證的措辭**

## 防止合理化

| 藉口 | 事實 |
|--------|---------|
| 「現在應該能用了」 | 執行驗證 |
| 「我有信心」 | 信心 ≠ 證據 |
| 「就這麼一次」 | 沒有例外 |
| 「Linter 過了」 | Linter ≠ 編譯器 |
| 「代理說成功了」 | 獨立驗證 |
| 「我累了」 | 疲憊 ≠ 藉口 |
| 「部分檢查就夠了」 | 部分什麼都證明不了 |
| 「換句話說所以規則不適用」 | 精神優先於字面 |

## 關鍵模式

**測試：**
```
✅ [Run test command] [See: 34/34 pass] "All tests pass"
❌ "Should pass now" / "Looks correct"
```

**回歸測試（TDD 紅-綠）：**
```
✅ Write → Run (pass) → Revert fix → Run (MUST FAIL) → Restore → Run (pass)
❌ "I've written a regression test" (without red-green verification)
```

**建置：**
```
✅ [Run build] [See: exit 0] "Build passes"
❌ "Linter passed" (linter doesn't check compilation)
```

**需求：**
```
✅ Re-read plan → Create checklist → Verify each → Report gaps or completion
❌ "Tests pass, phase complete"
```

**代理委派：**
```
✅ Agent reports success → Check VCS diff → Verify changes → Report actual state
❌ Trust agent report
```

## 何時套用

**一律在以下之前：**
- 任何形式的成功/完成宣稱
- 任何滿意的表達
- 任何關於工作狀態的正面陳述
- Commit、建立 PR、任務完成
- 進行到下一個任務
- 委派給代理

**規則適用的範圍：**
- 確切的措辭
- 改寫與同義詞
- 成功的暗示
- 任何暗示完成/正確的溝通
