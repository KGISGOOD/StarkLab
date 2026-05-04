# 技術約束清單（CSS 重構前置）

> **產出者**: tech-lead
> **日期**: 2026-05-03
> **用途**: 提供給 T2（CSS 收斂重構計畫）作為技術輸入，T2 必須在計畫中遵守本文件所有約束。

---

## 1. 靜態檔案路徑規則（Django）

| 項目 | 值 | 說明 |
|------|----|------|
| `STATIC_URL` | `/static/` | 瀏覽器存取前綴 |
| `STATICFILES_DIRS` | `mylab/static/` | 開發時來源目錄 |
| `STATIC_ROOT` | `staticfiles/` | collectstatic 輸出目錄 |
| Template 引用格式 | `{% static 'css/filename.css' %}` | 必須保持此格式，不可用相對路徑 |

**重構後的新 CSS 檔案路徑規則：**
- 開發位置：`mylab/static/css/` 子目錄（如 `mylab/static/css/components/navbar.css`）
- Template 引用：`{% static 'css/components/navbar.css' %}`
- **禁止**直接寫死路徑（`/static/css/...`），必須用 `{% static %}` tag

---

## 2. Template → CSS 依賴對應表

| 模板 | 目前載入的 CSS | 廢棄注解 | 高風險 |
|------|--------------|---------|--------|
| `stark_lab_home.html` | stark_lab_home.css, styleguide.css, globals.css | ✅ 有（3 個） | ⚠️ 有 JS class 操作 |
| `stark_lab_member.html` | stark_lab_member.css, styleguide.css, globals.css | 無 | 低 |
| `stark_lab_professor.html` | **無外部 CSS（全部內嵌 `<style>`）** | 無 | 中 |
| `stark_lab_project.html` | **無外部 CSS（全部內嵌 `<style>`）** | 無 | 中 |
| `stark_lab_project_etfbot.html` | stark_lab_project_linebot.css, styleguide.css, globals.css | ✅ 有（3 個） | 低 |
| `stark_lab_project_financial.html` | **無外部 CSS（全部內嵌 `<style>`）** | 無 | 高（含複雜 JS） |
| `stark_lab_project_linebot.html` | **無外部 CSS（全部內嵌 `<style>`）** | 無 | 中 |
| `stark_lab_project_stock.html` | stark_lab_project_linebot.css, styleguide.css, globals.css | ✅ 有（3 個） | 高（含複雜 JS） |
| `stark_lab_project_wra.html` | **無外部 CSS（全部內嵌 `<style>`）** | 無 | 中 |
| `stark_lab_project_wra_report.html` | **無外部 CSS（全部內嵌 `<style>`）** | 無 | 低 |
| `stark_lab_trans.html` | **無外部 CSS（全部內嵌 `<style>`）** | 無 | ⚠️ 有 JS class 操作 |
| `translate.html` | **無外部 CSS（全部內嵌 `<style>`）** | 無 | ⚠️ 有 JS class 操作 |
| `index.html` | components.css, icons.css, responsee.css, owl-carousel/owl.carousel.css, owl-carousel/owl.theme.css, template-style.css | 無 | 中（owl-carousel 依賴） |
| `news.html` | 無 CSS 引入 | 無 | 低 |
| `financial_1/2/3.html` | **無外部 CSS（全部內嵌 `<style>`）** | 無 | 高（金融教學頁面） |

---

## 3. JavaScript CSS 操作（不可在重構中改名的 class）

以下 class 名稱被 JavaScript 直接操作，**重構時禁止改名或移除**，否則會靜默破壞功能：

| 模板 | 操作 | 受保護的 class/style | 用途 |
|------|------|---------------------|------|
| `stark_lab_home.html` | `classList.add/remove` | `.expanded` | 卡片展開/收合 |
| `stark_lab_home.html` | `element.style.height` | （inline height 動畫） | 展開高度動畫 |
| `news.html` | `element.style.display` | `#updating-text` | 更新中提示顯示 |
| `translate.html` | `classList.add/remove` | `.recording` | 錄音按鈕狀態 |

> **未發現 jQuery `.addClass()` / `.css()` 操作** — 目前只用原生 JS，風險相對可控。

---

## 4. 「內嵌 CSS 模板」特殊處理說明

共 **9 個模板**使用內嵌 `<style>` block 而非外部 CSS 檔：
`stark_lab_professor`, `stark_lab_project`, `stark_lab_project_financial`,
`stark_lab_project_linebot`, `stark_lab_project_wra`, `stark_lab_project_wra_report`,
`stark_lab_trans`, `translate`, `financial_1/2/3`

**重構計畫建議**（T2 決定，tech-lead 無異議）：
- 選項 A：保留內嵌，只補 token 變數（最低風險）
- 選項 B：遷移到 `pages/` 子目錄的外部 CSS 檔（標準做法，但需動模板）

若選 B，每個模板需加 `{% load static %}` 並補 `<link>` tag，tech-lead 已確認無技術障礙。

---

## 5. collectstatic 行為注意

- 執行 `python manage.py collectstatic` 後，`mylab/static/` 內容會被複製到 `staticfiles/`
- 新增子目錄（如 `css/components/`）後，**不需要額外設定**，collectstatic 會自動遞迴複製
- **注意**：`staticfiles/` 目錄下有舊版 CSS 副本，部署後必須重新執行 collectstatic

---

## 6. 已廢棄的注解 CSS link（待清理）

以下模板有被注解掉的舊 CSS link，建議在 T2 第一批重構時一併清理：

| 模板 | 被注解的 link | 建議 |
|------|-------------|------|
| `stark_lab_home.html` | `/static/css/stark_lab_home.css`、`styleguide.css`、`globals.css` | 直接刪除 |
| `stark_lab_project_etfbot.html` | 同上 3 個 | 直接刪除 |
| `stark_lab_project_stock.html` | 同上 3 個 | 直接刪除 |

---

## 7. 高風險頁面清單（對應 T2 影響評估）

| 頁面 | 風險原因 | 建議處理順序 |
|------|---------|------------|
| `stark_lab_project_financial.html` | 複雜 JS 互動、內嵌 CSS | 最後批次（第 3 批） |
| `stark_lab_project_stock.html` | 複雜 JS 互動 | 最後批次（第 3 批） |
| `financial_1/2/3.html` | 金融教學頁面、內嵌 CSS | 最後批次或排除本次 |
| `stark_lab_home.html` | JS class 操作（`.expanded`） | 第 2 批，需同步更新 JS |
| `index.html` | 依賴 owl-carousel CSS（第三方） | 第 2 批，owl-carousel 不動 |
