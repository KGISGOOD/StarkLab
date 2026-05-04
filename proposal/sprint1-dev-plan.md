# Sprint 1 開發計畫書 — StarkLab 官網技術健康提升

> **版本**: v1.0
> **L1 負責人**: product-manager（提案書部分）/ tech-lead（後端部分）
> **G0 狀態**: 待審核
> **最後更新**: 2026-05-02
> **對應提案書**: `proposal/sprint1-proposal.md`

---

## 1. 需求摘要

依據架構診斷報告（`docs/architecture/2026-05-02-audit.md`）及 Sprint 1 提案書，本計畫書涵蓋三個並行軌道：

| 軌道 | 代號 | 風險等級 | 主要執行者 |
|------|------|---------|-----------|
| 後端安全止血 | Phase 1 | 🔴 HIGH | tech-lead |
| 後端技術收斂 | Phase 2 | 🟠 MEDIUM | tech-lead |
| CSS 設計基線 | Phase 3 | 🟡 LOW | brand-guardian / ui-designer |

---

## 2. 技術方案

### 2.1 技術棧（現況）

| 組件 | 版本/技術 |
|------|----------|
| 後端框架 | Django 3.2.3 |
| Python | 3.10 |
| 資料庫 | SQLite（w.db） |
| Web Server | Waitress |
| Reverse Proxy | Caddy |
| 外部 API | LINE Bot API、Grok (X.AI)、Gemini API |
| 部署環境 | Windows（開發 + 部署） |

### 2.2 Phase 1 技術方案（安全止血）

**T4 執行項目說明**：

1. **敏感檔案移除**
   - 在 `.gitignore` 加入 `ngrok.exe`、`*.db`、`*.csv`、`*.xlsx`
   - 確認現有 git history 是否包含敏感資料（評估是否需 `git filter-repo`）

2. **語系 / 時區**
   - `settings.py`: `LANGUAGE_CODE = "zh-Hant"`, `TIME_ZONE = "Asia/Taipei"`

3. **安全標頭**
   ```python
   SECURE_SSL_REDIRECT = True           # 生產環境強制 HTTPS
   SESSION_COOKIE_SECURE = True
   CSRF_COOKIE_SECURE = True
   SECURE_HSTS_SECONDS = 31536000
   SECURE_HSTS_INCLUDE_SUBDOMAINS = True
   ```
   > ⚠️ 本地開發環境需用 `DEBUG=True` 時繞過，建議用 `if not DEBUG:` 包住

4. **@csrf_exempt endpoint 加固**
   - 三個公開 endpoint 加 token 驗證（X-API-Token header）
   - 加 django-ratelimit 或自製 rate limit decorator（每 IP 每分鐘 ≤ 10 次）

5. **CSV 路徑修正**
   ```python
   # 舊
   open('chat_records.csv', ...)
   # 新
   BASE_DIR / "data" / "chat_records.csv"
   ```

### 2.3 Phase 2 技術方案（程式碼收斂）

**T5 執行項目說明**：

1. **urls.py 清理**：移除死碼、加 `project_war_report` redirect（typo 修正）
2. **Static 收斂**：以 `STATICFILES_DIRS` 統一指向單一目錄
3. **Views 拆檔**（不改邏輯）：
   - `project2_views.py` → 依功能拆為 3~5 個子模組
   - `project3_views.py` → 依功能拆為 3~5 個子模組
4. **Templates 目錄規範**：`Templates/` → `templates/mylab/`（需更新所有 `TEMPLATES` 設定）
5. **SQLite → PostgreSQL 評估**：產出可行性評估報告（含遷移成本、Windows 部署考量）

### 2.4 Phase 3 技術方案（CSS 設計基線）

**T1**：純唯讀盤點，產出 5 份交付物於 `docs/design/audit/`
**T2**：依 T1 結果產出重構計畫書，產出 3 份交付物於 `docs/design/`

---

## 3. 檔案變更清單

### T4 — Phase 1（止血）

| 動作 | 檔案 | 說明 |
|------|------|------|
| 修改 | `.gitignore` | 加入敏感檔案排除規則 |
| 修改 | `labweb/lab/lab/settings.py` | 語系/時區/安全標頭 |
| 修改 | `labweb/lab/mylab/views.py`（或對應 views）| csrf_exempt endpoint 加固 |
| 修改 | 相關 CSV 路徑 | 收斂至 BASE_DIR/data/ |
| 新增 | `labweb/lab/data/` | 統一資料目錄 |

### T5 — Phase 2（收斂）

| 動作 | 檔案 | 說明 |
|------|------|------|
| 修改 | `labweb/lab/lab/urls.py` | 清死碼 + 加 redirect |
| 修改 | `labweb/lab/lab/settings.py` | STATICFILES_DIRS 收斂 |
| 新增 | `labweb/lab/mylab/views_project2_*.py` | project2_views.py 拆檔 |
| 新增 | `labweb/lab/mylab/views_project3_*.py` | project3_views.py 拆檔 |
| 移動 | `Templates/` → `templates/mylab/` | 目錄規範化 |
| 新增 | `docs/backend/sqlite-pg-evaluation.md` | 資料庫遷移評估報告 |

### T1/T2 — Phase 3（CSS）

| 動作 | 檔案 | 說明 |
|------|------|------|
| 新增 | `docs/design/audit/colors.md` | 顏色盤點（T1） |
| 新增 | `docs/design/audit/typography.md` | 字級盤點（T1） |
| 新增 | `docs/design/audit/spacing.md` | 間距盤點（T1） |
| 新增 | `docs/design/audit/conflicts.md` | 衝突清單（T1） |
| 新增 | `docs/design/audit/tokens-draft.css` | Design Token 草案（T1） |
| 新增 | `docs/design/refactor-plan.md` | CSS 重構計畫書（T2） |
| 新增 | `docs/design/components-api.md` | 元件 API 草案（T2） |
| 新增 | `docs/design/impact.md` | HTML 模板影響評估（T2） |

---

## 4. 依賴關係圖

```
T3（提案書）── 完成 ──┐
                      ↓
T1（CSS 盤點）──────── 完成 ──→ T2（重構計畫）
                                        ↓
                              PM Review → G4

T4（Phase 1 止血）──── 完成 ──→ T5（Phase 2 收斂）
                                        ↓
                              L1 Review → G2

G2 + G4 全通過 ──────────────────── Sprint 1 完成
```

---

## 5. 規範文件索引

| 文件 | 路徑 | 狀態 |
|------|------|------|
| 架構診斷報告 | `docs/architecture/2026-05-02-audit.md` | ✅ 已建立 |
| CSS 盤點報告 | `docs/design/audit/` | ⏳ T1 執行中 |
| CSS 重構計畫 | `docs/design/refactor-plan.md` | ⏳ T2 待 T1 |
| 後端評估報告 | `docs/backend/sqlite-pg-evaluation.md` | ⏳ T5 產出 |

---

## 6. 任務拆解表

| 任務 ID | 任務名稱 | 負責 Agent | 依賴 | 預估工時 | 優先級 | 狀態 |
|---------|---------|-----------|------|---------|--------|------|
| T1 | CSS / Design Token 盤點 | brand-guardian | — | 4h | P1 | created |
| T2 | CSS 收斂重構計畫書 | ui-designer | T1 | 6h | P1 | created |
| T3 | 補做 Sprint 1 提案書（本文件） | product-manager | — | 3h | P0 | in_review |
| T4 | 產生 12 頁 baseline 視覺基準截圖 | ui-designer | — | 3h | P1 | done |
| T5 | 後端 Phase 1 止血 | tech-lead | — | TBD | P0 | pending_lead |
| T6 | 後端 Phase 2 收斂 | tech-lead | T5 | TBD | P1 | pending_lead |

> **T5/T6 狀態說明**：`pending_lead` = 待 tech-lead 認領並回覆估時。PM 已發送協調請求。
>
> **⚠️ 編號修正紀錄（2026-05-03）**：原 dev-plan 草稿誤將後端任務命名為 T4/T5，與已存在的 `.tasks/sprint-1/T4-baseline-screenshots.md`（ui-designer，done）衝突。依 tech-lead 回報，修正為 T5/T6，避免 Gate 紀錄混亂。

### 任務詳細說明

#### T4：Baseline 視覺基準截圖（已完成）
- **負責**：ui-designer
- **狀態**：✅ done（由 design-director 接手執行完成）
- **交付物**：`docs/design/baseline/desktop/*.png`（14 張）、`docs/design/baseline/mobile/*.png`（14 張）、`scripts/baseline-screenshots.js`、`scripts/visual-diff.js`、`docs/design/README.md`
- **備註**：詳見 `.tasks/sprint-1/T4-baseline-screenshots.md`

#### T5：後端 Phase 1 止血
- **負責**：tech-lead
- **驗收標準**：
  - [ ] `.gitignore` 涵蓋 ngrok.exe、*.db、*.csv、*.xlsx
  - [ ] settings.py LANGUAGE_CODE / TIME_ZONE 正確
  - [ ] SECURE_SSL_REDIRECT / SESSION_COOKIE_SECURE / HSTS 已設定（含 DEBUG 判斷）
  - [ ] 三個 @csrf_exempt endpoint 已加 token 驗證 + rate limit
  - [ ] CSV 路徑全部使用 BASE_DIR / "data" / ...
  - [ ] 修改後現有功能可正常啟動（Waitress dev 環境）

#### T6：後端 Phase 2 收斂
- **負責**：tech-lead
- **前提**：T5 通過 L1 Review
- **驗收標準**：
  - [ ] urls.py 死碼清除，project_wra_repoet → redirect
  - [ ] STATICFILES_DIRS 收斂為單一目錄
  - [ ] project2_views.py 拆為多檔，總行數各 ≤ 400 行
  - [ ] project3_views.py 拆為多檔，總行數各 ≤ 400 行
  - [ ] Templates/ → templates/mylab/ 完成，所有 template 路徑正確
  - [ ] SQLite → PostgreSQL 評估報告完成（含結論建議）

---

## 7. 驗收標準（Sprint 層級）

- [ ] T1 五份盤點交付物完成且可閱讀
- [ ] T2 三份設計計畫交付物完成
- [x] T4 Baseline 截圖 26 張完成（已 done）
- [ ] T5 所有 HIGH 安全風險修復，通過 G2 審查
- [ ] T6 程式碼整理完成，評估報告落檔
- [ ] T3 正式提案書與 dev-plan 落檔
- [ ] tech-lead 已回覆認領 T5/T6 並提供估時
- [ ] 第 10 節所有記錄填寫完整

---

## 8. 異常處理

| 場景 | 處理方式 |
|------|---------|
| T1 盤點發現 CSS 超過 30 種顏色 | 列出合併建議，不阻斷 T2，但 T2 計畫書需標記 |
| T4 修改 @csrf_exempt 導致 LINE Bot 失效 | 立即 revert，設計白名單機制後再修 |
| Views 拆檔後 import 錯誤 | 以 git 回滾對應批次，逐檔修復 |
| tech-lead 48h 內未回覆 | PM 上報老闆，評估是否延後 T4/T5 |

---

## 9. 時程預估

| 任務 | 開始條件 | 預估完成 |
|------|---------|---------|
| T3（提案書） | 立即 | 2026-05-02 |
| T4（Baseline 截圖） | — | 2026-05-03（已完成） |
| T1（CSS 盤點） | G0 通過後 | G0+1d |
| T5（Phase 1 止血） | G0 + tech-lead 認領 | G0+2d |
| T2（重構計畫） | T1 完成 | T1+1d |
| T6（Phase 2 收斂） | T5 完成 | T5+2d |

---

## 10. 任務與審核紀錄（備查）

> 每個任務完成後記錄結果，每次 Review/Gate 通過後記錄決策。本區作為 Sprint 完整稽核軌跡。

### 任務完成紀錄

| 任務 | 完成日期 | 結果 | 備註 |
|------|---------|------|------|
| T1 | 2026-05-03 | 🔍 待審查 | 5 份盤點交付物完成：colors.md（39色→建議合併18）、typography.md（12級）、spacing.md、conflicts.md（10項衝突含3 CRITICAL）、tokens-draft.css |
| T2 | | | |
| T3 | 2026-05-02 | 🔍 待審查 | proposal/sprint1-proposal.md、sprint1-dev-plan.md、docs/architecture/2026-05-02-audit.md 完成 |
| T4 | 2026-05-03 | ✅ 完成 | 28 張 baseline 截圖（desktop×14 + mobile×14）、腳本、README；self-diff 0%。詳見 .tasks/sprint-1/T4-baseline-screenshots.md |
| T5 | | | |
| T6 | | | |

### Review 紀錄

| Review 步驟 | 日期 | 結果 | Review 文件連結 |
|------------|------|------|---------------|
| CSS 盤點 Review（T1） | | | |
| CSS 計畫書 Review（T2） | | | |
| Baseline 截圖 Review（T4） | 2026-05-03 | 通過 | design-director 接手完成；self-diff 0% |
| 後端 Phase 1 Review（T5） | | | |
| 後端 Phase 2 Review（T6） | | | |

### Gate 紀錄

| Gate | 日期 | 決策 | 審核意見 |
|------|------|------|---------|
| G0 | | | |
| G2 | | | |
| G4 | | | |

---

*本文件依 `company://sop/sprint-planning.md` v4.1 產出*
