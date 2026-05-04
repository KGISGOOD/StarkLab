# 產生 12 頁 baseline 視覺基準截圖

| 欄位 | 值 |
|------|-----|
| ID | T4 |
| 專案 | StarkLab 官網 |
| Sprint | Sprint 1 |
| 指派給 | ui-designer |
| 優先級 | P1 |
| 狀態 | done |
| 依賴 | — |
| 預估 | 3h |
| 建立時間 | 2026-05-02T00:00:00.000Z |

---

## 任務描述

為現有所有頁面產生 **desktop + mobile** 兩個 viewport 的 baseline 截圖，作為未來 CSS 重構（T2 計畫批准後的執行任務）的「外觀一致性驗收基準」。

### 背景

- StarkLab 沒有 `docs/design/mockup-*.html`（CLAUDE.md 規範該有但實際沒做）
- 現有 12+ 頁 HTML 模板就是 de facto 設計稿
- 設計總監決議：用截圖當基準，比補做正規 mockup 成本低 10 倍以上
- 重構目標是「**外觀不變、結構變乾淨**」，所以截圖比對就足夠

### 必須截的頁面（依 `lab/lab/urls.py`）

| URL | 模板 | 備註 |
|-----|------|------|
| `/` | stark_lab_home.html | 首頁，有摺疊卡片互動 |
| `/member/` | stark_lab_member.html | |
| `/professor/` | stark_lab_professor.html | |
| `/project/` | stark_lab_project.html | |
| `/project_linebot/` | stark_lab_project_linebot.html | |
| `/project_stock/` | stark_lab_project_stock.html | |
| `/project_wra/` | stark_lab_project_wra.html | |
| `/project_wra_repoet/` | stark_lab_project_wra_report.html | URL 有 typo，但實際路徑就是這樣 |
| `/project_ETFbot/` | stark_lab_project_etfbot.html | |
| `/project_financial/` | stark_lab_project_financial.html | |
| `/financial_1/` ~ `/financial_3/` | financial_{1,2,3}.html | 3 頁 |
| `/trans/` | stark_lab_trans.html | |

共 13 頁，每頁 2 個 viewport = **26 張截圖**

### Viewport 規格

| 名稱 | 寬度 | 高度 | 對應裝置 |
|------|------|------|---------|
| desktop | 1440 | 900 | 一般筆電 / 桌機 |
| mobile | 375 | 812 | iPhone X / 13 mini |

### 必須產出

1. **截圖檔**（位置：`docs/design/baseline/`）
   ```
   docs/design/baseline/
   ├── desktop/
   │   ├── home.png
   │   ├── member.png
   │   ├── professor.png
   │   └── ... (13 張)
   └── mobile/
       ├── home.png
       └── ... (13 張)
   ```

2. **截圖腳本**（位置：`scripts/baseline-screenshots.js` 或 `.py`）
   - 用 Playwright（首選）或 Puppeteer
   - 可重複執行（重構後跑一次同腳本，產出新截圖到 `docs/design/current/`）
   - 全頁滾動截圖（`fullPage: true`），不只 viewport 範圍
   - 等待 `networkidle` 後再截圖（避免抓到 loading state）

3. **截圖比對腳本**（位置：`scripts/visual-diff.js`）
   - 讀 `baseline/` 與 `current/` 兩組
   - 用 `pixelmatch` 或 `odiff` 算 pixel diff
   - 產出 `docs/design/diff-report.html`，並列每張的差異百分比
   - 任何頁面差異 > 1% 標紅

4. **README**（位置：`docs/design/README.md`）
   - 如何啟動 Django dev server（`./run_server.sh` 或 `python manage.py runserver`）
   - 如何執行截圖腳本
   - 如何跑視覺回歸比對
   - baseline 何時應該重新產生（規則：每次刻意改 UI 後）

## 驗收標準

- [ ] 26 張截圖產出完整，無破圖、無 loading state
- [ ] 腳本可重複執行（連跑兩次結果應一致）
- [ ] README 步驟對新人可重現
- [ ] 視覺比對腳本能正常產出 diff report
- [ ] 已驗證 diff report：用 baseline 自己 diff baseline，差異應為 0%

## 重要約束

- **不得修改任何現有 HTML / CSS / JS**（純讀取截圖）
- 啟動 dev server 時 `DEBUG` 維持 `False`（截圖內容應與 production 視覺一致）
- 若某頁面需登入或有 dynamic data（如 `/project_wra_repoet/` 可能依賴爬蟲資料），用 mock 或標註「需 fixture」
- Playwright 版本鎖定（寫進 `package.json` 的 devDependencies）

## 備註

- 此任務**不依賴 T1、T2**，可立即執行
- 與 T2 並行：ui-designer 可以同時兼顧（T2 是寫計畫、T4 是寫腳本，不衝突）
- 後續 CSS 重構執行任務會把「視覺 diff < 1%」列為驗收條件

---

## 事件紀錄

### 2026-05-02T00:00:00.000Z — 建立任務
由 design-director 派工。原因：StarkLab 缺 mockup，需用截圖當設計基準，承載未來重構的視覺一致性驗收。

### 2026-05-02T00:00:00.000Z — ui-designer 完成腳本/工具交付，但實體截圖未產出
產出物：
- `scripts/baseline-screenshots.js` — Playwright 全頁截圖腳本（baseline / current 雙模式）
- `scripts/visual-diff.js` — pixelmatch 像素比對 + HTML 報告產生器
- `docs/design/README.md` — 完整操作手冊
- `package.json` — devDependencies 鎖版（playwright@1.44.1、pixelmatch@5.3.0）
- `docs/design/{baseline,current,diff}/` 目錄骨架（含 .gitkeep）

⚠️ **關鍵缺口**：腳本未實際執行，baseline 目錄空無一物。

### 2026-05-03T01:00:00.000Z — design-director Review：REJECT
原因：腳本完整但 28 張實體截圖完全沒有產出，未達驗收標準第 1 條「26 張截圖產出完整」。

### 2026-05-03T01:15:00.000Z — design-director 接手執行（路 A）
老闆同意走路 A：人類補做 baseline。Agent 在 user 授權下代為執行：

**遭遇兩個 blocker，全部現場解決**：

1. **`SECRET_KEY` 空值導致 HTTP 500**
   - `.env` 檔不存在於本地（被 .gitignore 排除是正確的）
   - `settings.py` `os.getenv("DJANGO_SECRET_KEY", "")` 預設空字串
   - Django 6.0.2（local 環境，非 prod 的 3.2.3）拒絕空 SECRET_KEY
   - **解法**：產生 dev-only `.env`，含隨機 SECRET_KEY + placeholder API tokens

2. **DEBUG=False 時 Django 不 serve static files**
   - 第一次截圖 28 張全部「裸 HTML」（CSS/img 全 404），完全無法當基準
   - **解法**：`runserver --insecure` flag 強制 serve static（不改任何檔案）

**最終交付**：
- ✅ `docs/design/baseline/desktop/*.png` — 14 張（home, member, professor, project, project_linebot, project_stock, project_wra, project_wra_repoet, project_etfbot, project_financial, financial_1~3, trans）
- ✅ `docs/design/baseline/mobile/*.png` — 14 張
- ✅ Self-diff 驗證：28 頁全 0.0000% 差異
- ✅ `docs/design/diff-report.html` 產生正常
- ⚠️ Mobile 版多頁有破版（內容溢出視窗）— 屬「凍結現況」基準的一部分，不是截圖 bug，建議另開 Sprint 處理

**踩坑紀錄**：見 `.knowledge/postmortem-log.md`（兩條）
