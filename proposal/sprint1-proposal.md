# Sprint 1 提案書 — StarkLab 官網技術健康提升

> **提案人**: 產品經理（product-manager）
> **日期**: 2026-05-02
> **狀態**: 待 G0 審核
> **專案**: StarkLab 官網
> **Sprint 編號**: Sprint 1

---

## 1. Sprint 背景

老闆提出「請看整個網站架構建議」，design-director 依此對現有 Django 專案進行全面架構診斷，產出診斷報告（詳見 `docs/architecture/2026-05-02-audit.md`）。診斷結論：專案存在多項高風險安全問題、程式碼負債、及 CSS 混亂，需系統性處理。

> **事後追認決策紀錄**：在正式 Sprint 提案建立前，design-director 已 ad-hoc 派出 T1（brand-guardian）與 T2（ui-designer）兩張工單。老闆已口頭批准，本提案書將此兩張單正式納編，完成程序合規。

---

## 2. Sprint 目標

在不破壞現有功能的前提下，完成 StarkLab 官網的「止血 → 收斂 → 設計基線」三階段準備工作，讓後續 Sprint 可以在安全、清晰的基礎上推進。

**成功指標**：
- 🔴 所有 HIGH 安全風險修復完畢（Phase 1 全部完成）
- 🟠 程式碼負債評估完成，Phase 2 重構計畫書落檔
- 🟡 CSS 設計系統基線建立，T1/T2 交付物通過 PM Review

---

## 3. 範圍定義

### ✅ 做（In Scope）

#### 🔴 後端 Phase 1 — 止血（HIGH 風險，必做）
| # | 項目 | 風險等級 |
|---|------|---------|
| 1 | 移除 `lab/lab/ngrok.exe`、`w.db`、`*.csv` 並加入 `.gitignore` | HIGH |
| 2 | 設定 `LANGUAGE_CODE = "zh-Hant"`、`TIME_ZONE = "Asia/Taipei"` | MEDIUM |
| 3 | 補 `SECURE_SSL_REDIRECT` / `SESSION_COOKIE_SECURE` / HSTS | HIGH |
| 4 | 三個 `@csrf_exempt` 公開 endpoint 加 rate limit + token 驗證 | HIGH |
| 5 | CSV 路徑統一收到 `BASE_DIR / "data" / ...` | MEDIUM |

#### 🟠 後端 Phase 2 — 收斂（技術負債）
| # | 項目 | 風險等級 |
|---|------|---------|
| 6 | 清 `urls.py` 註解死碼 + `project_wra_repoet` typo 加 redirect | LOW |
| 7 | 三份 static 收斂為單一來源 | MEDIUM |
| 8 | `project2_views.py`（1560 行）/ `project3_views.py`（1320 行）拆檔（不改邏輯） | MEDIUM |
| 9 | `Templates/` → `templates/mylab/` 目錄規範化 | MEDIUM |
| 10 | 評估 SQLite → PostgreSQL 遷移可行性（產出評估報告） | LOW |

#### 🟡 設計 Phase 3 — CSS 設計系統基線（已 ad-hoc 派工，回溯納編）
| 任務 ID | 項目 | 執行者 | 狀態 |
|---------|------|--------|------|
| T1 | CSS / Design Token 盤點 | brand-guardian | ⏳ created |
| T2 | CSS 收斂重構計畫書（依 T1 結果） | ui-designer | ⏳ created（待 T1） |
| T4 | Baseline 視覺基準截圖（26 張） | ui-designer | ✅ done |

#### 📋 流程補正
| 任務 ID | 項目 | 執行者 |
|---------|------|--------|
| T3 | 補做正式 Sprint 1 提案書（本文件） | product-manager |

#### 🔴🟠 後端任務（待 tech-lead 認領）
| 任務 ID | 項目 | 執行者 | 狀態 |
|---------|------|--------|------|
| T5 | 後端 Phase 1 止血 | tech-lead | ⏳ pending_lead |
| T6 | 後端 Phase 2 收斂（依 T5） | tech-lead | ⏳ pending_lead |

> **⚠️ 編號說明**：T4 已被 baseline 截圖任務佔用，後端任務從 T5 起編。

### ❌ 不做（Out of Scope）

- jQuery 1.8.3 升級（另案評估）
- 引入 Tailwind / Bootstrap / 任何 CSS framework
- 資料庫實際遷移（Phase 2 只出評估報告，不執行遷移）
- 任何前端功能新增
- 上線部署（本 Sprint 只出計畫和修復，不走 G5/G6）
- CSS 實際重構執行（T2 只出計畫，實際執行留待下個 Sprint）

---

## 4. 流程決策（步驟 + 關卡組合）

本 Sprint 選用「**需求分析 + 實作 + 測試 + 文件**」組合：

| 關卡 | 說明 | 負責審核 |
|------|------|---------|
| G0 | 需求確認（本文件） | 老闆 |
| G2 | 程式碼審查（後端 Phase 1/2 實作） | PM → 老闆 |
| G4 | 文件審查（計畫書、設計文件） | PM → 老闆 |

**阻斷規則**：
- G2 通過前不得宣告後端修復完成
- T2 依賴 T1 交付物，T1 未通過 PM Review 前 T2 不得啟動

---

## 5. 團隊分配

| 角色 | Agent ID | 負責範圍 |
|------|----------|---------|
| 產品經理 | product-manager | T3 提案書、PM Review、Gate 協調 |
| Tech Lead | tech-lead | 後端 Phase 1（T5）、Phase 2（T6）、認領任務 |
| 品牌守護者 | brand-guardian | T1 CSS / Design Token 盤點 |
| UI 設計師 | ui-designer | T2 CSS 收斂重構計畫書、T4 Baseline 截圖（已完成） |

---

## 6. 時程預估

| 任務 | 預估工時 | 依賴 | 狀態 |
|------|---------|------|------|
| T3 提案書（本任務） | 3h | — | 🔍 待審查 |
| T4 Baseline 截圖 | 3h | — | ✅ done |
| T1 CSS 盤點 | 4h | — | ⏳ created |
| T5 後端 Phase 1 止血 | 待 tech-lead 估時 | — | ⏳ pending_lead |
| T2 CSS 重構計畫 | 6h | T1 | ⏳ created（待 T1） |
| T6 後端 Phase 2 收斂 | 待 tech-lead 估時 | T5 | ⏳ pending_lead |

> ⚠️ T5、T6 工時待 tech-lead 認領後確認。

---

## 7. 風險評估

| 風險 | 影響 | 機率 | 緩解方式 |
|------|------|------|---------|
| ngrok.exe / w.db 已在 git history 中 | 敏感資料洩漏 | HIGH | 加 .gitignore 後另行評估是否 rewrite history |
| @csrf_exempt 修改影響現有功能 | 功能中斷 | MEDIUM | 逐一測試 + 保留原邏輯可快速 revert |
| views.py 拆檔引入 import 錯誤 | 功能中斷 | MEDIUM | 拆檔後立即跑所有現有測試 |
| CSS 盤點與實際生產環境不一致 | T2 計畫偏差 | LOW | T1 以 source code 為準，不依賴截圖 |
| SQLite → PostgreSQL 評估結論影響後續 Sprint 排程 | 計畫變動 | MEDIUM | 本 Sprint 只出評估，決策交老闆 |

---

## 8. 驗收標準

- [ ] `proposal/sprint1-proposal.md` 完成（本文件）
- [ ] `proposal/sprint1-dev-plan.md` 完成（第 6 節含 T1~T6）
- [x] T4 Baseline 截圖 26 張完成
- [ ] T1 盤點報告（5 份交付物）通過 PM Review
- [ ] T2 重構計畫書（3 份交付物）通過 PM Review
- [ ] T5 後端 Phase 1 所有 HIGH 風險修復通過 G2 代碼審查
- [ ] T6 後端 Phase 2 計畫書/評估報告落檔
- [ ] tech-lead 已認領 T5/T6 並回覆估時
- [ ] 所有 Gate 紀錄寫入 `proposal/sprint1-dev-plan.md` 第 10 節

---

## 9. 假設與依賴

- 假設老闆已口頭批准 T1/T2，本 G0 為正式追認
- 假設 tech-lead 在 G0 通過後 24h 內回覆估時
- 假設現有測試（若有）可作為後端修復的回歸基準
- 不假設有 staging 環境，所有修復需在本地充分測試

---

## 10. 決策紀錄（事後追認）

| 日期 | 決策 | 決策人 | 備註 |
|------|------|--------|------|
| 2026-05-02 | T1 CSS 盤點 ad-hoc 派工 | design-director | 老闆口頭批准 |
| 2026-05-02 | T2 CSS 重構計畫 ad-hoc 派工 | design-director | 依賴 T1 |
| 2026-05-02 | PM 接手補做正式提案書（T3） | design-director → product-manager | 避免孤兒任務 |

---

## G0 審核區塊

> 以下由老闆審核後填寫

**G0 Checklist**：
- [ ] Sprint 目標清晰且可驗收
- [ ] 範圍邊界明確（做/不做已定義）
- [ ] 流程與關卡組合已確認
- [ ] 風險評估合理
- [ ] 團隊分配無缺口

**老闆決策**：[ ] 通過 / [ ] 調整 / [ ] 擱置

**審核意見**：

**審核日期**：

---

*本文件依 `company://sop/sprint-planning.md` v4.1 產出*
