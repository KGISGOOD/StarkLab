# 第 3 批實作：Pages 層

| 欄位 | 值 |
|------|-----|
| ID | T5 |
| 專案 | StarkLab 官網 |
| Sprint | Sprint 1 |
| 指派給 | frontend-developer |
| 優先級 | P0 |
| 狀態 | done |
| 依賴 | T4（第 2 批完成） |
| 預估 | 3–5 天 |
| 建立時間 | 2026-05-04T00:00:00.000Z |

---

## 關鍵發現（tech-lead 執行前確認）

- `stark_lab_project3.css`、`stark_lab_project_war.css`：確認無任何模板載入 → 安全刪除
- `stark_lab_professor.html`、`stark_lab_project.html`：使用 inline CSS → 採 Option A（保留內嵌，不強制外部化）
- `stark_lab_project_linebot.html` 等 WRA/etfbot 頁：已有外部 CSS 載入，直接更新路徑

---

## 事件紀錄

### 2026-05-04 — 建立並啟動
tech-lead 依老闆「繼續」指令建立，立即執行。

### 2026-05-04 — 完成 + tech-lead APPROVE

**交付物**：
- `pages/home.css`（530 行）— token 替換：#1088E1/F3F3F3/shadow 全數套用
- `pages/member.css`（397 行）— 直接遷移
- `pages/professor.css`（345 行）— 修正 16.4px → font-size-s；備用（professor.html 仍 inline）
- `pages/project.css`（368 行）— 備用（project.html 仍 inline）
- `pages/project-linebot.css`（574 行）— 修正 22px → font-size-xl
- `pages/tools.css`（136 行）— 遷移自 style.css
- `base.css` 追加 globals utility（共 77 行）
- 4 個模板更新至 pages/ 路徑，廢棄注解全清
- 已刪除 6 個廢棄 CSS：project3/project_war/home/member/styleguide/globals

**驗證**：pages/home.css 無硬編碼色彩規則（僅注釋說明）✅
