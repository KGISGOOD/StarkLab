# StarkLab 視覺基準截圖 — 操作手冊

> **目的**：用截圖作為 CSS 重構的外觀一致性驗收基準。  
> 重構目標：外觀不變、結構變乾淨。視覺 diff < 1% 即視為通過。

---

## 目錄結構

```
docs/design/
├── README.md            ← 本文件
├── baseline/            ← 重構【前】的基準截圖（不得覆蓋，需重建時先備份）
│   ├── desktop/         ← 1440×900，每頁一張全頁 PNG
│   └── mobile/          ← 375×812，每頁一張全頁 PNG
├── current/             ← 重構【後】的截圖（每次重構後重新產出）
│   ├── desktop/
│   └── mobile/
└── diff/                ← 像素差異高亮圖（由 visual-diff.js 自動產出）
    ├── desktop/
    └── mobile/

diff-report.html         ← 視覺比對報告（開瀏覽器直接看）
```

---

## 環境準備（第一次）

### 1. 安裝 Node.js 依賴

```bash
# 在專案根目錄（StarkLab/）
npm install
```

### 2. 安裝 Playwright 瀏覽器

```bash
npx playwright install chromium
```

> 只需安裝 chromium 即可，不需要 firefox / webkit。

---

## 啟動 Django Dev Server

截圖腳本需要 server 在 `http://127.0.0.1:8000` 運行。

```bash
# 進入 Django 專案目錄
cd labweb/lab

# 啟動（Windows）
python manage.py runserver 127.0.0.1:8000
```

> **注意**：`settings.py` 中 `DEBUG = False`，截圖內容將與 production 視覺一致。  
> 若靜態檔案無法載入，請先執行 `python manage.py collectstatic --noinput`。

---

## 產出 Baseline 截圖（重構前，只做一次）

```bash
# 在專案根目錄，確保 Django server 已啟動
npm run screenshot:baseline
```

輸出位置：`docs/design/baseline/desktop/*.png` 和 `docs/design/baseline/mobile/*.png`

共 **14 頁 × 2 viewport = 28 張**截圖。

| 頁面 | URL | 檔名 |
|------|-----|------|
| 首頁 | `/` | `home.png` |
| 成員 | `/member/` | `member.png` |
| 教授 | `/professor/` | `professor.png` |
| 專案列表 | `/project/` | `project.png` |
| LineBot 專案 | `/project_linebot/` | `project_linebot.png` |
| 股票專案 | `/project_stock/` | `project_stock.png` |
| WRA 專案 | `/project_wra/` | `project_wra.png` |
| WRA 報告 | `/project_wra_repoet/` | `project_wra_repoet.png` |
| ETFbot 專案 | `/project_ETFbot/` | `project_etfbot.png` |
| 基金優化 | `/project_financial/` | `project_financial.png` |
| 基金教學 1 | `/financial_1/` | `financial_1.png` |
| 基金教學 2 | `/financial_2/` | `financial_2.png` |
| 基金教學 3 | `/financial_3/` | `financial_3.png` |
| 翻譯頁 | `/trans/` | `trans.png` |

---

## 重構後產出 Current 截圖

```bash
# CSS 重構完成後，在 Django server 運行的情況下執行
npm run screenshot:current
```

輸出位置：`docs/design/current/desktop/*.png` 和 `docs/design/current/mobile/*.png`

---

## 執行視覺回歸比對

```bash
npm run diff
```

完成後開啟瀏覽器查看報告：

```bash
# Windows
start docs/design/diff-report.html

# 或直接雙擊 docs/design/diff-report.html
```

### 報告說明

| 顏色 | 意義 |
|------|------|
| 🟢 綠色 | 差異 ≤ 1%，視覺一致，通過 |
| 🔴 紅色 | 差異 > 1%，需人工確認 |
| 🟠 橙色 | current 截圖缺失（尚未執行 current 模式） |

Diff 欄位顯示差異像素高亮圖，紅色像素為發生變化的區域。

---

## 驗證腳本正確性（自我比對）

用 baseline 對比 baseline 自己，差異應為 0%：

```bash
# 複製 baseline 到 current
xcopy docs\design\baseline docs\design\current /E /I /Y

# 執行比對（應全部 0%）
npm run diff
```

---

## Baseline 何時應該重新產生

> **規則**：每次刻意改動 UI 外觀後，需重新產生 baseline。

✅ 應更新 baseline 的情況：
- 設計師確認新設計已定稿
- PM 批准的 UI 改版（非重構）
- 新增頁面後

❌ 不應更新 baseline 的情況：
- CSS 重構進行中（這正是要驗收的對象）
- 僅改後端邏輯、無 UI 變動
- 尚未取得 PM 確認

更新步驟：
```bash
# 1. 備份舊 baseline（建議）
xcopy docs\design\baseline docs\design\baseline-backup-YYYYMMDD /E /I /Y

# 2. 重新產出
npm run screenshot:baseline
```

---

## 特殊頁面說明

| 頁面 | 注意事項 |
|------|---------|
| `/project_wra_repoet/` | URL 有 typo（repoet 非 report），路由照實際設定，無需修改 |
| `/project_wra/` | 可能依賴爬蟲資料，若出現空白，需確認 DB 是否有 fixture 資料 |
| 首頁 | 有摺疊卡片互動，腳本已加 500ms 等待，確保展開狀態正確截到 |

---

## 常見問題排除

**Q: 截圖全白或 CSS 不載入**  
A: 執行 `python manage.py collectstatic --noinput` 後重試。

**Q: 某頁面 timeout**  
A: 該頁可能有外部 API 請求。檢查 Django log，或在 `baseline-screenshots.js` 的 `WAIT_UNTIL` 改為 `'domcontentloaded'`。

**Q: diff-report.html 打開空白**  
A: 確認 `docs/design/baseline/` 和 `docs/design/current/` 兩個目錄均有截圖。

**Q: pixelmatch 報錯 `width/height mismatch`**  
A: `visual-diff.js` 已自動對齊兩張圖的尺寸（補白），正常不應發生。若仍出錯，檢查截圖是否損壞。
