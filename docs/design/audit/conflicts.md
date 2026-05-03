# 重複規則 / 衝突清單

> **產出時間**: 2026-05-03  
> **盤點範圍**: `labweb/lab/mylab/static/css/` 全部 14 個 CSS 檔  
> **執行者**: brand-guardian（T1）  
> **優先分級**：🔴 CRITICAL / 🟠 HIGH / 🟡 MEDIUM / 🟢 LOW

---

## 衝突 1 — 同一 class 在 3 個檔案中重複定義 🔴 CRITICAL

**受影響 Selector**：`.stark_lab_project_linebot`（根容器）

| 檔案 | `height` | `overflow` | 其他差異 |
|------|---------|-----------|---------|
| `stark_lab_project3.css` | `min-height: 100vh` | （無設定） | `position: relative`、footer `position: absolute; bottom: 0` |
| `stark_lab_project_linebot.css` | `height: 2851px`（固定！） | `overflow: hidden` | footer 無 absolute |
| `stark_lab_project_war.css` | `min-height: 100vh` | （無設定） | footer `position: absolute; bottom: 0; transform: translateX(-50%)` |

**問題說明**：
- 三個 CSS 檔案對同一 class 定義截然不同的高度策略，瀏覽器最終套用取決於 HTML 中的 `<link>` 載入順序
- `height: 2851px` 固定高度在小螢幕上會導致大量空白或內容溢出
- footer 定位方式三者不一（relative flow / absolute + bottom:0 / absolute + transform）

**修復建議**：
1. 確認哪個 HTML 模板使用哪個 CSS，將三個 CSS 合為一，刪除另外兩個
2. 統一使用 `min-height: 100vh` + footer `position: relative`（避免 absolute 定位帶來的 z-index 問題）

---

## 衝突 2 — `body` 樣式在 4 個檔案中相互覆蓋 🔴 CRITICAL

| 檔案 | `background` | `font-family` | `color` | `padding` |
|------|------------|--------------|---------|----------|
| `responsee.css` | `#eeeeee` | `"Open Sans", Arial` | `#ffffff` | — |
| `template-style.css` | `#fff` | — | — | — |
| `style.css` | `#f0f2f5` | `"Microsoft JhengHei"` | — | `20px` |

**問題說明**：
- `responsee.css` 預設 body 文字為白色（`color: #ffffff`），在淺色背景下造成文字不可見
- `style.css` 的 `padding: 20px` 會影響全局佈局
- `"Microsoft JhengHei"` 僅在 Windows 系統有效，macOS/Linux 會 fallback 到 sans-serif

**修復建議**：
- 建立統一的全域 base CSS，明確設定 body，覆蓋所有框架預設值
- `style.css` 的 body 規則移至頁面專屬容器 selector 中

---

## 衝突 3 — 品牌主色有 4 個不同「藍色」值 🔴 CRITICAL

| 色值 | 出現位置 | 命名 |
|------|---------|------|
| `#0f87e0` | `styleguide.css` `:root --navy-blue` | 官方 Brand Primary |
| `#1088E1` | `stark_lab_home.css` 硬編碼（.number, .fintech 等） | 疑為筆誤或 Figma 精度誤差 |
| `#1a3e6f` | `stark_lab_project.css` 硬編碼（全站） | 設計上的「深海軍藍」 |
| `#0d6fb7` | `template-style.css`（框架 primary） | Responsee 框架遺留 |

**問題說明**：
- `#0f87e0` 與 `#1088E1` 差異極小（約 0.6% hue 差），在螢幕上幾乎不可分辨，**強烈懷疑是 Anima/Figma 導出精度問題**
- `#1a3e6f` 是完全不同的顏色（深海軍藍 vs 亮藍），若為刻意設計需文件化；若為錯誤須修正
- 使用者無法從程式碼判斷哪個「藍」是主色

**修復建議**：
1. `#1088E1` → 統一改為 `var(--navy-blue)`（#0f87e0）
2. `#1a3e6f` → 需設計師確認；若保留，新增 `--color-brand-deep: #1a3e6f`
3. `#0d6fb7` → 框架色，標記為不使用，不納入品牌 token

---

## 衝突 4 — `.button` 在同一檔案內自我覆蓋 🟠 HIGH

**受影響檔案**：`template-style.css`

- **第 583–596 行**（Default Template Styles）：設定完整 border + color + padding
- **第 2025–2027 行**（Custom Template Styles）：`border: 0` 覆蓋上面的 border

**程式碼**：
```css
/* 第 583 行 */
.button, a.button, a.button:link, a.button:visited {
  border-color: rgba(255,255,255,0.4) rgba(255,255,255,0) rgba(0,0,0,0.3);
  border-style: solid;
  border-width: 1px;
  ...
}

/* 第 2025 行（同一檔案，後面的 custom 區覆蓋了前面） */
.button, a.button, a.button:link, a.button:visited {
  border: 0;
}
```

此外，`components.css` 中也有 `.button` 規則，形成三層覆蓋。

**修復建議**：合併 button 定義，保留一個，移除冗餘

---

## 衝突 5 — `nav` 在同一檔案內自我覆蓋 🟠 HIGH

**受影響檔案**：`template-style.css`

```css
/* 第 319 行（Default） */
nav {
  border-bottom: 4px solid rgba(0,0,0,0.05);
  border-top: 1px solid rgba(0,0,0,0.05);
  padding: 1.7rem 0;
}

/* 第 1927 行（Custom Template Styles） */
nav {
  border-bottom: 0px solid;
  border-bottom: 1px solid rgba(255,255,255,0.09); /* 自我重複！ */
  padding: 0 2rem;
}
```

**注意**：`border-bottom: 0px solid` 緊接著被 `border-bottom: 1px solid` 覆蓋，同一個 rule block 內有兩行相互矛盾。

**修復建議**：移除第一行（`border-bottom: 0px solid`），保留 `1px solid rgba(255,255,255,0.09)`

---

## 衝突 6 — 所有 h1~h6 被設定為 `"Playfair Display"` 字型 🟠 HIGH

**受影響檔案**：`template-style.css`（第 1903–1905 行）

```css
h1, h2, h3, h4, h5, h6, .h1, .h2, .h3, .h4, .h5, .h6 {
  font-family: "Playfair Display";
}
```

**問題說明**：
- 品牌字型為 Noto Sans / Space Grotesk，但 template 框架將所有標題強制設為 Playfair Display（Serif 字型）
- 不在 `globals.css` 的 Google Fonts 載入清單中，會直接 fallback
- Stark Lab 頁面透過 utility classes（如 `.notosans-bold-navy-blue-60px`）覆蓋，但需依賴 CSS 載入順序才生效

**修復建議**：刪除或覆蓋此規則，改為 `font-family: inherit`

---

## 衝突 7 — `photo-container` / `photo` 等 class 在兩個檔案中完全重複 🟡 MEDIUM

**受影響 Selectors**：`.photo-container`, `.photo-section`, `.photo`, `.caption`, `.photo:hover`

完全相同的規則分別出現在：
- `stark_lab_project3.css`（第 432–460 行）
- `stark_lab_project_war.css`（第 531–559 行）

**問題說明**：兩個專案頁面複製貼上了相同的 CSS，維護時需同步修改兩處。

**修復建議**：提取至共用 `components.css` 或新建 `shared-page.css`

---

## 衝突 8 — `#F3F3F3` 硬編碼與 `var(--grey)` 並用 🟡 MEDIUM

**受影響檔案**：`stark_lab_home.css`

```css
/* .card 使用硬編碼 */
background-color: #F3F3F3;

/* 但 .card.expanded 使用變數 */
background-color: var(--navy-blue);

/* .overlap-group2 使用變數 */
background-color: var(--grey); /* = #f3f3f3 */
```

同一檔案內混用硬編碼與 CSS 變數，修改時容易漏改。

**修復建議**：統一改為 `var(--grey)`

---

## 衝突 9 — `table` 在 3 個檔案中有不同基本設定 🟡 MEDIUM

| 檔案 | `border` | `background` | `border-collapse` |
|------|---------|------------|-----------------|
| `template-style.css` | `border: 0` | `#fff` | （無） |
| `responsee.css` | `border: 1px solid #f0f0f0` | `#fff` | `collapse: 0` |
| `style.css` | `1px solid #ddd`（td/th 各自設） | `#fff` | `collapse` |

**修復建議**：為不同頁面設定 page-scoped selector，避免全局 `table` 互相干擾

---

## 衝突 10 — `.clickable-text` class 僅在 `stark_lab_project_linebot.css` 中定義 🟢 LOW

但此 class 應為全站共用（連結樣式），局部定義可能造成其他頁面無法使用。

**修復建議**：移至 `components.css` 或新增的全站樣式表

---

## !important 使用統計

| 檔案 | !important 出現次數 | 說明 |
|------|-----------------|------|
| `template-style.css` | 50+ | 大量 utility classes（.text-white, .background-white 等） |
| `style.css` | 0 | 無 |
| `stark_lab_home.css` | 0 | 無 |
| `stark_lab_member.css` | 1 | `.group .link` 的 `left: auto !important; top: auto !important` |
| `stark_lab_professor.css` | 0 | 無 |
| `stark_lab_project.css` | 0 | 無 |
| `stark_lab_project_linebot.css` | 0 | 無 |
| `stark_lab_project_war.css` | 0 | 無 |
| `components.css` | 1 | `.button.disabled-btn { opacity: 0.2 !important }` |

> `template-style.css` 的 `!important` 密度高，是覆蓋困難的主因。建議在 T2 中評估是否需要保留框架，或逐步替換為品牌自定義元件。

---

## 高優先衝突摘要

| # | 衝突 | 嚴重度 | 修復成本 |
|---|------|--------|---------|
| 1 | `.stark_lab_project_linebot` 三檔重複 | 🔴 CRITICAL | 中（需確認 HTML 使用哪個） |
| 2 | `body` 四檔覆蓋 | 🔴 CRITICAL | 中 |
| 3 | 4 個不同藍色值 | 🔴 CRITICAL | 低（全局搜尋替換） |
| 4 | `.button` 同檔自我覆蓋 | 🟠 HIGH | 低 |
| 5 | `nav` 同 rule 兩行矛盾 | 🟠 HIGH | 低 |
| 6 | Playfair Display 強制覆蓋所有標題 | 🟠 HIGH | 低 |
| 7 | photo 相關 class 完全重複 | 🟡 MEDIUM | 低 |
| 8 | `#F3F3F3` 與 `var(--grey)` 並用 | 🟡 MEDIUM | 低 |
| 9 | `table` 三檔衝突 | 🟡 MEDIUM | 中 |
| 10 | `.clickable-text` 局部定義 | 🟢 LOW | 低 |
