# 技術前置準備

| 欄位 | 值 |
|------|-----|
| ID | T0 |
| 專案 | StarkLab 官網 |
| Sprint | Sprint 1 |
| 指派給 | tech-lead |
| 優先級 | P0 |
| 狀態 | done |
| 依賴 | — |
| 預估 | 2h |
| 建立時間 | 2026-05-03T00:00:00.000Z |
| 完成時間 | 2026-05-03T00:00:00.000Z |

---

## 任務描述

CSS 重構前的技術環境掃描與約束文件產出，作為 T1/T2 的技術輸入。

## 交付物

- [x] `docs/design/tech-constraints.md` — Django 靜態路徑規則、Template→CSS 依賴對應表、JS 保護 class 清單、高風險頁面清單
- [x] `docs/design/audit/` 目錄建立（供 T1 存放盤點結果）

## 關鍵發現摘要

1. **9 個模板**使用內嵌 `<style>` 而非外部 CSS — T2 需決定遷移策略
2. **3 個模板**有廢棄注解 CSS link 待清理（home / etfbot / stock）
3. **受 JS 保護的 class**：`.expanded`（home 卡片）、`.recording`（translate 錄音）
4. **高風險頁面**：financial / stock（複雜 JS）
5. **collectstatic 自動遞迴**，新增子目錄無需額外設定

---

## 事件紀錄

### 2026-05-03 — 完成
tech-lead 自行執行，作為 T1/T2 並行啟動的技術支援。
