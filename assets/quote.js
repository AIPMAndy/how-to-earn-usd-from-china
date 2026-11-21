/* 本机纯计算：无网络请求、无汇率抓取、无追踪。 */
(function (root) {
  "use strict";
  const FIELDS = ["quote", "percent", "fixed", "direct", "fx", "bank", "hours", "target"];
  function finite(value, name, min, max, exclusive) {
    if (value === "" || value === null || value === undefined || typeof value === "boolean")
      throw new Error(name + "不能为空");
    const n = Number(value);
    if (!Number.isFinite(n) || (exclusive ? n <= min : n < min) || n > max)
      throw new Error(name + "超出允许范围");
    return n;
  }
  function calculate(raw) {
    const quote = finite(raw.quote, "美元报价", 0, 1e10, true);
    const percent = finite(raw.percent, "平台费率", 0, 100, false);
    const fixed = finite(raw.fixed, "固定手续费", 0, 1e10, false);
    const direct = finite(raw.direct, "直接履约成本", 0, 1e10, false);
    const fx = finite(raw.fx, "假设汇率", 0, 1000, true);
    const bank = finite(raw.bank, "境内入账手续费", 0, 1e10, false);
    const hours = finite(raw.hours, "履约工时", 0, 100000, true);
    const target = finite(raw.target, "期望时薪", 0, 1e10, false);
    const platform = quote * percent / 100;
    const netUSD = quote - platform - fixed - direct;
    const netCNY = netUSD * fx - bank;
    const hourly = netCNY / hours;
    return { quote, percent, fixed, direct, fx, bank, hours, target,
      platform, netUSD, netCNY, hourly, gap: hourly - target,
      clearsTarget: hourly >= target };
  }
  function csv(data) {
    const pairs = [
      ["USD quote", data.quote], ["Platform fee percent", data.percent],
      ["Platform fee USD", data.platform], ["Fixed fee USD", data.fixed],
      ["Direct cost USD", data.direct], ["Assumed CNY per USD", data.fx],
      ["Bank fee CNY", data.bank], ["Delivery hours", data.hours],
      ["Target CNY per hour", data.target], ["Net USD before tax", data.netUSD],
      ["Estimated CNY before tax", data.netCNY], ["CNY per hour", data.hourly],
      ["Gap CNY per hour", data.gap]
    ];
    return "\ufeff" + "Field,Value\r\n" + pairs.map(function (item) {
      return item[0] + "," + String(Number(item[1].toFixed(6)));
    }).join("\r\n") + "\r\n" +
      "Note,Teaching calculation only - not tax advice or confirmed bank settlement\r\n";
  }
  const api = { calculate, csv, fields: FIELDS.slice() };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  if (typeof document === "undefined") return;

  const form = document.getElementById("quote-form");
  if (!form) return;
  const error = document.getElementById("quote-error");
  const out = document.getElementById("quote-output");
  const exportBtn = document.getElementById("export-quote");
  const status = document.getElementById("quote-status");
  let last = null;
  const fmt = function (n, currency) {
    return new Intl.NumberFormat("zh-CN", { minimumFractionDigits: 2,
      maximumFractionDigits: 2, style: "currency", currency: currency }).format(n);
  };
  function update() {
    const raw = {};
    FIELDS.forEach(function (key) { raw[key] = form.elements.namedItem(key).value.trim(); });
    try {
      const d = calculate(raw);
      last = d;
      error.textContent = "";
      document.getElementById("out-usd").textContent = fmt(d.netUSD, "USD");
      document.getElementById("out-cny").textContent = fmt(d.netCNY, "CNY");
      document.getElementById("out-hourly").textContent = fmt(d.hourly, "CNY");
      document.getElementById("out-gap").textContent = fmt(d.gap, "CNY") + " / 小时";
      status.textContent = d.netCNY < 0 ? "当前假设下净额为负，请先重算报价与成本。" :
        (d.clearsTarget ? "达到你填写的期望时薪（仅按本次假设）。" :
          "低于你填写的期望时薪（仅按本次假设）。");
      out.hidden = false;
      exportBtn.disabled = false;
    } catch (e) {
      last = null;
      out.hidden = true;
      exportBtn.disabled = true;
      error.textContent = e.message;
      status.textContent = "";
    }
  }
  form.addEventListener("input", update);
  form.addEventListener("submit", function (event) { event.preventDefault(); update(); });
  document.getElementById("demo-quote").addEventListener("click", function () {
    const sample = { quote: "500", percent: "10", fixed: "5", direct: "80",
      fx: "7", bank: "20", hours: "12", target: "150" };
    FIELDS.forEach(function (key) { form.elements.namedItem(key).value = sample[key]; });
    document.getElementById("sample-note").hidden = false;
    update();
  });
  exportBtn.addEventListener("click", function () {
    if (!last) return;
    const url = URL.createObjectURL(new Blob([csv(last)], { type: "text/csv;charset=utf-8" }));
    const a = document.createElement("a");
    a.href = url;
    a.download = "usd-quote-estimate.csv";
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  });
  const copyBtn = document.getElementById("copy-wechat");
  const copyStatus = document.getElementById("copy-wechat-status");
  copyBtn.addEventListener("click", async function () {
    try {
      if (!navigator.clipboard || !window.isSecureContext) throw new Error("clipboard unavailable");
      await navigator.clipboard.writeText("AIPMAndy");
      copyStatus.textContent = "已复制微信号 AIPMAndy";
    } catch (_) {
      copyStatus.textContent = "无法自动复制，请手动复制 AIPMAndy";
    }
  });
  update();
})(typeof globalThis !== "undefined" ? globalThis : this);
