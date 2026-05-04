# 子專案共用團隊與流程規則

> **版本**: v1.0
> **最後更新**: 2026-03-25
> **來源**: 從各專案模板抽取的共用流程規則
> **部署位置**: 子專案 `.knowledge/team-workflow.md`

---

## 團隊架構（指揮鏈）

> **核心原則：老闆只對接 L1 部門領導，L1 負責管理旗下 L2 Agent。指揮鏈不可跳級。**

```
老闆（最終決策者）
 │
 ├── product-manager (PM)     → trend-researcher, feedback-synthesizer, sprint-prioritizer
 ├── tech-lead                → backend-architect, frontend-developer, devops-automator,
 │                              ai-engineer, mobile-app-builder, rapid-prototyper, test-writer-fixer
 ├── design-director          → ui-designer, ux-researcher, brand-guardian, visual-storyteller, whimsy-injector
 ├── qa-lead                  → api-tester, performance-benchmarker, test-results-analyzer,
 │                              tool-evaluator, workflow-optimizer
 ├── project-lead             → studio-producer, project-shipper, experiment-tracker
 ├── operations-lead          → infrastructure-maintainer, finance-tracker, analytics-reporter,
 │                              legal-compliance-checker, support-responder, context-manager
 └── marketing-lead           → content-creator, growth-hacker, tiktok-strategist, instagram-curator,
                                twitter-engager, reddit-community-builder, app-store-optimizer
```

### 指揮鏈原則

1. **逐級指揮**: 老闆 → L1 → L2，禁止跨級直接指揮
2. **逐級回報**: L2 → L1 → 老闆，L2 不得跳過 L1 直接回報
3. **L1 品管責任**: L1 負責內部 Review，確保品質後才提交 Gate
4. **L2 專注執行**: L2 只負責被分派的任務範圍，不擅自擴大範圍

### L1 收到任務的強制流程

L1 Agent 收到老闆或 PM 指派的任務後，**必須先進入 Plan Mode 規劃再執行**：

1. **進入 Plan Mode**：分析任務需求，制定執行計畫
2. **規劃內容必須包含**：
   - 子任務拆解與分配對象（指派給哪個 L2）
   - 涉及的規範文件清單
   - 需要修改的檔案清單
   - 驗收標準
   - 跨部門依賴
3. **規劃確認後退出 Plan Mode**，開始分派 L2 執行
4. **L1 負責驗收 L2 產出**，確保符合規範後才回報完成

### 跨部門協作規則

- L1 之間可直接溝通協調
- 跨部門的 L2 不得直接對接，須透過各自 L1 協調
- 有衝突或資源爭議時，上報 PM 或老闆決策

---

## Sprint 流程

> 遵循公司 SOP（動態流程模型）。每個 Sprint 的步驟和關卡由 G0 審核時勾選決定。
> 完整 SOP: `company://sop/sprint-planning.md`

### Gate 定義

| Gate | 名稱 | 用途 | 何時需要 |
|------|------|------|---------|
| G0 | 需求確認 | 需求文件、任務拆解 | 必選 |
| G1 | 圖稿審核 | HTML mockup 審核 | 有 UI 變更時 |
| G2 | 程式碼審查 | 功能實作、程式碼品質 | 有程式碼變更時 |
| G3 | 測試驗收 | 單元/整合/效能測試 | 有程式碼變更時 |
| G4 | 文件審查 | 規範文件與程式碼一致 | 有文件變更時 |
| G5 | 部署就緒 | CI/CD 通過、環境就緒 | 需上線時 |
| G6 | 正式發佈 | 安全審核、上線確認 | 需發佈時 |

> Gate 是串行的：勾選的 Gate 按順序依次通過。前一個沒過不能提交下一個。

### 步驟與關卡對照

| 步驟 | 說明 | 對應關卡 |
|------|------|---------|
| 需求分析 | 需求文件、任務拆解 | G0（必選） |
| 設計 | 架構/API 設計 | — |
| UI 圖稿 | HTML mockup | G1 |
| 實作 | 程式碼開發 | G2 |
| 測試 | 單元/E2E 測試 | G3 |
| 文件 | 文件更新 | G4 |
| 部署 | 環境配置、CI/CD | G5 |
| 發佈 | 正式對外發佈 | G6 |

### 常見組合

| 場景 | 勾選步驟 | 關卡 |
|------|---------|------|
| 全新大功能 | 需求+設計+圖稿+實作+測試+文件+部署 | G0→G1→G2→G3→G4→G5 |
| 一般功能 | 需求+實作+測試+文件 | G0→G2→G3→G4 |
| 純後端 | 需求+設計+實作+測試 | G0→G2→G3 |
| 修 Bug | 需求+實作+測試 | G0→G2→G3 |
| 緊急 Hotfix | 需求+實作 | G0→G2 |
| 純文件 | 需求+文件 | G0→G4 |

### G0 通過後的派工流程

> **核心原則：老闆只下一個指令給 L1，L1 自己讀開發計畫書、按依賴順序產生所有任務檔案。**

```
G0 通過 → 老闆對 L1 說「開工」
           ↓
       L1 使用 /task-delegation
           ↓
       自動讀取 dev-plan 第 6 節任務清單
           ↓
       按依賴順序產生 .tasks/sprint-{N}/TN-xxx.md 檔案
           ↓
       系統（project-sync）自動同步到 DB
           ↓
       L1 依序指派 L2 執行
```

**PM 產出指令的規則**：
- 老闆說「給我指令」時，PM 針對**每個相關 L1 各產生一個指令**
- 指令必須**足夠完整**，L1 拿到就能自己跑完全程，老闆只當轉發者
- 指令內容須包含：要讀哪份 dev-plan、負責哪些步驟、該用哪些 Skill
- ❌ 不使用舊版 DelegationCommand JSON 格式
- ❌ 不逐一列出每個任務的派工指令

**L1 收到指令後的執行流程**：
1. 讀取 dev-plan，確認依賴流程與阻斷規則
2. 自行決定任務執行順序
3. 使用 `/task-delegation` 建立所有 `.tasks/` 檔案
4. 按順序執行任務（自己做或指派 L2）
5. 全程使用 Skill 操作（依任務狀態流程）：
   - `/task-start <ID>` — 開始任務（→ in_progress）
   - `/task-done <ID>` — 提交完成（→ in_review）
   - `/task-approve <ID>` — L1 審核通過（→ done）
   - `/task-status <ID>` — 查詢任務狀態
   - `/review` — 內部 Code Review
   - `/gate-record` — 記錄 Gate 審查結果
6. **不需要老闆再介入**，直到需要老闆審核 Gate 時才回報

> **任務狀態流程**：`created → assigned → in_progress → in_review → done`
> - `/task-delegation` 建立 → `created`
> - `/task-dispatch` 老闆派工 → `assigned`
> - `/task-start` agent 開始 → `in_progress`
> - `/task-done` agent 完成 → `in_review`
> - `/task-approve` L1 審核通過 → `done`

---

## Review 機制

> 每個 G0 勾選的步驟完成後，L1 必須執行內部 Review，通過後才提交對應 Gate。

### Review 四種類型

| 類型 | 檢查對象 | 核心問題 |
|------|---------|---------|
| 對程式碼 | 品質、邏輯、coding standards | 有沒有 bug？品質合格嗎？ |
| 對規範 | 實作 vs 規範文件 | 實作跟文件一致嗎？ |
| 對設計稿 | UI vs 設計稿 | 畫面跟設計稿一致嗎？ |
| 對功能 | 端到端功能 | 功能跑得通嗎？效能達標嗎？ |

### 步驟 vs Review 類型

| 步驟 | 適用 Review 組合 |
|------|-----------------|
| 設計 | 對規範 |
| UI 圖稿 | 對設計稿 |
| 實作（後端） | 對程式碼 + 對規範 |
| 實作（前端） | 對程式碼 + 對設計稿 + 對規範 |
| 測試 | 對功能 + 對規範 |
| 文件 | 對規範 |

### Review 通過標準

- 0 Blocker + 0 Major → **通過**
- 有 Blocker / Major → **不通過**，修正後重新 Review
- Minor → 記錄，可後續處理

---

## PM Gate 審核

L1 提交 Gate 回報後，PM 先審核再呈報老闆：

| # | 檢查項 | 說明 |
|---|--------|------|
| 1 | 交付物完整性 | 所有交付物是否齊全 |
| 2 | 數據正確性 | 報告數字與實際一致 |
| 3 | 驗收標準對照 | 逐項比對提案書/計畫書標準 |
| 4 | 流程合規 | 阻斷規則遵守、前置 Gate 已通過 |
| 5 | 計畫書紀錄 | 第 10 節已填寫 |
| 6 | 附帶問題 | 過程問題已記錄 |

> PM 審核通過後整理摘要呈報老闆，含 PM 建議（通過/駁回/附條件通過）。
> 老闆決策後，PM 須**當下**記錄到開發計畫書第 10 節。

---

## 上線階段（僅勾選「部署」步驟時）

### 上線前必做

| # | 檢查項 |
|---|--------|
| 1 | CI 全通過（lint + type-check + test） |
| 2 | Production Build 成功 |
| 3 | 健康檢查通過 |

### 上線後驗證

| # | 驗證項 |
|---|--------|
| 1 | 健康檢查 API 回傳 healthy |
| 2 | 核心功能 smoke test |
| 3 | 新功能逐一手動驗證 |
| 4 | 錯誤日誌無異常 |

### 回滾機制

| 嚴重度 | 處理方式 |
|--------|---------|
| 服務不可用 | 立即回滾上一版本，通知老闆 |
| 功能異常 | 開 hotfix 分支，走緊急 Hotfix 流程（G0→G2） |
| UI 瑕疵 | 記錄，下個 Sprint 修正 |

---

## 收尾

- Sprint 回顧（Retrospective）：做得好的 / 需改善的 / 行動項目
- 踩坑紀錄更新：`.knowledge/postmortem-log.md`
- CLAUDE.md 索引更新
- 稽核軌跡：開發計畫書第 10 節已完整填寫

### 文件產出 Checklist

- [ ] `proposal/sprint{N}-proposal.md` — G0 審核通過
- [ ] 設計稿已交付（僅勾選「UI 圖稿」時）
- [ ] `.knowledge/` 規範文件已更新
- [ ] `proposal/sprint{N}-dev-plan.md` — 開發計畫書已完成
- [ ] CLAUDE.md 索引已更新
