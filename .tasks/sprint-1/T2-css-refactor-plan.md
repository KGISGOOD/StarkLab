# CSS 收斂重構計畫

| 欄位 | 值 |
|------|-----|
| ID | T2 |
| 專案 | StarkLab 官網 |
| Sprint | Sprint 1 |
| 指派給 | ui-designer |
| 優先級 | P1 |
| 狀態 | done |
| 依賴 | T1 |
| 預估 | 6h |
| 建立時間 | 2026-05-02T00:00:00.000Z |

---

## 任務描述

依據 T1 的盤點結果，產出 CSS 三層架構的重構計畫書（**只寫計畫、不動 code**）。

### 目標架構（三層）

```
mylab/static/css/
├── tokens.css              # 第 1 層：design token（變數）
├── base.css                # 第 2 層：reset + 全域排版
├── components/             # 第 3 層：可複用元件
│   ├── navbar.css
│   ├── card.css
│   ├── button.css
│   └── ...
└── pages/                  # 第 4 層：頁面差異樣式（盡量薄）
    ├── home.css
    ├── member.css
    └── ...
```

### 必須產出（交付物）

1. **重構計畫書**（`docs/design/refactor-plan.md`）章節：
   - **1. 收斂對應表**：14 個現有 CSS 檔 → 新架構的去處（哪些合併、哪些刪除、哪些改名）
   - **2. 元件清單**：從盤點結果抽出至少 6 個共用元件（navbar / footer / card / button / form / modal / hero）
   - **3. 遷移順序**：分 3 批，第 1 批（token + base）→ 第 2 批（components）→ 第 3 批（pages）
   - **4. 每批 diff-level 預覽**：列出每批會動的檔案清單（不寫實際 diff，只列檔名 + 動作）
   - **5. 風險與回滾策略**：每批失敗時如何 revert
   - **6. 驗收方法**：用截圖比對工具或 Playwright 視覺回歸驗證

2. **元件 API 草案**（`docs/design/components-api.md`）
   - 每個元件列出：用途、HTML 範例、可變變體（variant）、狀態（hover / active / disabled）

3. **影響評估**（`docs/design/impact.md`）
   - 列出 12 個 HTML 模板各自會被哪一批影響
   - 標示「高風險頁面」（首頁、含複雜 JS 互動的 financial_*.html）

### 重要約束

- **不得修改任何現有 CSS / HTML 檔**（只寫計畫）
- jQuery 1.8.3 升級不在本任務範圍（另案）
- 不得引入 Tailwind / Bootstrap / 任何 CSS framework（先把現況收乾淨）
- 計畫書要假設「老闆批了才動工」，所以每一步要可被獨立 review

## 驗收標準

- [ ] 3 份交付物完成
- [ ] 14 個 CSS 檔在收斂對應表中全部有歸屬（不能漏）
- [ ] 至少 6 個共用元件被抽出
- [ ] 遷移計畫分 3 批，每批可獨立 PR
- [ ] 風險評估涵蓋每批的回滾策略

---

## 事件紀錄

### 2026-05-02T00:00:00.000Z — 建立任務
由 design-director 派工，依賴 T1 完成後啟動。

### 2026-05-03 — T1 審核通過，T2 解鎖啟動

**tech-lead 技術 Review（T1 交付物）：**
- ✅ conflicts.md — 3 CRITICAL 衝突（linebot 三檔重複 / body 四檔覆蓋 / 4個藍色）已清楚標示，技術上可修復
- ✅ tokens-draft.css — token 命名語意清晰，transition / z-index token 補得好，T2 可直接用
- ✅ spacing.md — 100px 頁面水平邊距確認為全站標準，`--spacing-page-x` 命名正確
- ⚠️ 技術補充：`stark_lab_project3.css` 的固定高度 `height: 2851px` 是最高修復優先度（行動裝置致命 bug）

**tech-lead 技術輸入（T2 必讀）：**
- `docs/design/tech-constraints.md` — Django 靜態路徑規則、Template→CSS 依賴對應、JS 保護 class 清單、高風險頁面清單
- 9 個模板使用內嵌 `<style>`，T2 需在計畫中決定遷移策略（保留 or 外部化）
- `.expanded` 和 `.recording` class 受 JS 保護，禁止改名

**啟動時間**：2026-05-03

### 2026-05-03 — tech-lead Review：APPROVE

**驗收結果**：
- ✅ 3 份交付物完整（refactor-plan.md 16KB / components-api.md 15KB / impact.md 13KB）
- ✅ 14 個 CSS 檔全部有歸屬
- ✅ 8 個元件（超過最低 6 個）
- ✅ 3 批遷移計畫，每批可獨立 PR
- ✅ 每批有 git 回滾指令
- ✅ JS 保護 class（`.expanded`、`.recording`）明確標注
- ✅ 高風險頁面（financial / stock）排除或置最後批

**Minor（不阻擋）**：
1. 日期標為 2026-05-02 應為 2026-05-03（下次更新修正）
2. `stark_lab_project3.css` 刪除前需執行 `grep` 確認無模板引用（已在計畫書中標注）

T2 標為 done，計畫書提交設計師（design-director）final review 後方可向老闆提案動工。
