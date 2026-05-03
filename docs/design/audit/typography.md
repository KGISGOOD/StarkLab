# 字級 / 字型盤點表

> **產出時間**: 2026-05-03  
> **盤點範圍**: `labweb/lab/mylab/static/css/` 全部 14 個 CSS 檔  
> **執行者**: brand-guardian（T1）

---

## 一、字型家族（Font Family）

### 1.1 品牌字型（Google Fonts，由 `globals.css` 載入）

| 變數名稱 | 字型名稱 | Fallback | 用途 |
|---------|---------|---------|------|
| `--font-family-noto_sans_tc` | `"Noto Sans TC"` | Helvetica | 繁體中文主字型 |
| `--font-family-noto_sans` | `"Noto Sans"` | Helvetica | 英文/數字主字型 |
| `--font-family-space_grotesk` | `"Space Grotesk"` | Helvetica | 顯示字型（標題/強調） |

### 1.2 框架遺留字型（非品牌）

| 字型名稱 | 出現檔案 | 用途 | 風險 |
|---------|---------|------|------|
| `"Playfair Display"` | `template-style.css`（Custom 區段） | 所有 h1~h6 heading | ⚠️ 覆蓋品牌字型，衝突 |
| `"Open Sans"` | `responsee.css` | body 預設字型 | ⚠️ 與品牌 Noto Sans 衝突 |
| `"Microsoft JhengHei"` | `style.css` | 工具頁 body | ⚠️ Windows 限定，非跨平台 |
| `"georgia"` | `template-style.css` | blockquote `::before` 引號 | 低風險 |

### 1.3 圖示字型

| 字型名稱 | 出現檔案 | 來源 |
|---------|---------|------|
| `"mfg"` | `icons.css`、`template-style.css` | MFG Labs Icon Set，本地 `../font/` |
| `"sli"` | `template-style.css`（Carousel） | Slidicon / Responsee 圖示字型 |

---

## 二、字型大小（Font Size）

### 2.1 設計系統 Token（`styleguide.css` `:root`）

| 變數名稱 | 值 | 建議語意 |
|---------|-----|---------|
| `--font-size-m` | `18px` | Body / Small UI |
| `--font-size-l` | `20px` | Body / Navigation |
| `--font-size-xl` | `24px` | Sub-heading / Info |
| `--font-size-xxl` | `30px` | Card Title |
| `--font-size-xxxl` | `32px` | Section Sub-title |
| `--font-size-xxxxl` | `36px` | Section Title |
| `--font-size-xxxxxl` | `48px` | Page Hero |

### 2.2 硬編碼字級（未使用 token）

| 值 | 出現檔案 | 對應角色 | 建議 |
|----|---------|---------|------|
| `96px` | `stark_lab_member.css`、`stark_lab_project_linebot.css` | 超大顯示標題（教授名/專案名） | 新增 token `--font-size-display` |
| `60px` | `styleguide.css`（utility class）、`template-style.css` | 顯示字 / text-size-60 | 新增 token `--font-size-hero` |
| `50px` | `template-style.css`（utility class） | text-size-50 | 框架 utility，可保留 |
| `40px` | `stark_lab_member.css`（教授職稱）、`template-style.css` | 顯示副標 | 可用 `--font-size-xxxxxl` 替代（差 8px，待確認） |
| `16.4px` | `stark_lab_professor.css`（ORCID 連結） | 非標準值！ | 應改為 16px 或 18px |
| `22px` | `stark_lab_project_linebot.css`（.text-3-2） | 非標準值！ | 應改為 `--font-size-xl` (24px) |
| `16px` | `style.css`、`stark_lab_project_linebot.css` | 一般 UI、返回按鈕 | 建議新增 `--font-size-s: 16px` |
| `15px` | `style.css`（table cell） | 表格文字 | 接近 16px，可統一 |
| `14px` | `stark_lab_professor.css`（論文年份） | Caption | 建議新增 `--font-size-xs: 14px` |
| `12px` | `style.css`（form input）、`template-style.css` | 最小字級 | 建議新增 `--font-size-xxs: 12px` |

### 2.3 去重後字級清單

**絕對值**（px）：`12, 14, 15, 16, 16.4 ⚠️, 18, 20, 22 ⚠️, 24, 25, 30, 32, 36, 40, 48, 50, 60, 70, 96` → 共 **19 個**

**相對值**（rem）：`0.75, 0.8, 0.85, 0.9, 1.0, 1.1, 1.2, 1.4, 1.8, 2.0, 2.2, 2.4, 2.6, 2.7, 3.0, 3.8rem` → 框架系統 16 個

> ⚠️ 超出驗收標準 12 級上限。`16.4px` 與 `22px` 為非標準值，必須修正。  
> 品牌頁面（非框架）去重後有 12 個有效字級，達標建議見第三節。

---

## 三、字型粗細（Font Weight）

| 值 | 出現檔案 | 角色 |
|----|---------|------|
| `300` | `template-style.css`（`.text-thin`） | 細字（選用） |
| `400` | 全域 | 正文、一般 UI |
| `500` | `styleguide.css`、`stark_lab_home.css`、`stark_lab_member.css` | 中等強調 |
| `600` | `styleguide.css`（Noto Sans TC semi-bold utility class） | 半粗，Noto TC 特有 |
| `700` | 全域 | 標題、重要強調 |
| `800` | `stark_lab_home.css`（hero .pioneering-solutions） | 超粗，頁面英雄標題 |

---

## 四、行高（Line Height）

| 值 | 出現檔案 | 角色 |
|----|---------|------|
| `normal` | 全域（最常見） | 預設行高 |
| `28px` | navbar-link-text 共用 | 導航文字 |
| `35px` | 卡片展開文字（home） | 卡片內文 |
| `40px` | stark_lab_member 教授描述 | 段落行距 |
| `50px` | stark_lab_project_linebot 內文 | 長文段落 |
| `1.4` | template-style utility 文字系列 | 工具類 |
| `1.6` / `1.6rem` | responsee.css、template-style | 段落預設 |
| `1.3rem` | responsee.css（tooltip） | 提示文字 |
| `120px` | linebot hero title | 超大顯示標題 |

---

## 五、Web Font 載入（`globals.css`）

```
Google Fonts URL:
?family=Noto+Sans+TC:500,700,600,400
       |Noto+Sans:500,700,800,400
       |Space+Grotesk:500,400
```

- Noto Sans TC：400、500、600、700（四個粗細）
- Noto Sans：400、500、700、800（四個粗細）
- Space Grotesk：400、500（兩個粗細）
- **本地圖示字型**：`mfg`（mfglabsiconset），位於 `../font/`

> ⚠️ `globals.css` 第 3 行含 AnimaApp 追蹤像素 URL（隱私疑慮），應於 T2 移除。

---

## 六、品牌字型精簡建議（≤ 12 級目標）

| 等級 | Token 建議 | 值 | 角色 |
|------|---------|-----|------|
| D | `--font-size-display` | 96px | 超大顯示（教授名/專案標題） |
| H0 | `--font-size-hero` | 60px | 英雄區塊（暫僅 utility class） |
| H1 | `--font-size-xxxxxl` | 48px | 頁面主標題 |
| H2 | `--font-size-xxxxl` | 36px | 段落標題 |
| H3 | `--font-size-xxxl` | 32px | 子標題 |
| H4 | `--font-size-xxl` | 30px | 卡片標題 |
| H5 | `--font-size-xl` | 24px | 資訊標題 |
| H6 | `--font-size-l` | 20px | 小標題 / Nav |
| Body | `--font-size-m` | 18px | 正文 |
| UI | `--font-size-s` | 16px | UI 元素 / 按鈕 |
| Caption | `--font-size-xs` | 14px | 標籤 / 年份 |
| Micro | `--font-size-xxs` | 12px | 最小文字 |

共 12 個等級，達標。  
**廢棄值**：`15px`（→ 16px）、`16.4px`（→ 16px）、`22px`（→ 24px）、`25px`（→ 24px 或 utility only）、`40px`（→ 36px 或 36px+，待設計確認）、`50px`（保留為 utility class）、`70px`（保留為 utility class）
