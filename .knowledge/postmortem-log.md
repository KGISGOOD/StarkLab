# 踩坑紀錄: StarkLab 官網

> **最後更新**: 2026-05-03
> **總計**: 2 項

---

## 使用說明

1. 每次遇到非預期問題且花費超過 10 分鐘排查，新增一筆紀錄
2. 分類標籤幫助快速定位同類問題
3. 嚴重度決定在 CLAUDE.md 中的曝光優先級
4. 定期回顧，將高頻問題提升為 coding-standards 規範

---

## 紀錄表

| # | 分類 | 問題描述 | 根因 | 影響 | 正確做法 | 嚴重度 |
|---|------|---------|------|------|---------|--------|
| 1 | 環境設定 | 本機跑 `python manage.py runserver` 直接 HTTP 500，log 顯示 `ImproperlyConfigured: The SECRET_KEY setting must not be empty.` | (a) 專案本來就沒有 commit `.env`（正確，安全）；(b) `settings.py` 對 `DJANGO_SECRET_KEY` 給的預設值是 `""` 空字串；(c) 老闆本機目前跑的是 Django 6.0.2（非專案規範的 3.2.3），Django 4+ 對空 SECRET_KEY 直接拒絕啟動 | T4 baseline 截圖任務首次啟動 server 即崩，浪費 ~15 分鐘排查 | (1) 新人 onboarding 需先建立本機 `.env`（含隨機 `DJANGO_SECRET_KEY`，可用 `python -c "import secrets; print('django-insecure-' + secrets.token_urlsafe(50))"` 產出）；(2) `settings.py` 預設值改用會「明確報錯但訊息友善」的策略，例如讀不到時印出「請複製 `.env.example` 到 `.env`」；(3) 在 repo 加 `.env.example` 範本檔（已 .gitignore `.env`，但 example 應該 commit）；(4) tech-lead 應另開任務統一本機 Django 版本（3.2.3 vs 6.0.2 是更深層問題） | 🔴高 |
| 2 | 環境設定 | 截圖腳本第一次跑出來 28 張全部「裸 HTML」（純文字、CSS/img 全 404），無法當 baseline | Django 在 `DEBUG=False` 時**預設不會 serve static files**（`runserver` 把這視為 production 場景，期望由 reverse proxy 處理）。專案實際部署用的是 Caddy + Waitress，所以開發環境本來就沒踩過這條 | 28 張首批截圖完全作廢，需重新跑；若沒人發現直接當 baseline 提交，後續所有 visual regression diff 都會變成「跟空白頁比對」 | 三選一：(a) 暫時改 `DEBUG=True` 跑截圖（最簡單但會引入 debug toolbar 等噪音）；(b) `runserver --insecure` flag 強制 serve static（**本次採用**，零檔案改動，最乾淨）；(c) 用 `whitenoise` middleware 讓 production-like server 也能 serve static（長期方案，但屬重構範圍）。截圖腳本未來應加 sanity check：若 baseline 截圖中 `<img>` 數量 / file size 異常低，自動 fail | 🔴高 |

---

## 分類標籤定義

| 標籤 | 說明 | 常見場景 |
|------|------|---------|
| 環境設定 | 開發/部署環境配置 | Node 版本、Docker、環境變數、系統依賴 |
| 套件相容 | 第三方套件問題 | 版本衝突、API 變更、型別不符 |
| API 設計 | 介面設計不當 | 命名不一致、缺少欄位、狀態碼錯誤 |
| 資料庫 | Schema/Migration/查詢 | Migration 順序、欄位型別、N+1 查詢 |
| 部署流程 | CI/CD/Docker | Build 失敗、環境變數遺漏、權限問題 |
| 前端 | UI/CSS/狀態管理 | 樣式衝突、響應式問題、狀態同步 |
| 安全 | 認證/授權/資料保護 | Token 處理、CORS、密鑰洩漏 |
| 測試 | 測試撰寫/環境 | Mock 不準、環境隔離、非確定性測試 |
| Git | 版控操作 | 合併衝突、分支策略、hook 問題 |

---

## 統計

| 分類 | 數量 | 最近一次 |
|------|------|---------|
| 環境設定 | 2 | 2026-05-03 |
| 套件相容 | 0 | — |
| API 設計 | 0 | — |
| 部署流程 | 0 | — |
| 其他 | 0 | — |

---

## 跨議題備忘

- **Django 版本對齊**：CLAUDE.md 規定 Django 3.2.3，但 design-director 本機跑 6.0.2 才會踩到坑 #1 的「空 SECRET_KEY 直接拒啟」行為。Django 3.2 對空字串較寬容（仍會啟動但給警告）。建議 tech-lead 在 Sprint 1 後端任務中把「本機環境鎖版」列入（pin requirements.txt 並提供 venv 建立指引）。
- **Visual baseline 凍結策略**：本次刻意把現有 mobile 破版納入 baseline（內容溢出視窗）。理由：T2 重構目標是「外觀不變、結構乾淨」，破版是現況事實，不該在 baseline 階段偷偷修。修破版另列任務由 ui-designer + ux-researcher 處理。
