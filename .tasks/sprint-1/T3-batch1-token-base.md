# 第 1 批實作：Token 層 + Base 層

| 欄位 | 值 |
|------|-----|
| ID | T3 |
| 專案 | StarkLab 官網 |
| Sprint | Sprint 1 |
| 指派給 | frontend-developer |
| 優先級 | P0 |
| 狀態 | done |
| 依賴 | T2（計畫書審核通過） |
| 預估 | 1 天 |
| 建立時間 | 2026-05-03T00:00:00.000Z |

---

## 任務描述

按照 `docs/design/refactor-plan.md` 第 1 批計畫，建立 `tokens.css` 與 `base.css`，並在受影響的模板加入 `<link>` tag。

**原則**：不修改任何現有 CSS 檔案；只新增檔案、只在 HTML 加 `<link>` tag。

---

## 交付物

1. `mylab/static/css/tokens.css`
2. `mylab/static/css/base.css`
3. 5 個 HTML 模板各加入新 `<link>` tag

---

## 事件紀錄

### 2026-05-03 — 建立並啟動
tech-lead 依老闆「開始」指令建立，立即執行。

### 2026-05-03 — 完成 + tech-lead APPROVE

**交付物**：
- `mylab/static/css/tokens.css`（201 行）— 含新 token 系統 + 8 個舊名稱別名映射
- `mylab/static/css/base.css`（42 行）— 含 Google Fonts、2 個衝突修正 override、box-sizing
- 5 個模板已插入 `tokens.css`（最前）和 `base.css`（framework CSS 之後）

**驗證通過**：無 AnimaApp 追蹤像素；index.html 載入順序正確。

**Minor**：日期標 2026-05-02（應為 2026-05-03），下次修正。
