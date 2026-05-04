# 顏色盤點表

> **產出時間**: 2026-05-03  
> **盤點範圍**: `labweb/lab/mylab/static/css/` 全部 14 個 CSS 檔  
> **執行者**: brand-guardian（T1）

---

## 一、CSS 自訂屬性（Brand Token）

定義於 `styleguide.css` `:root`，為全站唯一正式顏色命名來源：

| 變數名稱 | 值 | 語意 |
|---------|-----|------|
| `--black` | `#000000` | 純黑 |
| `--grey` | `#f3f3f3` | 淺灰背景 |
| `--mirage` | `#191a23` | 深色邊框/陰影 |
| `--navy-blue` | `#0f87e0` | 品牌主色（Figma 導出命名為 navy-blue，但實為亮藍） |
| `--white` | `#ffffff` | 純白 |

---

## 二、所有出現的色彩值（去重後共 **39 個**）

> ⚠️ 超過驗收標準 30 個上限，合併建議見第三節。

### 2.1 品牌藍色系（高優先衝突）

| 色值 | 出現次數 | 出現檔案 | 推測語意 |
|------|---------|---------|---------|
| `#0f87e0` | 多次 | `styleguide.css`（`:root --navy-blue`） | Brand Primary |
| `#1088E1` | 6+ | `stark_lab_home.css` | 與 `--navy-blue` 差一色階，疑為筆誤 |
| `#1a3e6f` | 10+ | `stark_lab_project.css` | 深海軍藍，設計稿獨立色 |
| `#0d6fb7` | 8+ | `template-style.css` | Responsee 框架 Primary（非品牌） |
| `#002633` | 10+ | `template-style.css` | Responsee 框架 Dark（非品牌） |
| `#152732` | 1 | `components.css`（tooltip bg） | 近似 `#002633`，可合併 |
| `#3498db` | 2 | `style.css` | 工具頁 button（非品牌） |
| `#2980b9` | 1 | `style.css` | 工具頁 button hover |

### 2.2 中性灰系

| 色值 | 出現次數 | 出現檔案 | 推測語意 |
|------|---------|---------|---------|
| `#ffffff` / `#fff` / `white` | 大量 | 全域 | 背景/文字 |
| `#f3f3f3` / `#F3F3F3` | 3+ | `styleguide.css`、`stark_lab_home.css` | 淡灰背景（有硬編碼重複） |
| `#f5f5f5` / `#F5F5F5` | 4+ | `template-style.css`、`components.css` | 表單輸入背景 |
| `#f0f2f5` | 1 | `style.css` | 工具頁 body 背景 |
| `#f0f0f0` | 2 | `responsee.css` | 表格 stripe |
| `#eeeeee` | 1 | `responsee.css` | body 背景 |
| `#ecf0f1` | 1 | `style.css` | 表頭背景 |
| `#e9e9e9` | 1 | `template-style.css` | 巢狀 nav 背景 |
| `#e8eef5` | 2 | `stark_lab_project.css` | 淺藍灰卡片背景 |
| `#e5e5e5` | 5+ | `template-style.css` | 分隔線/邊框 |
| `#e0e0e0` / `#E0E0E0` | 3 | `template-style.css`、`components.css` | 表單邊框、引用前景 |
| `#ddd` | 1 | `style.css` | 表格邊框 |
| `#ccc` | 1 | `style.css` | Select 邊框 |
| `#eee` | 2 | `stark_lab_professor.css`、`template-style.css` | 淡邊框 |
| `#C9C9C9` | 1 | `template-style.css` | Carousel 按鈕 |
| `#777` | 4+ | `template-style.css`、`components.css` | 次要文字/按鈕 |
| `#555` | 2 | `style.css`、`stark_lab_project_war.css` | Caption 文字 |
| `#444` | 2 | `template-style.css`、`components.css` | 次要按鈕 |
| `#363636` | 2 | `stark_lab_project_linebot.css`、`stark_lab_professor.css` | 正文/ORCID 連結 |
| `#333` | 2 | `template-style.css`、`stark_lab_professor.css` | 論文標題 |
| `#2c3e50` | 1 | `style.css` | h1（工具頁） |
| `#34495e` | 2 | `style.css` | 段落（工具頁） |
| `#262626` | 1 | `components.css` | Tab 背景 |
| `#191a23` | 2+ | `styleguide.css`（`--mirage`）、`stark_lab_home.css`（硬編碼） | 深色邊框 |
| `#888` | 1 | `stark_lab_professor.css` | 論文年份 |

### 2.3 狀態色 / 強調色

| 色值 | 出現次數 | 出現檔案 | 推測語意 |
|------|---------|---------|---------|
| `#27ae60` | 1 | `style.css` | 成功/保守風險 |
| `#9bdd42` | 1 | `template-style.css` | 表單成功 |
| `#9BB800` / `#B6C900` | 2 | `responsee.css` | 連結色（框架） |
| `#e67e22` | 1 | `style.css` | 警告/平衡風險 |
| `#ff9800` | 1 | `components.css` | Reload 按鈕 |
| `#e74c3c` | 1 | `style.css` | 錯誤/激進風險 |
| `#C81010` | 2 | `template-style.css` | 框架錯誤色 |
| `#dc003a` | 1 | `components.css` | Cancel 按鈕 |
| `#b4bf04` | 2 | `template-style.css`、`components.css` | Submit 按鈕（橄欖色） |

---

## 三、建議合併方向（超出 30 個，縮減至 ≤ 18 個）

| 合併目標 Token | 含蓋現有值 | 理由 |
|--------------|---------|------|
| `--color-brand-primary` → `#0f87e0` | `#0f87e0`、`#1088E1`（相差 1 色階，疑筆誤） | 統一品牌主色 |
| `--color-brand-dark` → `#1a3e6f` | `#1a3e6f` | project 頁深色主色，保留作 secondary brand |
| `--color-brand-shadow` → `#191a23` | `#191a23`（var 與硬編碼） | 統一用 var |
| `--color-white` → `#ffffff` | `#fff`、`white` | 統一 |
| `--color-black` → `#000000` | `#000`、`#000000` | 統一 |
| `--color-bg-light` → `#f3f3f3` | `#f3f3f3`、`#F3F3F3` | 統一，移除硬編碼 |
| `--color-bg-subtle` → `#f5f5f5` | `#f5f5f5`、`#F5F5F5`、`#f0f0f0`、`#eeeeee`、`#ecf0f1` | 合併相近淺灰背景 |
| `--color-border` → `#e5e5e5` | `#e5e5e5`、`#ddd`、`#ccc`、`#e0e0e0`、`#eee` | 統一邊框色 |
| `--color-text-body` → `#363636` | `#363636`、`#333`、`#2c3e50` | 正文文字 |
| `--color-text-secondary` → `#777` | `#777`、`#555`、`#888` | 次要文字 |
| `--color-text-tertiary` → `#444` | `#444`、`#34495e` | 三級文字/次要按鈕 |
| `--color-success` → `#27ae60` | `#27ae60`（保留業界標準綠） | 成功狀態 |
| `--color-warning` → `#e67e22` | `#e67e22` | 警告狀態 |
| `--color-error` → `#e74c3c` | `#e74c3c`、`#C81010`、`#dc003a` | 錯誤狀態 |
| `--color-info` → `#0d6fb7` | `#0d6fb7`（框架 primary，可作 Info） | 資訊藍 |
| `--color-framework-dark` → `#002633` | `#002633`、`#152732` | Responsee 框架色（不改，保持相容） |
| `--color-project-card-bg` → `#e8eef5` | `#e8eef5` | project 頁淺色卡片，暫保留 |
| `--color-accent-olive` → `#b4bf04` | `#b4bf04`、`#9BB800` | 框架遺留，可考慮移除 |

> 合併後預計 **18 個** 語意 token（達驗收標準 ≤ 30）

---

## 四、注意事項

- `#0f87e0`（`--navy-blue`）與 `#1088E1` 差異極小（約 1–2% 亮度），**強烈懷疑是 Figma 導出時的精度誤差**，T2 重構應統一為 `--navy-blue`。
- `#1a3e6f` 是 `stark_lab_project.css` 獨立定義的深藍，**與品牌 `--navy-blue` 差異極大**，需設計師確認是否為刻意的設計決策或待修正的偏差。
- Responsee 框架顏色（`#002633`、`#0d6fb7`、`#9BB800` 等）為第三方樣式表遺留，**不應納入品牌 token**，但短期維持相容。
