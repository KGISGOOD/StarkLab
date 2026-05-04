# Web App 架構參考

> PM 參考此文件，根據專案需求調整後放入 `{workDir}/.knowledge/`

---

## 前端架構

### 推薦模式

- **元件化**: 頁面由可重用的元件組成
- **狀態管理**: 集中管理應用狀態（Pinia / Redux / Zustand）
- **路由**: 前端路由控制頁面切換
- **API 層**: 獨立的 API 呼叫層，統一處理請求/錯誤

### 目錄建議

```
src/
├── components/          # 共用元件
│   ├── common/          # 基礎元件（Button, Input, Modal）
│   └── {domain}/        # 業務元件（UserCard, OrderList）
├── views/               # 頁面（對應路由）
├── stores/              # 狀態管理
├── composables/         # 共用邏輯 (Vue) / hooks (React)
├── services/            # API 呼叫層
├── utils/               # 工具函數
├── types/               # 型別定義
└── router/              # 路由設定
```

## 後端架構（如有）

### 推薦模式

- **分層**: Controller → Service → Repository
- **中介層**: 認證、錯誤處理、日誌
- **資料庫**: ORM / Query Builder

### 目錄建議

```
server/
├── routes/              # 路由定義
├── controllers/         # 請求處理
├── services/            # 業務邏輯
├── models/              # 資料模型
├── middleware/           # 中介層
└── utils/               # 工具
```

## 資料庫設計原則

- 表名: snake_case, 複數形式
- 主鍵: `id`
- 外鍵: `{table}_id`
- 時間欄位: `created_at`, `updated_at`
- 布林欄位: `is_` 或 `has_` 前綴
- 使用 migration 管理 schema 變更

## 測試策略

| 層級 | 工具建議 | 覆蓋目標 |
|------|---------|---------|
| 單元測試 | Vitest / Jest | 核心邏輯 >= 80% |
| 元件測試 | @vue/test-utils / React Testing Library | 關鍵元件 |
| E2E 測試 | Playwright / Cypress | 核心用戶流程 |

## 部署

- 開發: 本地開發伺服器（Vite dev server）
- 測試: Docker Compose 或 CI 環境
- 正式: 靜態檔 CDN + API 伺服器，或 SSR 部署
