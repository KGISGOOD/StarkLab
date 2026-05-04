# 子專案共用開發規則

> **版本**: v1.0
> **最後更新**: 2026-03-25
> **來源**: 從各專案模板抽取的共用規則
> **部署位置**: 子專案 `.knowledge/company-rules.md`

---

## 文件治理（最高原則）

1. **文件就是法律**: 程式碼必須與規範文件一致。發現不一致時，**以規範文件為準修正程式碼**；若規範文件本身有誤，須先提案修改文件，經 PM 或老闆確認後才能改程式碼。**任何情況下不得跳過文件直接改 code。**
2. **原子性**: 每個 PR / commit 必須同時包含「程式碼變更」與「對應文件更新」。只改 code 不改文件 = 未完成。只改文件不改 code = 未完成。兩者必須在同一次變更中一起完成。
3. **文件同步維護**: 任何功能新增、修改、刪除，必須同步更新對應的 `.knowledge/` 文件與 CLAUDE.md 索引。程式碼與文件不一致視為未完成。
4. **索引完整性**: 所有 `.knowledge/` 文件都必須在 CLAUDE.md 的「專案文件索引」中登記。新增文件但未更新索引 = 未完成。
5. **先確認再開發**: 功能需求確認 → 老闆核可 → 才進入開發。未經確認不得直接實作。
6. **遵循公司規範**: 所有開發須遵循公司知識庫所列的規範與 SOP。
7. **公司規範本地化**: 引用公司規範時，若本地 `.knowledge/` 尚無對應文件，**必須先建立一份本地副本再使用**。未用到的規範不需複製，用到時才建立。
8. **需求備忘統一入口**: 老闆提出的額外需求、想法、未來功能構想，統一記錄到 `proposal/product-roadmap-draft.md` 的「未排期 Backlog」。PM 負責分類與評估，正式納入開發前須寫入對應 Sprint 提案書經 G0 審核。

## 文件層級

| 層級 | 強制力 | 說明 | 適用文件 |
|------|--------|------|---------|
| 🔴 規範 | **必須遵循** | 開發時嚴格依照，違反視為 bug | `coding-standards`, `api-design`, `data-model` |
| 🟡 規格 | **開發依據** | 功能實作的需求來源，有疑義找 PM | `feature-spec`, `acceptance-criteria` |
| 🔵 參考 | **輔助理解** | 幫助理解背景，不作為強制依據 | `project-overview`, `tech-stack`, `architecture` |

## 禁止憑空想像規則（最高強制力）

> **核心原則：不確定就去讀，不要猜。** Agent 不得憑空想像任何資料結構、API 回傳格式、型別定義。所有實作必須有明確的「真相來源」。

| 項目 | 真相來源 | 驗證方式 | 違反後果 |
|------|---------|---------|---------|
| API Response 結構 | 後端路由的實際回傳 | 讀路由原始碼確認 | 前端顯示全壞（undefined） |
| API Request 參數 | 後端的驗證 schema | 讀驗證定義 | 400 / 422 錯誤 |
| 前端型別定義 | 後端回傳 + 命名轉換結果 | 逐欄位對照 | TypeScript 編譯過但運行時炸 |
| 資料庫欄位名 | ORM schema / migration | 讀 schema 檔案 | 查詢失敗 |

## 命名規範（骨架）

> 各專案模板可覆寫細節，但以下骨架不可偏離。

| 層 | 命名風格 | 範例 |
|----|---------|------|
| 資料庫 | snake_case | `user_id`, `created_at` |
| API JSON（請求/回應） | snake_case | `trace_id`, `total_elements` |
| 程式碼變數/函數 | camelCase | `userId`, `shopName` |
| 型別/類別/元件 | PascalCase | `UserService`, `HomeScreen` |

## 依賴與環境變數變更規則（強制）

### 依賴變更

修改任何依賴定義檔（`package.json` / `requirements.txt` 等）後，**必須**：
1. 執行對應安裝指令更新 lockfile
2. 將 lockfile 與依賴定義檔**一起 commit**

### 環境變數變更

新增或修改環境變數時，**必須逐一對照以下位置**，全部一致才能 commit：

| # | 位置 | 用途 |
|---|------|------|
| 1 | 程式碼 | 實際讀取的變數名 |
| 2 | CI workflow | 建置時注入 |
| 3 | `.env.example` | 文件記錄 |
| 4 | 部署設定 | 容器 / 雲端注入 |

> 變數名不一致 = 程式讀不到值 = 運行時才爆炸

## Commit 紀律（強制）

1. **一事一 commit**: 禁止「大雜燴」commit
2. **commit 前必過 CI 檢查**: lint + type-check + test 全部通過
3. **commit message 格式**: `<type>(<scope>): <summary>`，type 限 feat/fix/refactor/test/docs/chore
4. **禁止 force push 到共用分支**: main / develop / release 禁止 `--force`
5. **WIP commit 禁止合併**: 含 `WIP` / `TODO` / `FIXME` 不得出現在合併請求中
6. **lockfile 必須隨依賴定義一起 commit**

### Commit 前必做檢查清單

- [ ] CI 檢查通過（lint + type-check + test）？
- [ ] 依賴改了 → lockfile 已同步？
- [ ] 環境變數名稱：程式碼 / CI / .env.example 一致？
- [ ] DB schema 有改 → migration 已生成並 commit？
- [ ] 本地啟動驗證通過？

## 平行 Session 規則

1. **每個 Session 完成後必須列出修改的共用檔案**：routes、shared types、config 等
2. **不得假設其他 Session 的實作內容**：依賴其他 Session 的產出必須讀取確認
3. **共用檔案衝突風險**：多個 Agent 同時修改同一檔案時，必須標記並通知 L1
