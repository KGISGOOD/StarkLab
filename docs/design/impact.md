# 模板影響評估表

> **文件狀態**: 計畫草案（待老闆批准後方可動工）
> **產出者**: frontend-engineer（T2）
> **產出日期**: 2026-05-02
> **輸入來源**: tech-constraints.md（Template → CSS 對應表、高風險頁面清單、JS 保護 class 清單）

---

## 說明

本表列出所有 15 個模板（含 financial_1/2/3 合為一組）：
- 目前使用哪些 CSS（外部檔案或內嵌 `<style>`）
- 每一批次的影響範圍
- 風險等級（直接引用 `tech-constraints.md` §7）
- 特殊注意事項

---

## 模板影響評估總表

| 模板 | 目前 CSS 方式 | 第 1 批影響 | 第 2 批影響 | 第 3 批影響 | 風險等級 | 特殊注意 |
|------|-------------|-----------|-----------|-----------|---------|---------|
| `stark_lab_home.html` | 外部（3 檔） | 加 `<link>` tokens.css | 加 components `<link>` | 路徑更新；刪廢棄注解 | ⚠️ 中高 | JS `.expanded` 禁止改名；JS inline `style.height` 動畫 |
| `stark_lab_member.html` | 外部（3 檔） | 加 `<link>` tokens.css | 加 components `<link>` | 路徑更新 | 低 | 無特殊 JS 依賴 |
| `stark_lab_professor.html` | 內嵌 `<style>` | 無（不動 HTML） | 無（不動 HTML） | 加 `{% load static %}` + `<link>`（選擇性） | 中 | 內嵌 CSS 遷移需老闆另行決策（選項 A 或 B） |
| `stark_lab_project.html` | 內嵌 `<style>` | 無 | 無 | 加 `{% load static %}` + `<link>`（選擇性） | 中 | 同上 |
| `stark_lab_project_etfbot.html` | 外部（3 檔） | 加 `<link>` tokens.css | 加 components `<link>` | 路徑更新；刪廢棄注解 | 低 | 無特殊 JS 依賴 |
| `stark_lab_project_financial.html` | 內嵌 `<style>` | 無 | 無 | 保留內嵌，不動（高風險） | 🔴 高 | 複雜 JS 互動；不在第 3 批動工範圍，需另立任務 |
| `stark_lab_project_linebot.html` | 內嵌 `<style>` | 無 | 無 | 加 `{% load static %}` + `<link>`（選擇性） | 中 | 衝突 1（三檔重複 class）影響此頁，需確認使用哪個 CSS |
| `stark_lab_project_stock.html` | 外部（3 檔） | 加 `<link>` tokens.css | 加 components `<link>` | 路徑更新；刪廢棄注解 | 🔴 高 | 複雜 JS 互動；最後批次處理 |
| `stark_lab_project_wra.html` | 內嵌 `<style>` | 無 | 無 | 加 `{% load static %}` + `<link>`（選擇性） | 中 | 無特殊 JS 依賴 |
| `stark_lab_project_wra_report.html` | 內嵌 `<style>` | 無 | 無 | 加 `{% load static %}` + `<link>`（選擇性） | 低 | 無特殊 JS 依賴 |
| `stark_lab_trans.html` | 內嵌 `<style>` | 無 | 無 | 加 `{% load static %}` + `<link>`（選擇性） | ⚠️ 中高 | JS `.recording` class 禁止改名（錄音按鈕狀態） |
| `translate.html` | 內嵌 `<style>` | 無 | 無 | 加 `{% load static %}` + `<link>`（選擇性） | ⚠️ 中高 | JS `.recording` class 禁止改名；`element.style.display` 控制 `#updating-text` |
| `index.html` | 外部（6 檔） | 加 `<link>` tokens.css、base.css（最前） | 加 components `<link>` | 路徑整理 | 中 | owl-carousel CSS 不動（第三方）；`components.css`、`icons.css`、`responsee.css`、`template-style.css` 保留 |
| `news.html` | 無 CSS 引入 | 無 | 無 | 無 | 低 | JS `element.style.display` 控制 `#updating-text`（但無 CSS 依賴） |
| `financial_1/2/3.html` | 內嵌 `<style>` | 無 | 無 | 保留內嵌，不動（高風險） | 🔴 高 | 金融教學頁面；本次排除重構範圍 |

---

## 逐模板詳細說明

### 1. `stark_lab_home.html`

**目前 CSS 載入**（外部檔案，含廢棄注解）：
```html
<!-- 有效 link -->
{% static 'css/stark_lab_home.css' %}
{% static 'css/styleguide.css' %}
{% static 'css/globals.css' %}
<!-- 廢棄注解（第 3 批清理）：/static/css/stark_lab_home.css、styleguide.css、globals.css -->
```

**批次影響**：
- 第 1 批：在 `<head>` 最前加入 `{% static 'css/tokens.css' %}` + `{% static 'css/base.css' %}`
- 第 2 批：加入對應 components `<link>` tag（`card.css`、`navbar.css`、`button.css`、`footer.css`）
- 第 3 批：`stark_lab_home.css` 改路徑為 `css/pages/home.css`；刪除廢棄注解；移除 `styleguide.css`（內容已在 `tokens.css`）；移除 `globals.css`（內容已在 `base.css`）

**風險等級**：⚠️ 中高（tech-constraints.md §7：「有 JS class 操作」）

**特殊注意**：
- `.expanded` class 由 JS `classList.add/remove` 操作 → **禁止改名、禁止移除**
- JS 直接操作 `element.style.height` 做展開高度動畫 → 不動 JS，只整理 CSS
- 第 3 批硬編碼清理：`#F3F3F3` → `var(--color-gray-50)`、`#1088E1` → `var(--color-brand-primary)`、`#191a23` → `var(--color-brand-shadow)`

---

### 2. `stark_lab_member.html`

**目前 CSS 載入**（外部檔案，無廢棄注解）：
```html
{% static 'css/stark_lab_member.css' %}
{% static 'css/styleguide.css' %}
{% static 'css/globals.css' %}
```

**批次影響**：
- 第 1 批：加 `tokens.css`、`base.css`
- 第 2 批：加 `badge.css`、`footer.css`、`navbar.css`
- 第 3 批：`stark_lab_member.css` → `pages/member.css`；移除 `styleguide.css`、`globals.css`

**風險等級**：低（tech-constraints.md §2）

**特殊注意**：無 JS 依賴。非標準小數間距（`34.8px`、`99.4px`、`99px gap`）維持原值，不在本批清理範圍。

---

### 3. `stark_lab_professor.html`

**目前 CSS 載入**：**全部內嵌 `<style>`**（無外部 CSS 引用）

**批次影響**：
- 第 1 批：無影響
- 第 2 批：無影響
- 第 3 批：依老闆決策選擇處理方式：
  - 選項 A：保留內嵌，僅在內嵌 `<style>` 頂部加 `@import` 或確認繼承 token（最低風險）
  - 選項 B：提取內嵌 CSS 至 `pages/professor.css`，模板加 `{% load static %}` + `<link>` tag

**風險等級**：中（tech-constraints.md §2）

**特殊注意**：
- `16.4px` 非標準字級（`stark_lab_professor.css`）→ 第 3 批替換為 `var(--font-size-s)`
- `#363636` 字色硬編碼多次 → 替換為 `var(--color-text-body)`

---

### 4. `stark_lab_project.html`

**目前 CSS 載入**：**全部內嵌 `<style>`**

**批次影響**：
- 第 1–2 批：無影響
- 第 3 批：依老闆決策（選項 A / B，同上）；`photo` 相關共用 class 可抽至 `components/photo-gallery.css`

**風險等級**：中（tech-constraints.md §2）

**特殊注意**：
- 衝突 7（photo class 完全重複）清理後，`photo-gallery.css` 可被此模板和 `project_war` 共用
- `#1a3e6f` 深海軍藍硬編碼大量出現 → 第 3 批統一為 `var(--color-brand-deep)`（待設計師確認）

---

### 5. `stark_lab_project_etfbot.html`

**目前 CSS 載入**（外部檔案，含廢棄注解）：
```html
{% static 'css/stark_lab_project_linebot.css' %}
{% static 'css/styleguide.css' %}
{% static 'css/globals.css' %}
<!-- 廢棄注解（同上 3 個）-->
```

**批次影響**：
- 第 1 批：加 `tokens.css`、`base.css`
- 第 2 批：加對應 components
- 第 3 批：`stark_lab_project_linebot.css` → `pages/project-linebot.css`；刪廢棄注解

**風險等級**：低

**特殊注意**：無特殊 JS 依賴。

---

### 6. `stark_lab_project_financial.html`

**目前 CSS 載入**：**全部內嵌 `<style>`**

**批次影響**：全三批均**無影響**（高風險頁面，本次排除）

**風險等級**：🔴 高（tech-constraints.md §7：「複雜 JS 互動、內嵌 CSS」）

**特殊注意**：
- 需另立獨立任務處理，不納入本次 Sprint 重構範圍
- 操作前必須完整記錄頁面所有 JS 行為

---

### 7. `stark_lab_project_linebot.html`

**目前 CSS 載入**：**全部內嵌 `<style>`**

**批次影響**：
- 第 1–2 批：無影響
- 第 3 批：衝突 1 處理（確認此模板對應哪個 CSS 檔後遷移）

**風險等級**：中

**特殊注意**：
- 衝突 1 — `.stark_lab_project_linebot` 同 class 在三個 CSS 檔有不同定義；**動工前必須確認此模板使用哪個 CSS**（`stark_lab_project3.css` / `stark_lab_project_linebot.css` / `stark_lab_project_war.css`），再決定保留哪一份
- `height: 2851px` 固定高度問題 → 第 3 批改為 `min-height: 100vh`

---

### 8. `stark_lab_project_stock.html`

**目前 CSS 載入**（外部檔案，含廢棄注解）：
```html
{% static 'css/stark_lab_project_linebot.css' %}
{% static 'css/styleguide.css' %}
{% static 'css/globals.css' %}
<!-- 廢棄注解（同上 3 個）-->
```

**批次影響**：
- 第 1 批：加 `tokens.css`、`base.css`
- 第 2 批：加對應 components
- 第 3 批：路徑更新；刪廢棄注解；**但 JS 互動部分不動**

**風險等級**：🔴 高（tech-constraints.md §7：「複雜 JS 互動」）

**特殊注意**：
- 此頁含複雜 JS 互動，第 3 批僅做 `<link>` 路徑更新，不改任何 CSS 規則
- 驗收時需專門測試 JS 功能是否正常

---

### 9. `stark_lab_project_wra.html`

**目前 CSS 載入**：**全部內嵌 `<style>`**

**批次影響**：
- 第 1–2 批：無影響
- 第 3 批：依老闆決策（選項 A / B）

**風險等級**：中

**特殊注意**：無特殊 JS 依賴。

---

### 10. `stark_lab_project_wra_report.html`

**目前 CSS 載入**：**全部內嵌 `<style>`**

**批次影響**：
- 第 1–2 批：無影響
- 第 3 批：依老闆決策（選項 A / B）

**風險等級**：低

**特殊注意**：無特殊 JS 依賴，報告頁面，CSS 簡單。

---

### 11. `stark_lab_trans.html`

**目前 CSS 載入**：**全部內嵌 `<style>`**

**批次影響**：全三批均**無影響**（內嵌 CSS，JS 高依賴）

**風險等級**：⚠️ 中高

**特殊注意**：
- JS `classList.add/remove` 操作 `.recording` class → **禁止改名、禁止移除**
- 若第 3 批選擇選項 B 外部化，需確保 `.recording` class 在外部 CSS 中存在且與 JS 完全一致

---

### 12. `translate.html`

**目前 CSS 載入**：**全部內嵌 `<style>`**

**批次影響**：全三批均**無影響**（內嵌 CSS，JS 高依賴）

**風險等級**：⚠️ 中高

**特殊注意**：
- JS `classList.add/remove` 操作 `.recording` class → **禁止改名、禁止移除**
- JS `element.style.display` 控制 `#updating-text` → CSS 不設定此 element 的 `display`
- 此頁與 `stark_lab_trans.html` 功能重疊，需確認兩者關係

---

### 13. `index.html`

**目前 CSS 載入**（外部檔案，共 6 個）：
```html
{% static 'css/components.css' %}
{% static 'css/icons.css' %}
{% static 'css/responsee.css' %}
{% static 'css/owl-carousel/owl.carousel.css' %}
{% static 'css/owl-carousel/owl.theme.css' %}
{% static 'css/template-style.css' %}
```

**批次影響**：
- 第 1 批：在最前面加 `tokens.css`、`base.css`（確保覆蓋層優先順序）
- 第 2 批：加 components `<link>` tag（button、navbar、footer 等）
- 第 3 批：移除 `components.css`（已拆至各 components/）；其餘 5 個檔保留

**風險等級**：中

**特殊注意**：
- `owl-carousel/owl.carousel.css` 和 `owl.theme.css` 為第三方 CSS，**絕對不動**
- `responsee.css` 和 `template-style.css` 為框架 CSS，**絕對不動**
- `icons.css` 為本地圖示字型，**絕對不動**
- `base.css` 的覆蓋層需在 `responsee.css` 和 `template-style.css` 之後載入，才能正確覆蓋衝突

---

### 14. `news.html`

**目前 CSS 載入**：**無任何 CSS 引入**

**批次影響**：全三批均無影響

**風險等級**：低

**特殊注意**：
- JS `element.style.display` 控制 `#updating-text`，但無 CSS 依賴，不影響重構

---

### 15. `financial_1/2/3.html`（三個頁面合組）

**目前 CSS 載入**：**全部內嵌 `<style>`**

**批次影響**：全三批均**無影響**（高風險，本次排除）

**風險等級**：🔴 高（tech-constraints.md §7：「金融教學頁面、內嵌 CSS」）

**特殊注意**：
- 與 `stark_lab_project_financial.html` 性質相近，均屬高風險金融頁面
- 本次 Sprint 排除範圍，需後續另立任務

---

## 影響範圍統計

| 批次 | 影響模板數 | HTML 改動類型 | 不影響模板 |
|------|-----------|-------------|----------|
| 第 1 批 | 5 個（外部 CSS 模板） | 只加 `<link>` | 10 個（內嵌 CSS 模板） |
| 第 2 批 | 5 個（同上） | 只加 `<link>` | 10 個 |
| 第 3 批 | 最多 10 個（視老闆決策） | 路徑更新 + 可選內嵌外部化 | 高風險 3 個排除 |

---

## JS 保護 Class 彙整

> 引用自 tech-constraints.md §3。以下 class **任何批次均禁止改名或移除**：

| Class | 所在模板 | JS 操作 | 用途 |
|-------|---------|---------|------|
| `.expanded` | `stark_lab_home.html` | `classList.add/remove` | 卡片展開/收合 |
| `.recording` | `translate.html`、`stark_lab_trans.html` | `classList.add/remove` | 錄音按鈕狀態 |
| `#updating-text` | `news.html`、`translate.html` | `element.style.display` | 更新中提示（ID，非 class；CSS 不設 display） |

---

> **文件版本 v1.0** — 待老闆批准，批准後方可進入第 1 批動工。
