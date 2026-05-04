# 第 2 批實作：Components 層

| 欄位 | 值 |
|------|-----|
| ID | T4 |
| 專案 | StarkLab 官網 |
| Sprint | Sprint 1 |
| 指派給 | frontend-developer |
| 優先級 | P0 |
| 狀態 | done |
| 依賴 | T3（第 1 批完成） |
| 預估 | 2–3 天 |
| 建立時間 | 2026-05-03T00:00:00.000Z |

---

## 任務描述

建立 `components/` 子目錄及 7 個元件 CSS，並在受影響模板加入 `<link>` tag。
原有 CSS 檔案中已提取的規則改為注解，避免重複定義。

---

## 事件紀錄

### 2026-05-03 — 建立並啟動
tech-lead 依老闆「繼續」指令建立，立即執行。

### 2026-05-03 — 完成 + tech-lead APPROVE

**交付物**：
- `components/` 目錄 + 7 個元件 CSS（navbar/card/button/footer/badge/photo-gallery/modal）
- `components.css` 加 3 處過渡期注解（規則保留）
- 5 個模板各加入對應 components `<link>` tag

**驗證通過**：`.expanded` 保護✅ / `.disabled-btn !important` 保留✅ / 載入順序正確✅
