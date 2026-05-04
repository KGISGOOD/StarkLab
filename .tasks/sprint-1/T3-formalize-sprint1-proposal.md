# 補做 Sprint 1 提案書（含已派 ad-hoc 任務的回溯納編）

| 欄位 | 值 |
|------|-----|
| ID | T3 |
| 專案 | StarkLab 官網 |
| Sprint | Sprint 1 |
| 指派給 | product-manager |
| 優先級 | P0 |
| 狀態 | in_review |
| 依賴 | — |
| 預估 | 3h |
| 建立時間 | 2026-05-02T00:00:00.000Z |
| 完工時間 | 2026-05-02T00:00:00.000Z |

---

## 任務描述

design-director 已基於老闆的「請看整個網站架構建議」初步分析，產出一份架構診斷報告，並 ad-hoc 派出 T1（brand-guardian）、T2（ui-designer）兩張單。**但目前專案沒有 Sprint 提案書，導致這兩張單成為孤兒任務、未經正式 Gate 流程。**

請 PM 接手，補做 Sprint 1 的正式提案書，把以下範圍**整合**進去：

### Sprint 1 應包含的範圍（design-director 建議）

#### 🔴 後端 Phase 1（止血，HIGH 風險）— 待 tech-lead 認領
- 移除 `lab/lab/ngrok.exe`、`w.db`、`*.csv` 進 `.gitignore`
- `LANGUAGE_CODE = "zh-Hant"`、`TIME_ZONE = "Asia/Taipei"`
- 補 `SECURE_SSL_REDIRECT` / `SESSION_COOKIE_SECURE` / HSTS
- 三個 `@csrf_exempt` 公開 endpoint 加 rate limit + token 驗證
- CSV 路徑統一收到 `BASE_DIR / "data" / ...`

#### 🟠 後端 Phase 2（收斂）— 待 tech-lead 認領
- 清 `urls.py` 註解死碼 + `project_wra_repoet` typo 加 redirect
- 三份 static 收斂為單一來源
- `project2_views.py` (1560 行) / `project3_views.py` (1320 行) 拆檔（不改邏輯）
- `Templates/` → `templates/mylab/`
- 評估 SQLite → PostgreSQL（需要 PM 拍板）

#### 🟡 設計 Phase 3（已 ad-hoc 派工，需回溯納編）
- **T1**（brand-guardian）：CSS / Design Token 盤點 — 已派
- **T2**（ui-designer）：CSS 收斂重構計畫 — 已派，依賴 T1
- T?（待 T2 計畫批准後）：實際 CSS 重構執行

### 必須產出（交付物）

1. **`proposal/sprint1-proposal.md`**（依 `/sprint-proposal` 規範）
   - Sprint 目標、成功指標、範圍邊界
   - Gate 排程（G0/G1/G2...）
   - 風險與假設

2. **`proposal/sprint1-dev-plan.md`**（依 `/dev-plan` 規範）
   - 第 6 節任務表必須包含 T1、T2、T3，並補上 T4~Tn（後端任務）
   - 依賴圖

3. **與 design-director、tech-lead 對齊**
   - design-director: 確認 T1/T2 範圍合理 ✅（已對齊）
   - tech-lead: 認領後端 Phase 1/2 任務並估時

## 驗收標準

- [ ] `proposal/sprint1-proposal.md` 完成
- [ ] `proposal/sprint1-dev-plan.md` 完成，第 6 節任務表涵蓋 T1~Tn
- [ ] T1、T2 在 dev-plan 中被明確標註（不再是孤兒任務）
- [ ] tech-lead 已認領後端任務（透過你方便的方式聯繫）
- [ ] 提交給老闆過 G0 Gate

## 重要注意事項

- T1、T2 已建立檔案（`.tasks/sprint-1/T1-*.md`、`T2-*.md`），請**不要重新建立**，只要在 dev-plan 第 6 節**引用**即可
- 老闆已口頭批准 design-director 派出 T1/T2，但這不算正式 Gate 通過 — 你補的提案書要把這段**事後追認**寫進「決策紀錄」
- design-director 的架構診斷已存在於 conversation log，但**未落檔**。建議你把它整理成 `docs/architecture/2026-05-02-audit.md` 一併歸檔

---

## 事件紀錄

### 2026-05-02T00:00:00.000Z — 建立任務
由 design-director 透過 ad-hoc 派工建立。原因：design-director 已派 T1/T2，需 PM 補做正式 Sprint 提案以納編、避免孤兒任務。

### 2026-05-02T00:00:00.000Z — 狀態變更 → in_review
產出物完成：
- `proposal/sprint1-proposal.md`（含 G0 審核區塊）
- `proposal/sprint1-dev-plan.md`（含 T1~T5 任務表 + 第 10 節空表）
- `docs/architecture/2026-05-02-audit.md`（架構診斷歸檔）
T1/T2 已在 dev-plan 第 6 節正式納編，不再是孤兒任務。
待 PM Review 後送 tech-lead 認領後端任務，再提 G0。
