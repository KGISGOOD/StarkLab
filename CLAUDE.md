# 實驗室官網 — Agent 指南

> 本文件為專案索引導航，所有 Agent 執行任務前必須先閱讀本文件，再依任務需求查閱對應文件。

---

## 專案簡介

- **專案名稱**: {名稱}
- **類型**: {Web 應用 / SaaS 平台}
- **核心價值**: {一句話描述}
- **目標用戶**: {描述}
- **開發平台**: Windows

## 共用開發規則

> 以下 2 份文件包含所有 Agent 必須遵循的共用規則，執行任務前**必須先閱讀**。

| 文件 | 內容 |
|------|------|
| `.knowledge/company-rules.md` | 文件治理、文件層級、禁止憑空想像、命名骨架、Commit 紀律、依賴/環境變數規則 |
| `.knowledge/team-workflow.md` | 團隊架構、指揮鏈、Sprint 流程、Gate、Review、上線/回滾 |

## 命名規範差異（覆蓋共用骨架）

| 層 | 風格 | 範例 |
|----|------|------|
| API JSON | snake_case | `trace_id`, `total_elements` |
| 前端 TS 型別 | camelCase | `shopId`, `createdAt`（經 `snakeToCamel` 轉換） |
| 轉換 | 自動 | `services/api.ts` 統一 `camelToSnake()` / `snakeToCamel()` |

## 技術棧

| 類型 | 技術 |
|------|------|
| 前端 | {Vue 3 / React / Next.js} |
| 後端 | {Fastify / Express / FastAPI} |
| 資料庫 | {PostgreSQL / MongoDB / SQLite} |
| 測試 | {Vitest / Playwright} |
| 部署 | {Docker / Vercel} |

## 前端 API 串接強制流程

1. **先讀後端路由原始碼**：找到對應端點，看實際回傳什麼
2. **確認信封層**：確認 API 回傳是否有統一信封格式
3. **逐欄位對照**：後端 `snake_case` → 前端 `camelCase`，不得自行新增欄位
4. **不確定就問**：api-design.md 與後端不一致，以**後端程式碼為準**，同時回報 PM

## 設計稿合規規則（強制）

> 前端 UI 必須按設計稿開發，UI 不一致 = Blocker。

1. **先讀設計稿**：`docs/design/mockup-*.html`
2. **識別所有狀態**：設計稿每個 UI 狀態都要實作
3. **對照動畫/色彩/響應式**：時長、easing、色系、桌面版/手機版
4. **不確定就問**：回報 L1 → 協調 Design Director

設計稿 HTML 給開發人員、截圖（JPG/PNG）給 Agent 視覺比對。

## 踩坑紀錄

| 問題 | 原因 | 正確做法 |
|------|------|---------|
| {問題描述} | {根因} | {解決方案} |

## 可用指令（Slash Commands）— 強制使用

> 以下指令已部署到 `.claude/commands/`。
> **使用方式**：讀取對應的 `.claude/commands/{指令名}.md` 檔案，依照其中的步驟執行。
>
> **強制規則：遇到下列「使用時機」描述的場景時，必須執行對應指令，不得跳過或手動替代。**
> 違反此規則等同未完成任務。

| 指令 | 用途 | 使用時機（遇到即必須執行） |
|------|------|--------------------------|
| `/project-kickoff` | 初始化專案結構 | 專案建立後第一件事 |
| `/product-diagnosis` | 產品六問診斷（G0 前置） | 提案前驗證產品方向 |
| `/sprint-proposal` | 產出 Sprint 提案書 | Sprint 規劃階段 |
| `/dev-plan` | 產出開發計畫書 | G0 通過後展開任務 |
| `/task-dispatch` | 老闆派工，建立 .tasks/ 檔案 | 老闆分配任務時 |
| `/task-delegation` | 拆解任務到計畫書第 6 節 | L1 拆解子任務時 |
| `/task-start` | 標記任務為進行中 | Agent 開始執行任務時 |
| `/task-status` | 更新任務狀態 | 任務狀態變更時（blocked、assigned 等） |
| `/task-done` | 標記任務完成（待審查） | 任務交付時 |
| `/task-approve` | L1 審核通過，標記為 done | L1 Review 通過後 |
| `/review` | L1 內部 Code Review | 程式碼完成後送審 |
| `/pm-review` | PM 審核 Gate 提交 | L1 提交 Gate 後 |
| `/gate-record` | 記錄 Gate 審查決策 | Gate 審查結果出爐時 |
| `/pre-deploy` | 上線前檢查清單（G5） | 部署前最後確認 |
| `/pitfall-record` | 記錄踩坑經驗 | 發現問題時立即記錄 |
| `/pitfall-resolve` | 標記踩坑已解決 | 問題修復後 |
| `/sprint-retro` | Sprint 回顧報告 | Sprint 結束時 |
| `/harness-audit` | Harness 健康度稽核 | 定期檢查 |

## 專案文件索引

| 文件 | 說明 |
|------|------|
| `.knowledge/company-rules.md` | 共用開發規則 |
| `.knowledge/team-workflow.md` | 共用工作流程 |
| `.knowledge/project-overview.md` | 專案概述 |
| `.knowledge/api-design.md` | API 設計（🔴 規範） |
| `.knowledge/data-model.md` | 資料模型（🔴 規範） |
| `.knowledge/feature-spec.md` | 功能規格（🟡 規格） |
| `.knowledge/acceptance-criteria.md` | 驗收標準（🟡 規格） |
| `.knowledge/postmortem-log.md` | 踩坑紀錄 |

## 公司知識庫

> **使用規則（company-rules.md 第 7 條）**：需要引用公司規範時，先檢查本地 `.knowledge/` 是否已有副本。若無，從下方來源路徑複製一份到 `.knowledge/` 再使用。不需要的規範不必複製。

| 規範 | 來源路徑 | 本地副本 |
|------|---------|---------|
| 程式碼規範 | `C:/Users/Bandai/Desktop/AgentHub/Agent-hub/.knowledge/company/standards/coding-standards.md` | `.knowledge/coding-standards.md` |
| API 規範 | `C:/Users/Bandai/Desktop/AgentHub/Agent-hub/.knowledge/company/standards/api-standards.md` | `.knowledge/api-standards.md` |
| 測試規範 | `C:/Users/Bandai/Desktop/AgentHub/Agent-hub/.knowledge/company/standards/testing-standards.md` | `.knowledge/testing-standards.md` |
| 品質 Checklist | `C:/Users/Bandai/Desktop/AgentHub/Agent-hub/.knowledge/company/standards/quality-checklist.md` | `.knowledge/quality-checklist.md` |
| Code Review SOP | `C:/Users/Bandai/Desktop/AgentHub/Agent-hub/.knowledge/company/sop/code-review.md` | `.knowledge/code-review.md` |
| Sprint 規劃 SOP | `C:/Users/Bandai/Desktop/AgentHub/Agent-hub/.knowledge/company/sop/sprint-planning.md` | `.knowledge/sprint-planning.md` |
