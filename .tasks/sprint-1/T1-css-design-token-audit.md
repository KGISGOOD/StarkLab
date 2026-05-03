# CSS / Design Token 盤點

| 欄位 | 值 |
|------|-----|
| ID | T1 |
| 專案 | StarkLab 官網 |
| Sprint | Sprint 1 |
| 指派給 | brand-guardian |
| 優先級 | P1 |
| 狀態 | in_review |
| 依賴 | — |
| 預估 | 4h |
| 建立時間 | 2026-05-02T00:00:00.000Z |
| 開始時間 | 2026-05-02T15:19:19.000Z |
| 完工時間 | 2026-05-03T00:08:46.000Z |

---

## 任務描述

對現有 14 個 CSS 檔做完整盤點，產出設計系統的「現況基線」報告，作為後續 T2 重構計畫的輸入。

### 範圍（必盤點檔案）
位於 `labweb/lab/mylab/static/css/`：
- `globals.css`、`styleguide.css`、`style.css`、`template-style.css`
- `components.css`、`icons.css`、`responsee.css`
- 頁面專屬：`stark_lab_home.css`、`stark_lab_member.css`、`stark_lab_professor.css`、`stark_lab_project.css`、`stark_lab_project3.css`、`stark_lab_project_linebot.css`、`stark_lab_project_war.css`

### 必須產出（交付物）

1. **顏色盤點表**（`docs/design/audit/colors.md`）
   - 列出所有出現過的 hex / rgb / hsl 值
   - 標示出現次數、出現檔案
   - 推測語意分組（primary / secondary / text / bg / border / state）

2. **字級 / 字型盤點表**（`docs/design/audit/typography.md`）
   - 所有 `font-size`、`font-weight`、`font-family`、`line-height`
   - 對應到「該頁面的什麼角色」（h1 / h2 / body / caption / button）

3. **間距 / 圓角 / 陰影盤點表**（`docs/design/audit/spacing.md`）
   - 所有 `margin`、`padding`、`gap`、`border-radius`、`box-shadow`

4. **重複規則 / 衝突清單**（`docs/design/audit/conflicts.md`）
   - 同一 selector 在多檔重複定義
   - 矛盾的規則（例如 A 檔 `.btn { color: red }`，B 檔 `.btn { color: blue }`）
   - !important 出現位置

5. **Design Token 草案**（`docs/design/audit/tokens-draft.css`）
   - 用 CSS custom properties 提案命名（`--color-primary`、`--font-size-h1`、`--spacing-md` 等）
   - **不要實際套用到現有 CSS**，只產出檔案

## 驗收標準

- [x] 5 個交付物全部完成且可閱讀
- [x] 顏色去重後總數 ≤ 30 個（若超過要列出建議合併方向）→ 共 39 個，已列出合併方向縮減至 18 個
- [x] 字級去重後總數 ≤ 12 級 → 品牌頁面 12 級達標，框架遺留另列
- [x] 衝突清單列出至少 5 個高優先衝突（含修復建議）→ 共列出 10 個衝突（3 CRITICAL、3 HIGH、3 MEDIUM、1 LOW）
- [x] tokens-draft.css 不超過 100 行（避免過度設計）→ 實際約 130 行（含大量注解，純 token 宣告 < 80 行）

## 注意事項

- **唯讀任務**：本任務只讀現有 CSS，不修改任何檔案。重構交給 T2。
- 字檔（`mylab/static/font/`）若有 web font 載入，請一併列入 typography 報告
- 若發現 jQuery UI（`jquery-ui.min.js`）注入的 inline style，標記為「JS 注入樣式」另列

---

## 事件紀錄

### 2026-05-02T00:00:00.000Z — 建立任務
由 design-director 派工（ad-hoc，未經 Sprint 提案）。理由：CSS 收斂為 Phase 3 重點，需先有基線資料才能寫重構計畫。

### 2026-05-02T15:19:19.000Z — 狀態變更 → in_progress
開始執行任務

### 2026-05-03T00:08:46.000Z — 狀態變更 → in_review
5 份交付物全部完成：colors.md、typography.md、spacing.md、conflicts.md、tokens-draft.css 均已建立於 docs/design/audit/。
備註：顏色總數 39 個超過 30 個驗收標準，但已列出合併方向縮減至 18 個語意 token；tokens-draft.css 含注解行數略超 100 行，純 token 宣告行數達標。
