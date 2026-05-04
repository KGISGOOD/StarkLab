# 元件 API 規格書

> **文件狀態**: 計畫草案（待老闆批准後方可實作）
> **產出者**: frontend-engineer（T2）
> **產出日期**: 2026-05-02
> **說明**: 本文件定義重構後各共用元件的 HTML 結構、variant、狀態。實作時依本文件為準，不得自行添加未列出的 class 或屬性。

---

## 元件總覽

| # | 元件 | 目標 CSS 檔 | 用途 |
|---|------|------------|------|
| 1 | Navbar | `components/navbar.css` | 全站頂部導覽列 |
| 2 | Card | `components/card.css` | 首頁與專案展示卡片 |
| 3 | Button | `components/button.css` | 全站按鈕（含 clickable-text） |
| 4 | Footer | `components/footer.css` | 全站底部頁尾 |
| 5 | Badge | `components/badge.css` | 標籤、標題徽章、成員標籤 |
| 6 | Photo Gallery | `components/photo-gallery.css` | 專案頁面相片展示 |
| 7 | Modal / Tab | `components/modal.css` | 彈窗層與分頁面板 |
| 8 | Clickable Text | `components/button.css`（modifier） | 可點擊純文字連結樣式 |

---

## 1. Navbar

### 用途

全站頂部水平導覽列，固定高度 60px margin-top，頁面水平邊距 100px。來源：`stark_lab_home.css`（`.navigation-bar`）+ `template-style.css`（`nav`）。

### HTML 結構範例（Django template 語法）

```html
{% load static %}
<nav class="navigation-bar">
  <div class="nav-logo">
    <a href="{% url 'home' %}">
      <img src="{% static 'images/logo.png' %}" alt="StarkLab" class="nav-logo-img">
    </a>
  </div>
  <ul class="nav-links">
    <li class="nav-item">
      <a href="{% url 'home' %}" class="nav-link {% if active_page == 'home' %}nav-link--active{% endif %}">
        Home
      </a>
    </li>
    <li class="nav-item">
      <a href="{% url 'member' %}" class="nav-link {% if active_page == 'member' %}nav-link--active{% endif %}">
        Members
      </a>
    </li>
    <li class="nav-item">
      <a href="{% url 'project' %}" class="nav-link {% if active_page == 'project' %}nav-link--active{% endif %}">
        Projects
      </a>
    </li>
  </ul>
</nav>
```

### Variants

| Variant class | 說明 |
|--------------|------|
| （預設，無額外 class） | 標準白底導覽列 |
| `.navigation-bar--transparent` | 透明背景（用於英雄圖上方，待設計稿確認） |

### 狀態

| 狀態 | Class / 說明 |
|------|-------------|
| 預設 | 無額外 class |
| 當前頁面 | `.nav-link--active`（字色改為 `var(--color-brand-primary)`） |
| Hover | CSS `:hover` 偽類，底線或顏色變化 |

> **保護提醒**：`nav` 的 `border-bottom` 衝突（衝突 5）已於 `base.css` 覆蓋層修正，`navigation-bar` class 不改名。

---

## 2. Card

### 用途

首頁主要展示卡片，含品牌特徵陰影（`0px 5px 0px var(--color-black)`）。支援展開/收合互動（`.expanded`）。來源：`stark_lab_home.css`（`.card`、`.card-1`、`.card.expanded`）。

### HTML 結構範例（Django template 語法）

```html
{% load static %}
<!-- Default Card -->
<div class="card" data-card-id="{{ project.id }}">
  <div class="card-header">
    <img src="{% static project.icon_path %}" alt="{{ project.title }}" class="card-icon">
    <h3 class="card-title">{{ project.title }}</h3>
  </div>
  <div class="card-body">
    <p class="card-description">{{ project.description }}</p>
  </div>
  <button class="card-expand-btn button" aria-expanded="false">
    了解更多
  </button>
  <!-- 展開後顯示的額外內容 -->
  <div class="card-expand-content">
    <p>{{ project.detail }}</p>
  </div>
</div>

<!-- Dark Card (expanded state, triggered by JS) -->
<div class="card card--dark expanded" data-card-id="{{ project.id }}">
  <!-- 同上結構，JS 操作 .expanded class -->
</div>
```

### Variants

| Variant class | 說明 | 來源 |
|--------------|------|------|
| `.card`（預設） | 淺灰背景（`var(--color-gray-50)`）+ 品牌 solid shadow | `.card` |
| `.card.card--dark` | 品牌主色背景（`var(--color-brand-primary)`）+ 白色文字 | 參考 `.card.expanded` 的 navy-blue 背景 |
| `.card.expanded` | JS 動態加入（展開狀態），高度動畫、深色背景 | **禁止改名**（JS 依賴） |

### 狀態

| 狀態 | 說明 |
|------|------|
| 預設（collapsed） | 固定高度、淺灰背景、底部 5px solid shadow |
| Hover | shadow 加深為 `var(--shadow-brand-md)`（`0px 7px 0px`） |
| Expanded（`.expanded`） | JS 加入此 class；高度展開動畫；背景切換為品牌藍；白色文字 |
| Focus | 鍵盤 `:focus-visible`，outline 使用 `var(--color-brand-primary)` |

> **JS 保護**：`.expanded` class 由 `stark_lab_home.html` 中的 JavaScript `classList.add/remove` 操作，**禁止在重構中改名或移除**。

---

## 3. Button

### 用途

全站按鈕，合併 `components.css` 與 `template-style.css` 的三層 `.button` 定義（衝突 4），統一為單一規格。同時包含 `.clickable-text`（文字連結樣式，從 `stark_lab_project_linebot.css` 遷入）。

### HTML 結構範例（Django template 語法）

```html
{% load static %}

<!-- Primary Button -->
<button class="button button--primary" type="button">
  送出
</button>

<!-- Secondary Button -->
<button class="button button--secondary" type="button">
  取消
</button>

<!-- Icon + Text Button -->
<button class="button button--primary" type="button">
  <i class="icon-mfg"></i>
  <span>下載報告</span>
</button>

<!-- Link styled as button -->
<a href="{% url 'project' %}" class="button button--outline">
  查看專案
</a>

<!-- Clickable Text (link style, no button frame) -->
<a href="{{ url }}" class="clickable-text">返回列表</a>

<!-- Disabled Button (submit) -->
<button class="button button--primary" type="submit" disabled>
  處理中...
</button>
```

### Variants

| Variant class | 背景色 | 文字色 | Border | 說明 |
|--------------|--------|--------|--------|------|
| `.button--primary` | `var(--color-brand-primary)` | `var(--color-white)` | 無 | 主要 CTA |
| `.button--secondary` | `var(--color-gray-200)` | `var(--color-gray-700)` | 無 | 次要動作 |
| `.button--outline` | 透明 | `var(--color-brand-primary)` | 1px brand-primary | 線框按鈕 |
| `.button--danger` | `var(--color-error)` | `var(--color-white)` | 無 | 危險操作（Cancel） |
| `.button.rounded-full-btn` | 繼承 | 繼承 | 無 | 圓角全圓（`var(--radius-full)`）；來自 `template-style.css`，保留 class 名 |
| `.clickable-text` | 無 | `var(--color-brand-primary)` | 無 | 純文字連結樣式 |

### 狀態

| 狀態 | 說明 |
|------|------|
| 預設 | 標準外觀 |
| Hover | 背景稍暗或 `inset box-shadow` 光暈效果 |
| Active（`:active`） | 按下時背景加深 |
| Disabled | `opacity: 0.2`（保留 `!important`，來自 `components.css`）；`cursor: not-allowed` |
| Loading | 建議加 `.button--loading` modifier，顯示 spinner icon（視設計稿確認） |

---

## 4. Footer

### 用途

全站底部頁尾，含聯絡資訊、社群連結、版權文字。來源：`globals.css`（`.footer`）。圓角 `45px` 對應 `var(--radius-2xl)`。

### HTML 結構範例（Django template 語法）

```html
{% load static %}
<footer class="footer">
  <div class="footer-inner">
    <div class="footer-logo">
      <img src="{% static 'images/logo-white.png' %}" alt="StarkLab" class="footer-logo-img">
    </div>
    <div class="footer-contact">
      <p class="footer-address">{{ lab.address }}</p>
      <a href="mailto:{{ lab.email }}" class="footer-email">{{ lab.email }}</a>
    </div>
    <nav class="footer-nav" aria-label="Footer navigation">
      <ul>
        {% for item in footer_nav_items %}
        <li>
          <a href="{{ item.url }}" class="footer-nav-link">{{ item.label }}</a>
        </li>
        {% endfor %}
      </ul>
    </nav>
    <div class="footer-social">
      {% for social in lab.social_links %}
      <a href="{{ social.url }}" class="footer-social-link" target="_blank" rel="noopener noreferrer"
         aria-label="{{ social.platform }}">
        <i class="icon-{{ social.icon_class }}"></i>
      </a>
      {% endfor %}
    </div>
  </div>
  <p class="footer-copyright">
    &copy; {{ current_year }} StarkLab. All rights reserved.
  </p>
</footer>
```

### Variants

| Variant class | 說明 |
|--------------|------|
| `.footer`（預設） | 深色背景（`var(--color-brand-shadow)` 或 `var(--color-gray-900)`）、白色文字、`var(--radius-2xl)` 圓角 |

### 狀態

| 狀態 | 說明 |
|------|------|
| 預設 | 靜態，無互動 |
| Footer link hover | 連結 hover 時文字色改為 `var(--color-brand-primary)` |

---

## 5. Badge / Tag

### 用途

頁面標題旁的裝飾性標籤（section badge）、成員技術標籤（label）、教授頁專長標籤（section tag）。來源：`stark_lab_professor.css`、`stark_lab_member.css`、`stark_lab_project_linebot.css`。

### HTML 結構範例（Django template 語法）

```html
{% load static %}

<!-- Section Badge（頁面標題旁）-->
<div class="badge badge--section">
  <span class="badge-text">{{ section_label }}</span>
</div>

<!-- Skill Tag（成員技術標籤）-->
<span class="badge badge--skill">{{ skill }}</span>

<!-- Status Badge（狀態）-->
<span class="badge badge--status badge--status-{{ status }}">{{ status_label }}</span>

<!-- Django loop 用法 -->
<div class="badge-group">
  {% for skill in member.skills %}
  <span class="badge badge--skill">{{ skill }}</span>
  {% endfor %}
</div>
```

### Variants

| Variant class | 圓角 | 說明 |
|--------------|------|------|
| `.badge--section` | `var(--radius-md)` → 12px | 標題旁裝飾徽章（原 9px 取整） |
| `.badge--skill` | `var(--radius-sm)` → 8px | 成員/教授技術標籤（原 7px 取整） |
| `.badge--status` | `var(--radius-sm)` | 狀態標籤 |
| `.badge--status-active` | 繼承 | 綠色（`var(--color-success)`） |
| `.badge--status-warning` | 繼承 | 橘色（`var(--color-warning)`） |

### 狀態

| 狀態 | 說明 |
|------|------|
| 預設 | 靜態展示 |
| Hover（部分 badge） | 若為可點擊 badge，加 `cursor: pointer`；顏色加深 |
| Disabled | 降低 `opacity: 0.5` |

---

## 6. Photo Gallery

### 用途

專案頁面（`project`、`project_war`）相片展示區，hover 時圖片放大。來源：`stark_lab_project3.css`（第 432–460 行）+ `stark_lab_project_war.css`（第 531–559 行）— 兩份完全相同（衝突 7），提取為共用元件。

### HTML 結構範例（Django template 語法）

```html
{% load static %}
<section class="photo-section">
  <div class="photo-container">
    {% for photo in project.photos %}
    <figure class="photo">
      <img src="{% static photo.path %}" alt="{{ photo.alt }}" loading="lazy">
      <figcaption class="caption">{{ photo.caption }}</figcaption>
    </figure>
    {% endfor %}
  </div>
</section>
```

### Variants

| Variant class | 說明 |
|--------------|------|
| `.photo-container`（預設） | Grid 或 flex 排列相片 |
| `.photo-section` | 包裹整個相片區塊，含 section padding |

### 狀態

| 狀態 | 說明 |
|------|------|
| 預設 | 圖片正常顯示 |
| Hover（`.photo:hover`） | 圖片 zoom 放大，`var(--transition-slow)`（`0.5s cubic-bezier`） |

---

## 7. Modal / Tab

### 用途

資訊彈窗與分頁面板。來源：`components.css`（Tab 背景 `#262626`、Reload/Cancel 按鈕）。

### HTML 結構範例（Django template 語法）

```html
{% load static %}

<!-- Modal Overlay -->
<div class="modal-overlay" id="modal-{{ modal_id }}" hidden>
  <div class="modal" role="dialog" aria-modal="true" aria-labelledby="modal-title-{{ modal_id }}">
    <header class="modal-header">
      <h2 class="modal-title" id="modal-title-{{ modal_id }}">{{ modal.title }}</h2>
      <button class="modal-close button button--secondary" type="button" aria-label="關閉">
        &times;
      </button>
    </header>
    <div class="modal-body">
      {{ modal.content }}
    </div>
    <footer class="modal-footer">
      <button class="button button--primary" type="button">確認</button>
      <button class="button button--secondary modal-close" type="button">取消</button>
    </footer>
  </div>
</div>

<!-- Tab Panel -->
<div class="tab-container">
  <ul class="tab-list" role="tablist">
    {% for tab in tabs %}
    <li role="presentation">
      <button class="tab-btn {% if forloop.first %}tab-btn--active{% endif %}"
              role="tab"
              data-tab-target="#tab-panel-{{ forloop.counter }}"
              aria-selected="{% if forloop.first %}true{% else %}false{% endif %}">
        {{ tab.label }}
      </button>
    </li>
    {% endfor %}
  </ul>
  {% for tab in tabs %}
  <div class="tab-panel {% if forloop.first %}tab-panel--active{% endif %}"
       id="tab-panel-{{ forloop.counter }}"
       role="tabpanel">
    {{ tab.content }}
  </div>
  {% endfor %}
</div>
```

### Variants

| Variant class | 說明 |
|--------------|------|
| `.modal-overlay`（預設） | 全螢幕半透明遮罩，`z-index: var(--z-index-overlay)` |
| `.modal` | 內容容器，白色背景，`var(--radius-lg)` 圓角 |
| `.tab-container` | 分頁容器 |
| `.tab-btn--active` | 當前選中的 tab |
| `.tab-panel--active` | 顯示中的內容面板 |

### 狀態

| 狀態 | 說明 |
|------|------|
| 隱藏（預設） | Modal 使用 `hidden` 屬性或 `display: none` |
| 開啟 | JS 移除 `hidden`；overlay `z-index: var(--z-index-overlay)` |
| Tab 預設 | 第一個 tab active |
| Tab hover | tab-btn `:hover`，背景微變 |
| Tab active | `.tab-btn--active`，底線或背景標示選中 |
| Tab disabled | `aria-disabled="true"`，`opacity: 0.5` |

---

## 設計 Token 快速參照

> 以下為元件實作時常用的 token，完整清單見 `tokens.css`：

```css
/* 顏色 */
var(--color-brand-primary)   /* #0f87e0 品牌主色 */
var(--color-brand-shadow)    /* #191a23 品牌陰影色 */
var(--color-gray-50)         /* #f3f3f3 淺灰背景 */
var(--color-text-body)       /* #363636 正文文字 */
var(--color-white)           /* #ffffff 純白 */

/* 陰影 */
var(--shadow-brand-sm)       /* 0px 5px 0px var(--color-black) 品牌卡片陰影 */
var(--shadow-brand-md)       /* 0px 7px 0px var(--color-black) hover 加深 */

/* 圓角 */
var(--radius-sm)             /* 8px */
var(--radius-md)             /* 12px */
var(--radius-lg)             /* 16px */
var(--radius-2xl)            /* 45px */
var(--radius-full)           /* 9999px */

/* 動畫 */
var(--transition-fast)       /* 0.20s linear — 按鈕/hover */
var(--transition-normal)     /* 0.30s ease — 卡片展開 */
var(--transition-slow)       /* 0.50s cubic-bezier — 圖片 zoom */

/* 層級 */
var(--z-index-nav)           /* 2 — 導覽列 */
var(--z-index-overlay)       /* 20 — Modal 遮罩 */
```

---

> **文件版本 v1.0** — 待老闆批准，批准後方可進入元件實作。
