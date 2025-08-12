
let csvData = [];
let currentRecommendations = [];

// === 對話狀態 ===
let chatHistory = [];      // {role:"user"|"model", text:"..."}
let lastChosenFund = null; // 上一輪主推薦基金（供追問接續）

// === 主推薦挑選（YTD > 3M > Sharpe）===
function pickBestFund(list){
  if (!list || !list.length) return null;
  const ranked = [...list].sort((a,b)=>{
    const k = x => [(x.rYTD ?? -999), (x.r3m ?? -999), (x.sharpe ?? -999)];
    const [ay,a3,as] = k(a), [by,b3,bs] = k(b);
    if (by !== ay) return by - ay;
    if (b3 !== a3) return b3 - a3;
    return bs - as;
  });
  return ranked[0];
}

// === 追問偵測與改寫（為什麼等短句）===
function isFollowUp(msg){
  const m = msg.trim();
  return m.length <= 8 && /(為什麼|為何|原因|理由|怎麼|why|還有)/i.test(m);
}
function rewriteFollowUp(msg){
  if (!lastChosenFund) return msg;
  return `針對上一輪推薦的「${lastChosenFund.name}」，請說明推薦理由與投資邏輯，包含：為何符合我的風險屬性、主要風險（波動/信用/匯率）、適合與不適合族群、以及檢視與再平衡建議。`;
}

document.addEventListener("DOMContentLoaded", function () {
  fetch("/static/data/基金資料1140405.csv")
    .then(response => response.text())
    .then(text => {
      parseCSV(text);
      populateDropdowns();
    })
    .catch(error => console.error("無法讀取 CSV:", error));
});

function parseCSV(text) {
  const lines = text.trim().split("\n");
  const headers = lines[0].replace("\ufeff", "").split(",");

  const nameIndex = headers.indexOf("標的名稱");
  const industryIndex = headers.indexOf("類型1");
  const countryIndex = headers.indexOf("投資區域");
  const stdDevIndex = headers.indexOf("標準差％");
  const sharpeIndex = headers.indexOf("夏普值");
  const betaIndex = headers.indexOf("β係數");
  const r3mIndex = headers.indexOf("三個月％");
  const ytdIndex = headers.indexOf("今年來％");

  csvData = lines.slice(1).map(line => {
    const columns = line.split(",");
    return {
      name: columns[nameIndex]?.trim(),
      stdDev: parseFloat(columns[stdDevIndex]) || 0,
      sharpe: parseFloat(columns[sharpeIndex]) || 0,
      beta: parseFloat(columns[betaIndex]) || 0,
      r3m: parseFloat(columns[r3mIndex]) || 0,
      rYTD: parseFloat(columns[ytdIndex]) || 0,
      industry: columns[industryIndex]?.trim(),
      country: columns[countryIndex]?.trim()
    };
  });
}

function populateDropdowns() {
  const industries = [...new Set(csvData.map(d => d.industry).filter(Boolean))].sort();
  const countries = [...new Set(csvData.map(d => d.country).filter(Boolean))].sort();

  const industrySelect = document.getElementById("industrySelect");
  const countrySelect = document.getElementById("countrySelect");

  industrySelect.innerHTML = "<option>請選擇類型</option>" + industries.map(i => `<option>${i}</option>`).join("");
  countrySelect.innerHTML = "<option>請選擇主要投資區域</option>" + countries.map(c => `<option>${c}</option>`).join("");
}

function submitTotalScore() {
  let totalScore = 0;
  let allAnswered = true;

  for (let i = 1; i <= 10; i++) {
    const selected = document.querySelector(`input[name="q${i}"]:checked`);
    if (!selected) {
      allAnswered = false;
      break;
    }
    totalScore += parseInt(selected.value);
  }

  if (!allAnswered) {
    alert("請完成所有問題！");
    return;
  }

  const riskLevel = determineRiskLevel(totalScore);
  document.getElementById("totalScore").textContent = totalScore;

  const riskElem = document.getElementById("riskLevel");
  riskElem.textContent = riskLevel;
  riskElem.className = "";
  if (riskLevel === "保守型") riskElem.classList.add("risk-conservative");
  if (riskLevel === "穩健型") riskElem.classList.add("risk-balanced");
  if (riskLevel === "積極型") riskElem.classList.add("risk-aggressive");

  const rawRecommendations = csvData.filter(f =>
    riskLevel === "保守型"
      ? f.stdDev <= 12 && f.sharpe >= 0.35 && f.beta >= 0 && f.beta <= 1 && (f.r3m >= 0 || f.rYTD >= 4)
      : riskLevel === "穩健型"
        ? f.stdDev <= 18 && f.sharpe >= 0.25 && f.beta >= 0.7 && f.beta <= 1.0 && (f.r3m >= -3 || f.rYTD >= 8)
        : riskLevel === "積極型"
          ? f.stdDev >= 18 && f.sharpe >= 0.1 && f.beta >= 1.0 && f.beta <= 2.0 && (f.r3m >= -5 || f.rYTD >= 10)
          : false
  );

  // 基金名稱前10字相同的只保留報酬率最高（簡易去重）
  const seen = new Map();
  rawRecommendations.forEach(fund => {
    const key = fund.name.slice(0, 10);
    if (!seen.has(key) || seen.get(key).rYTD < fund.rYTD) {
      seen.set(key, fund);
    }
  });
  currentRecommendations = Array.from(seen.values());

  populateDropdowns();
  filterByDropdowns();
  document.getElementById("result").style.display = "block";
  document.getElementById("chatBox").style.display = "block";
}

function determineRiskLevel(score) {
  if (score <= 16) return "保守型";
  if (score <= 23) return "穩健型";
  return "積極型";
}

function filterByDropdowns() {
  const selectedIndustry = document.getElementById("industrySelect").value;
  const selectedCountry = document.getElementById("countrySelect").value;

  const filtered = currentRecommendations.filter(fund =>
    (selectedIndustry === "請選擇類型" || fund.industry === selectedIndustry) &&
    (selectedCountry === "請選擇主要投資區域" || fund.country === selectedCountry)
  );

  // ★ 記住本輪主推薦（供追問接續）
  lastChosenFund = pickBestFund(filtered);

  const sorted = filtered.sort((a, b) => b.rYTD - a.rYTD).slice(0, 5);

  const tableBody = document.getElementById("fundTableBody");
  tableBody.innerHTML = sorted.length > 0
    ? sorted.map(f => `
        <tr>
          <td>${f.name}</td>
          <td>${f.industry}</td>
          <td>${f.country}</td>
          <td>${f.stdDev.toFixed(2)}%</td>
          <td>${f.sharpe.toFixed(2)}</td>
          <td>${f.beta.toFixed(2)}</td>
          <td>${f.r3m.toFixed(2)}%</td>
          <td>${f.rYTD.toFixed(2)}%</td>
        </tr>
      `).join("")
    : `<tr><td colspan="8">沒有符合條件的基金</td></tr>`;
}

// 綁定選單變更事件
document.addEventListener("change", function (e) {
  if (e.target.id === "industrySelect" || e.target.id === "countrySelect") {
    filterByDropdowns();
  }
});

const contextPrompt = `
你是一個投資顧問 AI，需要根據使用者的問卷結果與基金清單回答問題。
- 回覆時先顯示使用者的分數與風險屬性。
- 如果問題與基金推薦相關 → 從基金清單挑選最合適的基金，並解釋原因。
- 如果問題與基金比較/指標解釋相關 → 使用基金清單與投資知識回答。
- 如果問題不是基金相關 → 自由回答，保持專業語氣。
- 不要使用固定格式，要根據問題靈活作答。
`;

async function getAIResponse(message) {
  const chatInput = document.getElementById("chatInput");
  const chatArea = document.getElementById("chatArea");

  const scoreRaw = document.getElementById("totalScore").textContent || "";
  const scoreText = scoreRaw.match(/\d+/)?.[0] || "未提供";
  const riskText = document.getElementById("riskLevel").textContent || "未提供";

  // 追問偵測：必要時改寫成針對上一檔
  let userMsg = message.trim();
  if (isFollowUp(userMsg)) userMsg = rewriteFollowUp(userMsg);

  // 傳給模型的基金清單：限 10 檔，避免 token 過大
  const toSendFunds = currentRecommendations.slice(0, 10).map(f => ({
    基金名稱: f.name,
    類型: f.industry,
    投資地區: f.country,
    標準差: f.stdDev,
    夏普值: f.sharpe,
    Beta值: f.beta,
    三個月報酬: f.r3m,
    今年來報酬率: f.rYTD
  }));

  // 系統前言：引導模型處理邏輯
  const preamble = `
你是投資顧問 AI。請務必：
1) 先自然提及使用者「總分」與「風險屬性」。
2) 若[最適合的一檔]存在，優先以它作為主要推薦，說明推薦原因與對應風險；若不合適，再從[基金清單]挑選。
3) 比較時用條列，補充風險與檢視週期；避免誇大績效。
4) 僅能使用提供的基金與數據，不可編造。
`.trim();

  // 當前狀態：分數/風險 + 主推薦 + 清單
  const stateBlob = `
[使用者狀態]
- 總分：${scoreText}
- 風險屬性：${riskText}

[最適合的一檔（供你優先說明）]
${lastChosenFund ? JSON.stringify({
    基金名稱: lastChosenFund.name,
    類型: lastChosenFund.industry,
    投資地區: lastChosenFund.country,
    標準差: lastChosenFund.stdDev,
    夏普值: lastChosenFund.sharpe,
    Beta值: lastChosenFund.beta,
    三個月報酬: lastChosenFund.r3m,
    今年來報酬率: lastChosenFund.rYTD
  }, null, 2) : "（目前沒有上一檔或清單為空）"}

[基金清單（最多 10 檔）]
${JSON.stringify(toSendFunds, null, 2)}
`.trim();

  // === UI：加入使用者訊息 + loading ===
  const userMsgElement = document.createElement("div");
  userMsgElement.innerHTML = `<strong>你：</strong>${message}`;
  chatArea.appendChild(userMsgElement);

  const loadingDiv = document.createElement("div");
  loadingDiv.id = "loading";
  loadingDiv.innerHTML = `AI：<em>正在思考中...</em>`;
  chatArea.appendChild(loadingDiv);

  chatInput.value = "";

  // 帶入最近 8 則對話歷史
  const recent = chatHistory.slice(-8).map(m => ({
    role: m.role === "model" ? "model" : "user",
    parts: [{ text: m.text }]
  }));

  // 以「前言 → 歷史 → 當前訊息＋狀態」的順序送出
  const contents = [
    { role: "user", parts: [{ text: preamble }] },
    ...recent,
    { role: "user", parts: [{ text: userMsg + "\n\n" + stateBlob }] }
  ];

  try {
    // ★ 建議改用你的後端 proxy：/api/gemini
    const response = await fetch("/api/gemini", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ contents })
    });

    const data = await response.json();
    document.getElementById("loading")?.remove();

    if (!data?.candidates?.[0]?.content?.parts) {
      chatArea.innerHTML += `<div><strong>AI：</strong>⚠️ 無法取得有效回應，請稍後再試。</div>`;
      console.error("Gemini 回傳內容：", data);
      return;
    }

    const aiReply = data.candidates[0].content.parts.map(p => p.text).join("");

    // 顯示 AI 回覆
    const aiDiv = document.createElement("div");
    aiDiv.innerHTML = `<strong>AI：</strong>${aiReply.replace(/\n/g, "<br>")}`;
    chatArea.appendChild(aiDiv);

    const hr = document.createElement("hr");
    hr.style.cssText = "border:1px solid #ccc; margin:10px 0;";
    chatArea.appendChild(hr);

    // 更新「可被串接」的對話歷史（存改寫後的 userMsg）
    chatHistory.push({ role: "user", text: userMsg });
    chatHistory.push({ role: "model", text: aiReply });

    // 捲到最底
    chatArea.scrollTop = chatArea.scrollHeight;

  } catch (err) {
    document.getElementById("loading")?.remove();
    const errorDiv = document.createElement("div");
    errorDiv.innerHTML = `<strong>AI：</strong>⚠️ 發生錯誤：${err.message}`;
    chatArea.appendChild(errorDiv);

    const hr = document.createElement("hr");
    hr.style.cssText = "border:1px solid #ccc; margin:10px 0;";
    chatArea.appendChild(hr);

    chatArea.scrollTop = chatArea.scrollHeight;
  }
}

function sendChat() {
  const chatInput = document.getElementById("chatInput");
  const userMessage = chatInput.value.trim();
  const chatArea = document.getElementById("chatArea");

  if (!userMessage) {
    alert("請輸入問題再送出！");
    return;
  }

  if (!currentRecommendations.length) {
    alert("⚠️ 請先完成問卷並產生推薦結果，再進行提問！");
    return;
  }

  getAIResponse(userMessage);
}

// 讓 Enter 也能送出訊息
document.getElementById("chatInput").addEventListener("keypress", function (e) {
  if (e.key === "Enter") {
    e.preventDefault();
    sendChat();
  }
});
