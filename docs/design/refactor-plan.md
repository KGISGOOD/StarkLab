# CSS 收斂重構計畫書

> **文件狀態**: 計畫草案（待老闆批准後方可動工）
> **產出者**: frontend-engineer（T2）
> **產出日期**: 2026-05-02
> **輸入文件**: colors.md、typography.md、spacing.md、conflicts.md、tokens-draft.css、tech-constraints.md
> **原則**: 本計畫每一批次均需老闆批准後方可執行，任何步驟皆不得超前進行。

---

## 1. 收斂對應表

### 1.1 現有 14 個 CSS 檔的去處

> **說明**：目前所有 CSS 位於 `mylab/static/css/`（扁平結構）。重構後目標架構如下：
>
> ```
> mylab/static/css/
> ├── tokens.css
> ├── base.css
> ├── components/
> │   ├── navbar.css
> │   ├── card.css
> │   ├── button.css
> │   ├── footer.css
> │   ├── badge.css
> │   ├── modal.css
> │   └── photo-gallery.css
> └── pages/
>     ├── home.css
>     ├── member.css
>     ├── professor.css
>     ├── project.css
>     ├── project-linebot.css
>     └── tools.css
> ```

| # | 現有檔案 | 去處 | 動作 | 說明 |
|---|---------|------|------|------|
| 1 | `globals.css` | `base.css` | 保留核心內容，改名 | 含 Google Fonts 載入、footer 基礎樣式；移除 AnimaApp 追蹤像素（第 3 行）；字型宣告保留 |
| 2 | `styleguide.css` | `tokens.css` | 合併後刪除 | `:root` 色彩/字型 token 遷移至 `tokens.css`；utility class（`.notosans-*`）評估是否遷移 `base.css` |
| 3 | `responsee.css` | 原地保留，不動 | 保留 | 第三方框架，不納入重構範圍；在 `base.css` 中加覆蓋層修正 `body color: #ffffff` 衝突 |
| 4 | `template-style.css` | 原地保留，不動 | 保留（局部覆蓋） | Responsee 框架客製化層；在 `base.css` 加覆蓋修正衝突 4（`.button` 自我覆蓋）、衝突 5（`nav` 自我覆蓋）、衝突 6（Playfair Display 強制標題）；不直接編輯此檔 |
| 5 | `components.css` | `components/button.css` + `components/modal.css` | 拆分 | `.button` 規則提取至 `button.css`；Modal/Tab 相關提取至 `modal.css`；原檔廢棄 |
| 6 | `icons.css` | 原地保留，不動 | 保留 | 本地圖示字型（`mfg`）聲明，無衝突，不動 |
| 7 | `stark_lab_home.css` | `pages/home.css` | 改名 + 清理 | 保留 `.expanded`（JS 依賴，禁止改名）；`#F3F3F3` 替換為 `var(--color-gray-50)`；`#1088E1` 替換為 `var(--color-brand-primary)`；`#191a23` 替換為 `var(--color-brand-shadow)` |
| 8 | `stark_lab_member.css` | `pages/member.css` | 改名 + 清理 | 非標準小數間距（`34.8px`、`99.4px`）記錄於 pitfall log，計畫書不動 |
| 9 | `stark_lab_professor.css` | `pages/professor.css` | 改名 + 清理 | `16.4px` → `var(--font-size-s)`；模板目前為內嵌 CSS，遷移時需加 `<link>` tag |
| 10 | `stark_lab_project.css` | `pages/project.css` | 改名 + 清理 | 模板目前為內嵌 CSS；photo 相關共用 class 提取至 `components/photo-gallery.css` |
| 11 | `stark_lab_project_linebot.css` | `pages/project-linebot.css` | 改名 + 清理 | 衝突 1（三檔同 class）釐清後，確認此為主檔；`22px` → `var(--font-size-xl)` |
| 12 | `stark_lab_project3.css` | 刪除 | 刪除 | 衝突 1：與 `project_linebot.css` 及 `project_war.css` 對同一 class 有三份不同定義；確認無模板使用此檔後刪除 |
| 13 | `stark_lab_project_war.css` | `pages/project.css`（合併） | 合併後刪除 | 與 `stark_lab_project.css` 共用大量 class（衝突 7 photo 系列）；photo 共用部分提取至 `components/photo-gallery.css`，頁面差異部分合併進 `pages/project.css` 後此檔刪除 |
| 14 | `style.css` | `pages/tools.css` | 改名 + 清理 | 工具頁（financial、translate）使用；`body` 樣式移至頁面容器 selector |

---

## 2. 元件清單

> **依據**：conflicts.md 衝突分析 + tokens-draft.css 設計系統

| # | 元件名稱 | 目標檔案 | 來源（現有 CSS）| 說明 |
|---|---------|---------|---------------|------|
| 1 | **Navbar** | `components/navbar.css` | `stark_lab_home.css`（`.navigation-bar`）、`template-style.css`（`nav`、衝突 5）| 全站導覽列；修正 `nav` 自我覆蓋衝突；保護 `.expanded` class 不改名 |
| 2 | **Card** | `components/card.css` | `stark_lab_home.css`（`.card`、`.card-1`、`.card.expanded`）、`stark_lab_project.css`（`.project-card`）| 含 default / expanded / dark 三種 variant；保留 `.expanded` class（JS 依賴）；品牌 solid shadow token 套用 |
| 3 | **Button** | `components/button.css` | `components.css`（`.button`）、`template-style.css`（衝突 4）| 合併三層覆蓋為一份；狀態：default / hover / active / disabled |
| 4 | **Footer** | `components/footer.css` | `globals.css`（`.footer`）| 頁尾圓角、padding、背景；`45px` border-radius 用 `var(--radius-2xl)` |
| 5 | **Badge / Tag** | `components/badge.css` | `stark_lab_professor.css`（section tag）、`stark_lab_member.css`（label）、`stark_lab_project_linebot.css`（badge）| 統一 `7px`/`9px` 圓角為 `var(--radius-sm)` / `var(--radius-md)` |
| 6 | **Photo Gallery** | `components/photo-gallery.css` | `stark_lab_project3.css`（衝突 7 第 432–460 行）、`stark_lab_project_war.css`（衝突 7 第 531–559 行）| 提取完全相同的 `.photo-container`、`.photo-section`、`.photo`、`.caption`、`.photo:hover`，消除重複 |
| 7 | **Modal / Tab** | `components/modal.css` | `components.css`（Tab 背景 `#262626`、Reload/Cancel 按鈕）| 含 modal overlay / tab panel；overlay 使用 `--z-index-overlay` |
| 8 | **Clickable Text** | `components/button.css`（內部 modifier）| `stark_lab_project_linebot.css`（`.clickable-text`，衝突 10）| 局部定義移至共用 button.css，避免其他頁面無法使用 |

---

## 3. 遷移順序（3 批）

> **重要原則**：每批需老闆批准方可動工；每批完成後必須做視覺截圖比對，驗收通過才進入下一批。

### 第 1 批 — Token 層 + Base 層

**目標**：建立設計基礎，不動任何 HTML，不影響視覺輸出。

- 建立 `tokens.css`（從 `tokens-draft.css` 正式化）
- 建立 `base.css`（從 `globals.css` 整理，移除 AnimaApp 追蹤像素）
- 在 `base.css` 加覆蓋層，修正 `responsee.css` 的 `body color: #ffffff` 衝突（衝突 2）
- 修正衝突 6（Playfair Display 強制 heading，加 `font-family: inherit` 覆蓋）

**HTML 改動**：無。僅新增 CSS 檔，不改任何模板。

**持續時間預估**：1 天（只建檔，不動現有 CSS）

---

### 第 2 批 — Components 層

**目標**：提取共用元件，消除重複 class（衝突 4、5、7、10）。

- 建立 `components/navbar.css`（修正衝突 5）
- 建立 `components/card.css`（`.card`、`.card-1`、`.card.expanded`；保護 `.expanded`）
- 建立 `components/button.css`（合併衝突 4 的三層覆蓋；遷移 `.clickable-text`）
- 建立 `components/footer.css`（從 `globals.css` 提取）
- 建立 `components/badge.css`（統一標籤圓角）
- 建立 `components/photo-gallery.css`（消除衝突 7 重複）
- 建立 `components/modal.css`（從 `components.css` 提取）
- 在受影響模板的 `<head>` 加入新 `<link>` tag（`{% static 'css/components/...' %}`）
- 注解或移除舊 `components.css` 中已提取的部分

**HTML 改動**：受影響模板加 `<link>` tag，但不改任何 CSS class 名稱。

**持續時間預估**：2–3 天

---

### 第 3 批 — Pages 層

**目標**：將頁面專屬樣式遷移至 `pages/` 子目錄，清理廢棄檔案，消除衝突 1、3、8。

- 建立並遷移 `pages/home.css`（清理 `#F3F3F3`、`#1088E1` 等硬編碼，衝突 3、8）
- 建立並遷移 `pages/member.css`
- 建立並遷移 `pages/professor.css`（含內嵌 CSS 外部化，補 `<link>` tag）
- 建立並遷移 `pages/project.css`（解決衝突 1；合併 `stark_lab_project_war.css`）
- 建立並遷移 `pages/project-linebot.css`（清理 `22px`、`83px` 等非標準值）
- 建立並遷移 `pages/tools.css`（`style.css` 改名，`body` 樣式移至容器 selector）
- 刪除確認廢棄的 `stark_lab_project3.css`
- 高風險頁面（`stark_lab_project_financial.html`、`stark_lab_project_stock.html`、`financial_1/2/3.html`）最後處理或保留內嵌 CSS 不動（依老闆決策）

**HTML 改動**：內嵌 CSS 的模板需加 `{% load static %}` 及 `<link>` tag；外部 CSS 模板需更新路徑。

**持續時間預估**：3–5 天

---

## 4. 每批 diff-level 預覽

### 第 1 批

| 動作 | 檔案 | 說明 |
|------|------|------|
| 新增 | `mylab/static/css/tokens.css` | 從 `tokens-draft.css` 正式建立 |
| 新增 | `mylab/static/css/base.css` | 從 `globals.css` 重組，加 responsee/template 覆蓋層 |
| 修改 | `index.html` | 在 `<link>` 清單最前面加 `tokens.css`、`base.css`（確保覆蓋層生效） |
| 修改 | `stark_lab_home.html` | 加 `tokens.css`（若尚未載入） |
| 修改 | `stark_lab_member.html` | 加 `tokens.css` |
| 修改 | `stark_lab_project_etfbot.html` | 加 `tokens.css` |
| 修改 | `stark_lab_project_stock.html` | 加 `tokens.css` |
| 不動 | `globals.css` | 保留，第 3 批前維持現狀 |
| 不動 | `styleguide.css` | 保留，第 3 批前維持現狀 |

### 第 2 批

| 動作 | 檔案 | 說明 |
|------|------|------|
| 新增 | `mylab/static/css/components/navbar.css` | 提取 nav 樣式，修正衝突 5 |
| 新增 | `mylab/static/css/components/card.css` | 提取 card 樣式（含 `.expanded`） |
| 新增 | `mylab/static/css/components/button.css` | 合併 button 三層，新增 `.clickable-text` |
| 新增 | `mylab/static/css/components/footer.css` | 提取 footer 樣式 |
| 新增 | `mylab/static/css/components/badge.css` | 統一 badge/tag 圓角 |
| 新增 | `mylab/static/css/components/photo-gallery.css` | 消除衝突 7 重複定義 |
| 新增 | `mylab/static/css/components/modal.css` | 提取 modal/tab |
| 修改 | `index.html` | 加 7 個 components `<link>` tag |
| 修改 | `stark_lab_home.html` | 加 `components/card.css`、`components/navbar.css` 等 `<link>` |
| 修改 | `stark_lab_member.html` | 加對應 components `<link>` |
| 修改 | `stark_lab_project_etfbot.html` | 加對應 components `<link>` |
| 修改 | `stark_lab_project_stock.html` | 加對應 components `<link>` |
| 不動 | `components.css` | 舊檔暫時保留（第 3 批清理） |
| 不動 | `stark_lab_home.css`（等） | 舊頁面 CSS 暫時保留 |

### 第 3 批

| 動作 | 檔案 | 說明 |
|------|------|------|
| 新增 | `mylab/static/css/pages/home.css` | 從 `stark_lab_home.css` 遷移，清理硬編碼 |
| 新增 | `mylab/static/css/pages/member.css` | 從 `stark_lab_member.css` 遷移 |
| 新增 | `mylab/static/css/pages/professor.css` | 從 `stark_lab_professor.css` 遷移（或從內嵌 CSS 提取） |
| 新增 | `mylab/static/css/pages/project.css` | 合併 `stark_lab_project.css` + `stark_lab_project_war.css` |
| 新增 | `mylab/static/css/pages/project-linebot.css` | 從 `stark_lab_project_linebot.css` 遷移 |
| 新增 | `mylab/static/css/pages/tools.css` | `style.css` 改名 + `body` 規則移至容器 |
| 刪除 | `stark_lab_project3.css` | 衝突 1 廢棄檔（確認無 HTML 引用後刪除） |
| 刪除 | `stark_lab_project_war.css` | 已合併至 `pages/project.css` |
| 刪除 | `stark_lab_home.css` | 已遷移至 `pages/home.css` |
| 刪除 | `stark_lab_member.css` | 已遷移至 `pages/member.css` |
| 刪除 | `globals.css` | 內容已拆至 `tokens.css` + `base.css` |
| 刪除 | `styleguide.css` | 內容已遷移至 `tokens.css` |
| 刪除 | `components.css` | 已拆至各 `components/` 子檔 |
| 修改 | `stark_lab_home.html` | 更新 `<link>` 路徑；刪除廢棄注解 `<link>` |
| 修改 | `stark_lab_member.html` | 更新 `<link>` 路徑 |
| 修改 | `stark_lab_project_etfbot.html` | 更新路徑；刪除廢棄注解 |
| 修改 | `stark_lab_project_stock.html` | 更新路徑；刪除廢棄注解 |
| 修改 | `stark_lab_professor.html` | 加 `{% load static %}` + `<link>` tag（若選擇外部化） |
| 修改 | `stark_lab_project.html` | 加 `{% load static %}` + `<link>` tag（若選擇外部化） |
| 保留不動 | `stark_lab_project_financial.html` | 高風險，保留內嵌 CSS（等老闆決策） |
| 保留不動 | `stark_lab_project_stock.html` JS | 保留 `.recording` JS 操作不動 |
| 保留不動 | `financial_1/2/3.html` | 高風險，本次排除 |

---

## 5. 風險與回滾策略

### 第 1 批回滾

**失敗情境**：`tokens.css` 或 `base.css` 的覆蓋層造成視覺異常（例如字型/顏色錯誤）。

**回滾指令**：
```bash
# 移除新增的 CSS 檔案，並從 Git 回到上一個狀態
git revert HEAD          # 若為單一 commit，直接 revert
# 或
git checkout HEAD~1 -- mylab/static/css/tokens.css
git checkout HEAD~1 -- mylab/static/css/base.css
# 同步移除模板中新增的 <link> tag
git checkout HEAD~1 -- mylab/templates/*.html
```

**預期損失**：零（第 1 批不動現有 CSS，只新增檔案；移除新檔即完全回到原狀態）。

---

### 第 2 批回滾

**失敗情境**：元件 CSS 提取後，部分頁面元件樣式破壞（例如 button hover 失效、卡片陰影消失）。

**回滾指令**：
```bash
# 以第 2 批的起始 commit hash（$BATCH2_START）為基準
git revert $BATCH2_START..$BATCH2_END --no-commit
git commit -m "revert: 回滾第 2 批 components 遷移"
# 或直接 reset 到第 2 批前
git reset --hard $BATCH2_START
```

**預期損失**：低（現有舊 CSS 檔在第 2 批仍保留，瀏覽器暫時並存兩套規則，不會破壞功能）。

---

### 第 3 批回滾

**失敗情境**：頁面 CSS 遷移後，某頁面視覺嚴重偏差；或內嵌 CSS 外部化後 Django collectstatic 未重跑導致 404。

**回滾指令**：
```bash
# 回滾第 3 批全部 commit
git revert $BATCH3_START..$BATCH3_END --no-commit
git commit -m "revert: 回滾第 3 批 pages 遷移"

# 若為 collectstatic 問題（不需 git，只需重跑）
python manage.py collectstatic --noinput

# 若已刪除舊 CSS 並回滾，可從 Git 還原
git checkout HEAD~N -- mylab/static/css/stark_lab_home.css
git checkout HEAD~N -- mylab/static/css/globals.css
# ... 其他已刪除舊檔
```

**特別注意**：
- 第 3 批刪除舊 CSS 檔前，必須確認 Git 已有乾淨 commit（回滾基點）
- 高風險頁面（`financial`、`stock` 複雜 JS 頁面）第 3 批不動，避免 `.recording`、`.expanded` class 遭誤改
- 每次刪除前確認 `git status` 乾淨，以確保可以完整還原

---

## 6. 驗收方法

### 視覺驗證流程（每批必做）

**Step 1 — 執行前截圖**

在每批動工前，對以下頁面截圖並存於 `docs/design/screenshots/before/`：

| 頁面 | URL |
|------|-----|
| 首頁（index） | `/` |
| 實驗室首頁 | `/home` 或對應路由 |
| 成員頁 | `/member` |
| 教授頁 | `/professor` |
| 專案列表頁 | `/project` |
| Linebot 專案頁 | `/project/linebot` |
| 工具頁（translate） | `/translate` |

截圖規格：桌機（1440×900）。

**Step 2 — 執行後截圖**

批次完成後，對同樣頁面截圖，存於 `docs/design/screenshots/after-batch{N}/`。

**Step 3 — 逐一比對**

使用瀏覽器開發工具或截圖比對工具（如 BackstopJS、或手動並排比對），確認：

| 項目 | 驗收標準 |
|------|---------|
| 字型 | Noto Sans TC / Noto Sans / Space Grotesk 正確載入 |
| 品牌主色 | `#0f87e0`（--color-brand-primary）顯示一致 |
| 卡片陰影 | `0px 5px 0px` 實心陰影正確顯示 |
| `.expanded` 功能 | 首頁卡片點擊展開/收合動畫正常 |
| `.recording` 功能 | translate 頁錄音按鈕狀態正常 |
| 圓角 | 卡片、按鈕圓角未破壞 |
| 間距 | 頁面水平邊距 `100px` 維持一致 |
| 無 404 | 所有 CSS 檔案 HTTP 200（DevTools Network 確認） |
| 無 console error | 開發者工具 Console 無紅色錯誤 |

**Step 4 — Django collectstatic 確認**

每批模板有變更時，執行：
```bash
python manage.py collectstatic --noinput
```
並重啟 Django dev server 確認靜態檔案路徑正確。

---

> **計畫版本 v1.0** — 待老闆批准，批准後方可進入第 1 批動工。
