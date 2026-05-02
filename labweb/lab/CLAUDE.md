# StarkLab 專案設定檔（Claude Code 專用）

## 🔹 語言規則

- 所有回覆必須使用「繁體中文」。
- 技術專有名詞保留英文（例如 Django、ORM、service layer、middleware、migration、LINE Bot API）。
- 回答應使用條列式結構，清楚分段。
- 若涉及風險評估，請標示：Low / Medium / High。

---

## 🔹 專案技術背景

- Django 版本：3.2.3（嚴禁使用 Django 4 或 5 才有的語法）
- Python：3.10
- 作業系統：Windows 開發、 Windows  部署
- 資料庫：SQLite（w.db）
- Web server：Waitress
- Reverse proxy：Caddy
- 使用 LINE Bot API、Grok (X.AI)、Gemini API
- 有 Selenium + BeautifulSoup 爬蟲流程
- 有 Windows Scheduled Task 依賴固定檔案路徑

---

## 🔹 架構原則

- 不得建議 async view（除非明確要求）。
- 所有重構建議應優先考慮低風險（Low-risk first）。
- 不得自動修改檔案，除非使用者明確要求。
- 所有檔案搬移建議必須列出 file-level change 清單。

---

## 🔹 安全規則（高優先）

- 不得將 API key 或 SECRET_KEY 硬寫於原始碼。
- 必須建議使用環境變數（os.getenv）。
- 若發現硬編碼憑證，請標示為 CRITICAL。
- 若 ALLOWED_HOSTS = ["*"]，請標示為 HIGH。
- 若 @csrf_exempt 出現在公開 endpoint，請標示為 HIGH。

---

## 🔹 回答格式範本

當分析架構時，請使用以下格式：

1️⃣ 專案結構摘要  
2️⃣ 主要架構問題（依風險排序）  
3️⃣ 建議修正步驟（分階段）  
4️⃣ 風險評估  

---

## 🔹 特殊注意事項

- 專案包含排程任務，請避免破壞既有檔案路徑。
- 相對路徑存取檔案（例如 'chat_records.csv'）請標示為部署風險。

---

## 🔹 預設行為

- 若使用者未明確要求修改，僅提供分析與規劃。
- 若需改動，必須先顯示 diff-level 計畫。
- 回答應偏向「架構顧問」而非「自動程式重寫」。

---

## 🔹 回答風格

- 偏工程顧問風格。
- 不要過度冗長。
- 結論先說。
- 條列清晰。