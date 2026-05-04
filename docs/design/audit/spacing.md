# 間距 / 圓角 / 陰影盤點表

> **產出時間**: 2026-05-03  
> **盤點範圍**: `labweb/lab/mylab/static/css/` 全部 14 個 CSS 檔  
> **執行者**: brand-guardian（T1）

---

## 一、Padding（內距）

### 1.1 頁面水平邊距（Page Horizontal Padding）

| 值 | 出現檔案 | 出現 selector | 頻率 |
|----|---------|-------------|------|
| `100px` | `stark_lab_home.css`、`stark_lab_member.css`、`stark_lab_professor.css`、`stark_lab_project.css`、`stark_lab_project_linebot.css` | `.navigation-bar`、`.project`、`.overlap-group6`/8 | ★★★★★ 最常見，應為**標準頁面水平邊距** |
| `83px` | `stark_lab_project_linebot.css` | `.frame-27` padding | 接近 100px，非標準值 |
| `60px` | `stark_lab_home.css`（card padding）、`globals.css`（footer） | `.card`、`.footer` | ★★★ 常見 |
| `40px` | `stark_lab_project.css`（card padding） | `.overlap-group5/4/6/8` | ★★★ |

### 1.2 元件 Padding

| 值 | 出現檔案 | 角色 |
|----|---------|------|
| `41px 60px` | `stark_lab_home.css`（card） | 卡片 padding |
| `34.8px 47.8px` | `stark_lab_member.css`（group card） | 成員卡片（非標準小數） |
| `105px 66px` | `stark_lab_member.css`（group-14） | 教授展示區 |
| `99.4px 66px` | `stark_lab_project_linebot.css` | 英雄卡片（非標準小數） |
| `40px` | `stark_lab_project.css`（section/card） | 標準 section padding |
| `20px` | `style.css`（body）、`stark_lab_project_linebot.css` | 一般間距 |
| `25px` | `style.css`（card-container） | card 內距 |
| `15px / 10px` | `stark_lab_professor.css`（section tag） | Badge 內距 |
| `6px 3px` | `stark_lab_home.css`（group-33） | 圖示組合 |
| `0px 7px` | `stark_lab_member.css`（label） | 小標籤 |

---

## 二、Margin（外距）

### 2.1 頁面頂部間距（垂直節奏）

| 值 | 出現檔案 | selector |
|----|---------|---------|
| `60px` margin-top | `stark_lab_home.css`、`stark_lab_member.css`、`stark_lab_professor.css`、`stark_lab_project_linebot.css` | 導覽列頂部 | ★★★★ 全站一致 |
| `70px` margin-top | `stark_lab_member.css` | 教授卡片頂距 |
| `80px` margin-top | `stark_lab_project.css`（footer）、`stark_lab_member.css` | Footer 頂距 |
| `92px` / `94px` margin-top | `stark_lab_home.css` | 專案區塊頂距（非標準） |
| `250px` margin-top | `stark_lab_member.css`（group-17） | 特殊按鈕定位（應改為 Flexbox） |
| `500px` margin-top | `stark_lab_home.css`（process-block） | 大量留白（絕對定位遺留問題） |

### 2.2 template-style.css margin utility（大量 !important）

工具類間距：`0, 10, 15, 20, 30, 40, 50, 60, 70, 80px`（margin-top/bottom/left/right）  
→ 共約 **400+ 行**的 margin utility classes（含響應式前綴 `-m-` 和 `-s-`）

---

## 三、Gap（彈性/格狀間距）

| 值 | 出現檔案 | 角色 |
|----|---------|------|
| `10px` | `stark_lab_home.css`（card gap） | 緊密元素 |
| `16px` | `stark_lab_project.css`（footer info） | 標準小間距 |
| `17px` | `stark_lab_home.css`（group-33） | 圖示+文字 |
| `19px` | `stark_lab_home.css`（group-52） | 專案卡片行 |
| `20px` | `stark_lab_member.css`（info/label） | 標準間距 |
| `22px` | `stark_lab_project_linebot.css` | 列表項目 |
| `23px` | `stark_lab_member.css`（content） | 成員資訊 |
| `24px` | `stark_lab_project.css`（flex-col） | 卡片內容 |
| `25px` | `stark_lab_home.css`（label） | 標籤元素 |
| `27px` | `globals.css`（contact-us） | 聯絡資訊 |
| `28px` | `stark_lab_member.css` | 人員資訊 |
| `35px` | `stark_lab_home.css`（frame-13） | 英雄區域 |
| `40px` | `stark_lab_home.css`（navbar）、`stark_lab_project.css` | 導覽連結 |
| `45px` | `stark_lab_project_linebot.css` | 內容區塊 |
| `50px` | `stark_lab_member.css`（container） | 成員卡片 grid |
| `63px` | `stark_lab_home.css` | 英雄橫向排版 |
| `66px` | `stark_lab_member.css`（frame-26） | 導覽+聯絡區 |
| `70px` | `stark_lab_home.css`（header gap） | 英雄區塊 |
| `71px` | `stark_lab_home.css`（overlap-group2） | 接近 70px，非標準 |
| `99px` | `stark_lab_member.css`（flex-col-1） | 非標準，疑為設計稿直接輸出 |
| `120px` | `stark_lab_member.css`（frame-26） | 頁尾導覽大間距 |
| `186px` | `stark_lab_project_linebot.css` | 英雄內容分欄 |

> ⚠️ gap 值高度碎片化（共 22 個不同值），應收斂為 spacing scale。

---

## 四、Border Radius（圓角）

| 值 | 出現檔案 | 角色 | 頻率 |
|----|---------|------|------|
| `3px` | `template-style.css`（image, border-radius utility） | 圖片、小元素 | ★ |
| `7px` | `stark_lab_member.css`、`stark_lab_professor.css`、`stark_lab_project_linebot.css`（label） | 標籤徽章 | ★★★ |
| `8px` | `stark_lab_project.css`（card image, card） | 卡片圖片 | ★★ |
| `8.3px` | `stark_lab_project_linebot.css`（返回按鈕） | 非標準，應為 8px | ★ |
| `9px` | `stark_lab_professor.css`、`stark_lab_project_linebot.css`（section badge） | 標題 Badge | ★★★ |
| `10px` | `style.css`（card-container）、`stark_lab_member.css` | 卡片容器 | ★★ |
| `12px` | `stark_lab_project_linebot.css`（.group-31） | 小圓角 | ★ |
| `12.41px` | `stark_lab_project_linebot.css`（.group-31 背景） | 非標準小數，應為 12px | ★ |
| `16px` | `stark_lab_project.css`（project card） | 現代卡片 | ★★★ |
| `17px` | `stark_lab_member.css`（social-icon） | 社群圖示 | ★ |
| `20.5px` | `stark_lab_project_linebot.css`（icon-1, icon） | 圓形圖示 | ★★ |
| `21px` | `stark_lab_home.css`（overlap-group, overlap-group1） | 方形圖示容器 | ★★ |
| `41px` | `stark_lab_project_linebot.css`（overlap-group2） | 資訊方塊 | ★ |
| `45px` | `globals.css`（.footer） | 頁尾圓角 | ★ |
| `57px` | `stark_lab_home.css`（overlap-group3, overlap-group2） | 專案卡片 | ★★ |
| `60px` | `template-style.css`（.i.icon-circle-small） | 圓形圖示 | ★ |
| `65px` | `stark_lab_member.css`、`stark_lab_project_linebot.css` | 大型成員/英雄卡片 | ★★★ |
| `100px` | `template-style.css`（.i.icon-circle） | 大圓形圖示 | ★ |
| `50%` / `9999px` | `template-style.css`（.button.rounded-full-btn）、`stark_lab_project.css`（button circle） | 完全圓形 | ★★ |

> ⚠️ 共 **19 個**不同圓角值，碎片化嚴重。  
> 非標準小數（`8.3px`、`12.41px`、`20.5px`）來自 Figma 精確導出，應取整。

### 圓角收斂建議

| Token | 值 | 含蓋現有值 |
|------|-----|---------|
| `--radius-xs` | `4px` | 3px |
| `--radius-sm` | `8px` | 7px、8px、8.3px |
| `--radius-md` | `12px` | 9px、10px、12px、12.41px |
| `--radius-lg` | `16px` | 16px、17px |
| `--radius-xl` | `20px` | 20.5px、21px |
| `--radius-2xl` | `45px` | 41px、45px |
| `--radius-3xl` | `65px` | 57px、60px、65px |
| `--radius-full` | `9999px` | 100px、50% |

---

## 五、Box Shadow（陰影）

| 值 | 出現檔案 | 角色 | 特點 |
|----|---------|------|------|
| `0px 5px 0px #000000` | `stark_lab_member.css`、`stark_lab_project_linebot.css` | 卡片底部實心陰影 | **品牌特徵陰影** |
| `0px 5px 0px #191a23` | `stark_lab_home.css`（.card, .card-1） | 卡片底部實心陰影（home） | 與 #000 同類，color 略不同 |
| `0px 7px 0px #000000` | `stark_lab_home.css`（project cards） | 更深陰影 | hover 變形 |
| `0px 7px 0px #191a23` | `stark_lab_home.css`（.card:hover） | Hover 加深陰影 | |
| `0 4px 12px rgba(0,0,0,0.1)` | `style.css`（.card-container）、`.result` | 柔和陰影 | 工具頁 |
| `0 1px 4px rgba(0,0,0,0.06)` | `style.css`（filter select） | 極淺陰影 | |
| `0 0 100px 100px rgba(255,255,255,0.25) inset` | `template-style.css`（button hover） | 按鈕 hover 光暈 | 框架效果 |
| `0 0 10px 100px rgba(255,255,255,0.15) inset` | `components.css`（button hover） | 按鈕 hover 光暈 | 框架效果 |

> **品牌特徵陰影識別**：`0px 5px 0px` 實心陰影（solid shadow）是 StarkLab 的視覺特徵，出現在卡片、按鈕等主要元件上。  
> 建議定義為 `--shadow-brand: 0px 5px 0px var(--color-black)`。

---

## 六、固定寬度 / 頁面寬度

| 值 | 出現次數 | 角色 |
|----|---------|------|
| `1440px` | 大量 | 頁面最大寬度（設計稿基準） |
| `1378px` | 4+ | 頁尾容器寬度 |
| `1339px` | 3+ | 成員頁主內容 |
| `1279px` / `1278px` | 2 | 專案卡片容器 |
| `1242px` / `1240px` | 3 | 內容框（含 margin 100px\*2） |
| `1234px` | 3 | Home 卡片寬度 |
| `900px` | 2 | style.css 工具頁容器 |

> ⚠️ 所有頁面均使用固定寬度 `1440px`，**完全無響應式設計**。  
> 這是 Sprint 1 Phase 3 重構的核心問題，T2 需規劃 RWD 策略。
