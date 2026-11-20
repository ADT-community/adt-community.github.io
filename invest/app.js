// ADT Invest: practice-mode investing app. All money and prices here are practice only.
(() => {
"use strict";
const KEY = "adt-invest-v1";
const DAY = 86400000;
const $ = id => document.getElementById(id);
const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const STOCKS = Object.fromEntries(INVEST.stocks.map(s => [s.t, s]));
const RATE = INVEST.sampleUsdRate;

// ---------- storage ----------
let S = load();
function load() {
  try { const raw = localStorage.getItem(KEY); if (raw) return JSON.parse(raw); } catch (e) {}
  return null;
}
function save() { try { localStorage.setItem(KEY, JSON.stringify(S)); } catch (e) {} }
function fresh(name, phone) {
  return { v: 1, user: { name, phone, joined: Date.now(), ref: "ADT" + Math.random().toString(36).slice(2, 7).toUpperCase() },
    cash: INVEST.practiceStartGHS, holdings: {}, orders: [], watch: ["MTNGH", "AAPL"], alerts: [], recurring: [],
    activity: [{ ts: Date.now(), text: `Added ₵${fmt(INVEST.practiceStartGHS)} practice money` }], lessons: {}, prices: seedPrices() };
}

// ---------- prices (simulated) ----------
function rng(seed) { let x = seed >>> 0; return () => ((x = (x * 1664525 + 1013904223) >>> 0) / 4294967296); }
function seedPrices() {
  const out = {};
  INVEST.stocks.forEach((s, i) => {
    const r = rng(1000 + i * 7919), vol = s.m === "US" ? 0.018 : 0.012;
    const hist = [s.p];
    for (let d = 1; d < 365; d++) hist.unshift(Math.max(0.05, hist[0] / (1 + (r() - 0.48) * vol * 2)));
    out[s.t] = { p: s.p, hist: hist.map(v => round(v, s.c === "USD" ? 2 : 3)), open: s.p, day: today() };
  });
  return out;
}
function today() { return new Date().toISOString().slice(0, 10); }
function round(v, d = 2) { const f = 10 ** d; return Math.round(v * f) / f; }
function price(t) { return S.prices[t].p; }
function changePct(t) { const q = S.prices[t]; return q.open ? (q.p / q.open - 1) * 100 : 0; }
function inCedis(t, amount) { return STOCKS[t].c === "USD" ? amount * RATE : amount; }
function tick() {
  if (!S) return;
  for (const s of INVEST.stocks) {
    const q = S.prices[s.t];
    if (q.day !== today()) { q.hist.push(q.p); q.hist = q.hist.slice(-365); q.open = q.p; q.day = today(); }
    const vol = s.m === "US" ? 0.0035 : 0.002;
    q.p = round(Math.max(0.05, q.p * (1 + (Math.random() - 0.5) * vol)), s.c === "USD" ? 2 : 3);
  }
  fillLimits(); checkAlerts(); runRecurring(); save();
  updateCash();
}

// ---------- money ----------
const fmt = (v, d = 2) => Number(v).toLocaleString("en-GH", { minimumFractionDigits: d, maximumFractionDigits: d });
const money = (v, c = "GHS") => (c === "USD" ? "$" : "₵") + fmt(v);
const pct = v => `${v >= 0 ? "+" : ""}${fmt(v)}%`;
function holdingValueGHS(t) { const h = S.holdings[t]; return h ? inCedis(t, h.qty * price(t)) : 0; }
function portfolioGHS() { return Object.keys(S.holdings).reduce((n, t) => n + holdingValueGHS(t), 0); }
function costGHS() { return Object.values(S.holdings).reduce((n, h) => n + h.costGHS, 0); }
function log(text) { S.activity.unshift({ ts: Date.now(), text }); S.activity = S.activity.slice(0, 100); }

function buy(t, ghs, how = "Bought") {
  const fee = round(ghs * INVEST.feePct / 100), spend = ghs - fee;
  if (ghs < INVEST.minGHS) return `Minimum is ₵${INVEST.minGHS}`;
  if (ghs > S.cash + 1e-9) return "Not enough practice cash";
  const qty = spend / inCedis(t, price(t));
  const h = S.holdings[t] || (S.holdings[t] = { qty: 0, costGHS: 0 });
  h.qty += qty; h.costGHS += spend; S.cash = round(S.cash - ghs);
  S.orders.unshift({ id: Date.now() + Math.random(), t, side: "buy", type: "market", qty, ghs, fee, price: price(t), status: "filled", ts: Date.now() });
  log(`${how} ${fmtQty(qty)} ${t} for ₵${fmt(ghs)} (fee ₵${fmt(fee)})`);
  return null;
}
function sell(t, qty) {
  const h = S.holdings[t]; if (!h || qty <= 0) return "Nothing to sell";
  qty = Math.min(qty, h.qty);
  const gross = inCedis(t, qty * price(t)), fee = round(gross * INVEST.feePct / 100), net = gross - fee;
  h.costGHS -= h.costGHS * (qty / h.qty); h.qty -= qty;
  if (h.qty < 1e-9) delete S.holdings[t];
  S.cash = round(S.cash + net);
  S.orders.unshift({ id: Date.now() + Math.random(), t, side: "sell", type: "market", qty, ghs: net, fee, price: price(t), status: "filled", ts: Date.now() });
  log(`Sold ${fmtQty(qty)} ${t} for ₵${fmt(net)} (fee ₵${fmt(fee)})`);
  return null;
}
function fmtQty(q) { return q >= 1 ? fmt(q, 3) : q.toPrecision(3); }

function fillLimits() {
  for (const o of S.orders) {
    if (o.status !== "open") continue;
    const p = price(o.t);
    if (o.side === "buy" && p <= o.limit) {
      S.cash = round(S.cash + o.ghs); // release the reserved cash, then buy
      const e = buy(o.t, o.ghs, "Limit buy filled:"); o.status = e ? "cancelled" : "filled"; if (!e) toast(`Limit buy filled: ${o.t}`);
    } else if (o.side === "sell" && p >= o.limit) {
      const e = sell(o.t, o.qty); o.status = e ? "cancelled" : "filled"; if (!e) toast(`Limit sell filled: ${o.t}`);
    }
  }
  S.orders = S.orders.filter((o, i) => !(o.status === "filled" && o.type === "limit" && i > 200));
}
function checkAlerts() {
  for (const a of S.alerts) {
    if (a.hit) continue;
    const p = price(a.t);
    if ((a.dir === "above" && p >= a.price) || (a.dir === "below" && p <= a.price)) {
      a.hit = Date.now(); toast(`🔔 ${a.t} is ${a.dir} ${money(a.price, STOCKS[a.t].c)}: now ${money(p, STOCKS[a.t].c)}`);
      log(`Price alert: ${a.t} ${a.dir} ${money(a.price, STOCKS[a.t].c)}`);
    }
  }
}
function runRecurring() {
  for (const r of S.recurring) {
    let guard = 0;
    while (r.next <= Date.now() && guard++ < 12) {
      const e = buy(r.t, r.ghs, "Auto-invest:");
      if (e) { log(`Auto-invest skipped for ${r.t}: ${e}`); }
      r.next += r.freq === "weekly" ? 7 * DAY : 30 * DAY;
    }
  }
}

// ---------- ui helpers ----------
let toastTimer;
function toast(msg) { const t = $("toast"); t.textContent = msg; t.hidden = false; clearTimeout(toastTimer); toastTimer = setTimeout(() => (t.hidden = true), 3500); }
function updateCash() { $("cash").textContent = S ? `Cash ${money(S.cash)}` : ""; }
function logo(t) { const s = STOCKS[t]; return `<div class="logo${s.m === "US" ? " us" : ""}">${esc(t.slice(0, 4))}</div>`; }
function chg(v) { return `<span class="${v >= 0 ? "up" : "down"}">${pct(v)}</span>`; }
function stockRow(t, extra = "") {
  const s = STOCKS[t];
  return `<a class="row" href="#stock/${t}">${logo(t)}<div class="grow"><b>${esc(s.n)}</b><span class="sub">${esc(t)} · ${s.m === "GSE" ? "Ghana" : "US"}${extra}</span></div>
    <div class="right"><b>${money(price(t), s.c)}</b><br>${chg(changePct(t))}</div></a>`;
}
function chart(t, days) {
  const q = S.prices[t], data = [...q.hist.slice(-days), q.p];
  const min = Math.min(...data), max = Math.max(...data), w = 320, h = 160, pad = 6;
  const pts = data.map((v, i) => `${(i / (data.length - 1)) * w},${h - pad - ((v - min) / (max - min || 1)) * (h - pad * 2)}`).join(" ");
  const up = data[data.length - 1] >= data[0];
  return `<svg class="chart" viewBox="0 0 ${w} ${h}" preserveAspectRatio="none" role="img" aria-label="${esc(t)} price, last ${days} days">
    <polyline fill="none" stroke="${up ? "var(--up)" : "var(--down)"}" stroke-width="2.2" vector-effect="non-scaling-stroke" points="${pts}"/></svg>`;
}
function rangePct(t, days) { const q = S.prices[t], h = q.hist; const old = h[Math.max(0, h.length - days)]; return (q.p / old - 1) * 100; }
function openSheet(html) { $("sheet").innerHTML = html; $("sheet").hidden = false; $("sheetbg").hidden = false; }
function closeSheet() { $("sheet").hidden = true; $("sheetbg").hidden = true; $("sheet").innerHTML = ""; }
$("sheetbg").onclick = closeSheet;
$("back").onclick = () => history.length > 1 ? history.back() : (location.hash = "#home");

// ---------- views ----------
function welcome() {
  $("tabs").hidden = true; $("cash").textContent = "";
  $("view").innerHTML = `<div class="welcome">
    <p class="sub">ADT Invest</p>
    <p class="big">Own Ghana and US companies from ₵20.</p>
    <p class="sub">MTN Ghana, GCB, Apple, Amazon and more. Start in practice mode with ₵${fmt(INVEST.practiceStartGHS, 0)} of practice money. No real money, no risk.</p>
    <form id="join" novalidate style="margin-top:18px">
      <label class="f">Your first name <input name="fname" id="fname" autocomplete="given-name" required></label>
      <label class="f">Phone number
        <div class="phone"><select id="code" aria-label="Country code"></select><input id="local" inputmode="tel" placeholder="024 123 4567" aria-label="Phone number"></div></label>
      <p class="err" id="err" role="alert"></p>
      <button class="btn block" type="submit">Start practising</button>
    </form>
    <p class="sub" style="margin-top:14px">Real trading opens once we've partnered with licensed brokers. Practice now and you'll be first in line.</p></div>`;
  adtPhoneSelect($("code")); $("code").value = "+233";
  $("join").onsubmit = e => {
    e.preventDefault();
    const name = $("fname").value.trim(), phone = adtValidPhone($("code").value, $("local").value);
    if (!name) return ($("err").textContent = "Enter your first name.");
    if (!phone) return ($("err").textContent = "Enter an African phone number.");
    S = fresh(name, phone); save(); location.hash = "#home"; render();
  };
}

function home() {
  const value = portfolioGHS(), cost = costGHS(), gain = value - cost, total = value + S.cash;
  const held = Object.keys(S.holdings).sort((a, b) => holdingValueGHS(b) - holdingValueGHS(a));
  const open = S.orders.filter(o => o.status === "open");
  return `<div class="card"><span class="sub">Total practice value</span><div class="big">${money(total)}</div>
      <span class="sub">Investments ${money(value)} · ${cost ? chg((gain / cost) * 100) + " " + (gain >= 0 ? "+" : "−") + money(Math.abs(gain)) : "nothing invested yet"}</span>
      <div class="pair" style="margin-top:14px"><a class="btn" href="#discover">Invest</a><button class="btn ghost" data-act="deposit">Add money</button></div></div>
    <h2>Your investments</h2><div class="card">${held.length ? held.map(t => {
      const h = S.holdings[t], v = holdingValueGHS(t), g = h.costGHS ? (v / h.costGHS - 1) * 100 : 0;
      return `<a class="row" href="#stock/${t}">${logo(t)}<div class="grow"><b>${esc(STOCKS[t].n)}</b><span class="sub">${fmtQty(h.qty)} shares</span></div>
        <div class="right"><b>${money(v)}</b><br>${chg(g)}</div></a>`; }).join("")
      : `<p class="empty">You don't own anything yet.<br><a href="#discover">Find your first company</a></p>`}</div>
    ${open.length ? `<h2>Waiting orders</h2><div class="card">${open.map(o => `<div class="row"><div class="grow"><b>Limit ${o.side} ${esc(o.t)}</b>
      <span class="sub">${o.side === "buy" ? "₵" + fmt(o.ghs) : fmtQty(o.qty) + " shares"} at ${money(o.limit, STOCKS[o.t].c)} or ${o.side === "buy" ? "lower" : "higher"}</span></div>
      <button class="btn ghost" data-cancel="${o.id}">Cancel</button></div>`).join("")}</div>` : ""}
    ${S.recurring.length ? `<h2>Auto-invest</h2><div class="card">${S.recurring.map(r => `<div class="row"><div class="grow"><b>${money(r.ghs)} ${r.freq} into ${esc(r.t)}</b>
      <span class="sub">Next: ${new Date(r.next).toLocaleDateString("en-GH")}</span></div><button class="btn ghost" data-stoprec="${r.id}">Stop</button></div>`).join("")}</div>` : ""}
    <h2>Watchlist</h2><div class="card">${S.watch.length ? S.watch.map(t => stockRow(t)).join("") : `<p class="empty">Tap ☆ on any company to watch it.</p>`}</div>
    <h2>Activity</h2><div class="card">${S.activity.slice(0, 6).map(a => `<div class="row"><div class="grow"><span>${esc(a.text)}</span>
      <span class="sub">${new Date(a.ts).toLocaleString("en-GH", { dateStyle: "medium", timeStyle: "short" })}</span></div></div>`).join("")}</div>`;
}

let disc = { market: "all", theme: "", q: "" };
function discover() {
  let list = INVEST.stocks.filter(s => (disc.market === "all" || s.m === disc.market) && (!disc.theme || s.themes.includes(disc.theme))
    && (!disc.q || (s.n + " " + s.t).toLowerCase().includes(disc.q.toLowerCase())));
  const movers = [...INVEST.stocks].sort((a, b) => Math.abs(changePct(b.t)) - Math.abs(changePct(a.t))).slice(0, 4);
  return `<input class="search" id="q" type="search" placeholder="Search companies, e.g. MTN, Apple" value="${esc(disc.q)}" aria-label="Search">
    <div class="chips" style="margin-top:10px">${[["all", "All"], ["GSE", "🇬🇭 Ghana"], ["US", "🇺🇸 US"]].map(([k, n]) =>
      `<button class="chip${disc.market === k ? " on" : ""}" data-market="${k}">${n}</button>`).join("")}</div>
    <div class="chips">${INVEST.themes.map(th => `<button class="chip${disc.theme === th.id ? " on" : ""}" data-theme="${th.id}">${esc(th.name)}</button>`).join("")}</div>
    ${!disc.q && !disc.theme && disc.market === "all" ? `<h2>Moving today</h2><div class="card">${movers.map(s => stockRow(s.t)).join("")}</div><h2>All companies</h2>` : ""}
    <div class="card">${list.length ? list.map(s => stockRow(s.t, s.y ? ` · ${fmt(s.y, 1)}% dividend` : "")).join("") : `<p class="empty">No companies match.</p>`}</div>`;
}

let range = 30;
function stock(t) {
  const s = STOCKS[t]; if (!s) return `<p class="empty">Company not found.</p>`;
  const h = S.holdings[t], watching = S.watch.includes(t), alerts = S.alerts.filter(a => a.t === t && !a.hit);
  return `<div class="card"><div class="row" style="padding-top:0">${logo(t)}<div class="grow"><b>${esc(s.n)}</b><span class="sub">${esc(t)} · ${s.m === "GSE" ? "Ghana Stock Exchange" : "US market"}</span></div>
      <button class="star" data-watch="${t}" aria-label="${watching ? "Remove from" : "Add to"} watchlist">${watching ? "★" : "☆"}</button></div>
    <div class="big">${money(price(t), s.c)}</div>
    <span class="sub">${s.c === "USD" ? `≈ ${money(price(t) * RATE)} per share · ` : ""}${chg(rangePct(t, range))} in ${range >= 365 ? "1 year" : range >= 180 ? "6 months" : range >= 30 ? "1 month" : "1 week"}</span>
    ${chart(t, range)}
    <div class="ranges">${[[7, "1W"], [30, "1M"], [180, "6M"], [365, "1Y"]].map(([d, n]) => `<button class="chip${range === d ? " on" : ""}" data-range="${d}">${n}</button>`).join("")}</div></div>
    ${h ? `<div class="card"><span class="sub">You own</span><div class="line"><span>${fmtQty(h.qty)} shares</span><b>${money(holdingValueGHS(t))}</b></div>
      <div class="line"><span>Return</span>${chg((holdingValueGHS(t) / h.costGHS - 1) * 100)}</div></div>` : ""}
    <div class="pair"><button class="btn" data-act="buy" data-t="${t}">Buy</button><button class="btn ghost" data-act="sell" data-t="${t}" ${h ? "" : "disabled"}>Sell</button></div>
    <h2>About</h2><div class="card"><p style="margin-top:0">${esc(s.about)}</p>
      <div class="kv"><div><small>Sector</small>${esc(s.s)}</div><div><small>Dividend yield</small>${s.y ? fmt(s.y, 1) + "% a year" : "None"}</div>
      <div><small>1-year change</small>${chg(rangePct(t, 365))}</div><div><small>Smallest buy</small>₵${INVEST.minGHS}</div></div></div>
    <h2>Price alerts</h2><div class="card">${alerts.map(a => `<div class="line"><span>🔔 ${a.dir} ${money(a.price, s.c)}</span><button class="chip" data-delalert="${a.id}">Remove</button></div>`).join("")}
      <button class="btn ghost block" data-act="alert" data-t="${t}">Set a price alert</button></div>
    <h2>More</h2><div class="pair"><button class="btn ghost" data-act="recurring" data-t="${t}">Auto-invest</button><button class="btn ghost" data-act="compare" data-t="${t}">Compare</button></div>
    <p class="sub" style="margin-top:16px">Practice mode: prices are sample prices that move in a simulation, not live market prices.</p>`;
}

function learn() {
  const done = Object.keys(S.lessons).length;
  return `<div class="card"><b>${done} of ${LESSONS.length} lessons done</b><br><span class="sub">Short lessons, 1–2 minutes each. Twi versions coming soon.</span></div>
    <div class="card">${LESSONS.map(l => `<a class="row" href="#lesson/${l.id}"><div class="logo">${S.lessons[l.id] != null ? "✓" : l.id}</div>
      <div class="grow"><b>${esc(l.title)}</b><span class="sub">${l.mins} min${S.lessons[l.id] != null ? ` · quiz ${S.lessons[l.id]}/3` : ""}</span></div></a>`).join("")}</div>
    <p class="sub">General education, not financial advice.</p>`;
}
function lesson(id) {
  const l = LESSONS.find(x => x.id === +id); if (!l) return `<p class="empty">Lesson not found.</p>`;
  const next = LESSONS.find(x => x.id === l.id + 1);
  return `<div class="card lesson">${l.body.map(p => `<p>${esc(p)}</p>`).join("")}</div>
    <h2>Quick quiz</h2><div class="card quiz" id="quiz">${l.quiz.map((q, qi) => `<p style="margin-top:${qi ? 18 : 0}px"><b>${esc(q[0])}</b></p>
      ${q[1].map((o, oi) => `<button data-q="${qi}" data-o="${oi}">${esc(o)}</button>`).join("")}`).join("")}
      <p class="sub" id="score"></p></div>
    ${next ? `<a class="btn block" href="#lesson/${next.id}">Next: ${esc(next.title)}</a>` : `<a class="btn block" href="#discover">Make your first practice buy</a>`}`;
}

function account() {
  return `<div class="card"><b>${esc(S.user.name)}</b><br><span class="sub">${esc(S.user.phone)} · practice account</span></div>
    <h2>Practice wallet</h2><div class="card"><div class="line"><span>Cash</span><b>${money(S.cash)}</b></div>
      <div class="pair" style="margin-top:10px"><button class="btn" data-act="deposit">Add money</button><button class="btn ghost" data-act="withdraw">Withdraw</button></div>
      <p class="sub">Sample rate for US shares: $1 = ₵${fmt(RATE)}. Your cedis are converted only when you buy a US share, and the rate is shown first.</p></div>
    <h2>Real trading</h2><div class="card"><p style="margin-top:0">Real investing opens once ADT Invest is live with licensed broker partners. Join the waitlist to be first.</p>
      <button class="btn block" data-act="waitlist">Join the waitlist</button></div>
    <h2>Invite friends</h2><div class="card"><p style="margin-top:0">Your invite code: <b>${esc(S.user.ref)}</b></p>
      <button class="btn ghost block" data-act="share">Share ADT Invest</button></div>
    <h2>Order history</h2><div class="card">${S.orders.slice(0, 15).map(o => `<div class="row"><div class="grow"><b>${o.side === "buy" ? "Buy" : "Sell"} ${esc(o.t)} <span class="badge">${o.type}</span></b>
      <span class="sub">${new Date(o.ts).toLocaleDateString("en-GH")} · ${o.status}</span></div><div class="right">${o.ghs ? money(o.ghs) : fmtQty(o.qty)}</div></div>`).join("") || `<p class="empty">No orders yet.</p>`}</div>
    <button class="btn ghost block" data-act="reset" style="margin-top:8px">Reset practice account</button>
    <p class="sub" style="margin-top:14px">ADT Invest is in practice mode. Nothing here is a real investment or financial advice.</p>`;
}

// ---------- sheets ----------
function buySheet(t) {
  const s = STOCKS[t];
  openSheet(`<h3>Buy ${esc(s.n)}</h3><span class="sub">${money(price(t), s.c)} per share${s.c === "USD" ? ` (≈ ${money(price(t) * RATE)})` : ""}</span>
    <div class="seg"><button class="on" data-mode="market">Buy now</button><button data-mode="limit">At a price (limit)</button></div>
    <label class="sub" for="amt">Amount in cedis</label><input class="amount" id="amt" inputmode="decimal" placeholder="₵0" autofocus>
    <div class="chips">${[20, 50, 100, 500].map(v => `<button class="chip" data-amt="${v}">₵${v}</button>`).join("")}</div>
    <div id="limitbox" hidden><label class="f">Buy when the price is at or below (${s.c === "USD" ? "$" : "₵"})<input id="lim" inputmode="decimal" value="${round(price(t) * 0.98, s.c === "USD" ? 2 : 3)}"></label></div>
    <div id="sum"></div><p class="err" id="err"></p><button class="btn block" id="go">Review</button>`);
  let mode = "market";
  const sum = () => {
    const a = parseFloat($("amt").value) || 0, fee = round(a * INVEST.feePct / 100), shares = (a - fee) / inCedis(t, price(t));
    $("sum").innerHTML = a ? `<div class="line"><span>Shares (about)</span><span>${fmtQty(Math.max(0, shares))}</span></div>
      ${s.c === "USD" ? `<div class="line"><span>In dollars</span><span>${money((a - fee) / RATE, "USD")}</span></div>` : ""}
      <div class="line"><span>Fee (${INVEST.feePct}%)</span><span>${money(fee)}</span></div><div class="line total"><span>Total</span><span>${money(a)}</span></div>` : "";
  };
  $("amt").oninput = sum;
  $("sheet").querySelectorAll("[data-amt]").forEach(b => b.onclick = () => { $("amt").value = b.dataset.amt; sum(); });
  $("sheet").querySelectorAll("[data-mode]").forEach(b => b.onclick = () => {
    mode = b.dataset.mode; $("sheet").querySelectorAll("[data-mode]").forEach(x => x.classList.toggle("on", x === b)); $("limitbox").hidden = mode !== "limit"; });
  $("go").onclick = () => {
    const a = parseFloat($("amt").value) || 0;
    if (a < INVEST.minGHS) return ($("err").textContent = `The smallest buy is ₵${INVEST.minGHS}.`);
    if (a > S.cash) return ($("err").textContent = `You have ${money(S.cash)} practice cash. Add money or buy less.`);
    if (mode === "limit") {
      const lim = parseFloat($("lim").value);
      if (!(lim > 0)) return ($("err").textContent = "Enter a limit price.");
      S.cash = round(S.cash - a);
      S.orders.unshift({ id: Date.now(), t, side: "buy", type: "limit", limit: lim, ghs: a, status: "open", ts: Date.now() });
      log(`Limit buy placed: ₵${fmt(a)} of ${t} at ${money(lim, s.c)} or lower`); save(); closeSheet(); toast("Limit order placed"); return render();
    }
    const e = buy(t, a); if (e) return ($("err").textContent = e);
    save(); closeSheet(); toast(`You bought ${t} (practice)`); render();
  };
  sum();
}
function sellSheet(t) {
  const s = STOCKS[t], h = S.holdings[t]; if (!h) return;
  openSheet(`<h3>Sell ${esc(s.n)}</h3><span class="sub">You own ${fmtQty(h.qty)} shares, worth ${money(holdingValueGHS(t))}</span>
    <div class="seg"><button class="on" data-mode="market">Sell now</button><button data-mode="limit">At a price (limit)</button></div>
    <label class="sub" for="amt">Shares to sell</label><input class="amount" id="amt" inputmode="decimal" value="${round(h.qty, 6)}">
    <div class="chips">${[[0.25, "25%"], [0.5, "50%"], [1, "All"]].map(([f, n]) => `<button class="chip" data-frac="${f}">${n}</button>`).join("")}</div>
    <div id="limitbox" hidden><label class="f">Sell when the price is at or above (${s.c === "USD" ? "$" : "₵"})<input id="lim" inputmode="decimal" value="${round(price(t) * 1.02, s.c === "USD" ? 2 : 3)}"></label></div>
    <div id="sum"></div><p class="err" id="err"></p><button class="btn red block" id="go">Sell</button>`);
  let mode = "market";
  const sum = () => {
    const q = Math.min(parseFloat($("amt").value) || 0, h.qty), gross = inCedis(t, q * price(t)), fee = round(gross * INVEST.feePct / 100);
    $("sum").innerHTML = q ? `<div class="line"><span>Value</span><span>${money(gross)}</span></div><div class="line"><span>Fee (${INVEST.feePct}%)</span><span>${money(fee)}</span></div>
      <div class="line total"><span>You receive</span><span>${money(gross - fee)}</span></div>` : "";
  };
  $("amt").oninput = sum;
  $("sheet").querySelectorAll("[data-frac]").forEach(b => b.onclick = () => { $("amt").value = round(h.qty * +b.dataset.frac, 6); sum(); });
  $("sheet").querySelectorAll("[data-mode]").forEach(b => b.onclick = () => {
    mode = b.dataset.mode; $("sheet").querySelectorAll("[data-mode]").forEach(x => x.classList.toggle("on", x === b)); $("limitbox").hidden = mode !== "limit"; });
  $("go").onclick = () => {
    const q = parseFloat($("amt").value) || 0;
    if (q <= 0 || q > h.qty + 1e-9) return ($("err").textContent = "Enter how many shares to sell.");
    if (mode === "limit") {
      const lim = parseFloat($("lim").value); if (!(lim > 0)) return ($("err").textContent = "Enter a limit price.");
      S.orders.unshift({ id: Date.now(), t, side: "sell", type: "limit", limit: lim, qty: q, status: "open", ts: Date.now() });
      log(`Limit sell placed: ${fmtQty(q)} ${t} at ${money(lim, s.c)} or higher`); save(); closeSheet(); toast("Limit order placed"); return render();
    }
    const e = sell(t, q); if (e) return ($("err").textContent = e);
    save(); closeSheet(); toast(`Sold ${t} (practice)`); render();
  };
  sum();
}
function alertSheet(t) {
  const s = STOCKS[t];
  openSheet(`<h3>Price alert for ${esc(t)}</h3><span class="sub">Now ${money(price(t), s.c)}. We'll tell you in the app when it gets there.</span>
    <div class="seg"><button class="on" data-dir="above">Goes above</button><button data-dir="below">Goes below</button></div>
    <label class="f">Price (${s.c === "USD" ? "$" : "₵"})<input id="ap" inputmode="decimal" value="${round(price(t) * 1.05, s.c === "USD" ? 2 : 3)}"></label>
    <p class="err" id="err"></p><button class="btn block" id="go">Set alert</button>`);
  let dir = "above";
  $("sheet").querySelectorAll("[data-dir]").forEach(b => b.onclick = () => { dir = b.dataset.dir; $("sheet").querySelectorAll("[data-dir]").forEach(x => x.classList.toggle("on", x === b)); });
  $("go").onclick = () => { const p = parseFloat($("ap").value); if (!(p > 0)) return ($("err").textContent = "Enter a price.");
    S.alerts.push({ id: Date.now(), t, dir, price: p }); save(); closeSheet(); toast("Alert set"); render(); };
}
function recurringSheet(t) {
  openSheet(`<h3>Auto-invest in ${esc(STOCKS[t].n)}</h3><span class="sub">Buy a fixed amount regularly, starting now.</span>
    <label class="f" style="margin-top:12px">Amount (₵)<input id="ra" inputmode="decimal" value="50"></label>
    <div class="seg"><button class="on" data-f="weekly">Every week</button><button data-f="monthly">Every month</button></div>
    <p class="err" id="err"></p><button class="btn block" id="go">Start auto-invest</button>`);
  let freq = "weekly";
  $("sheet").querySelectorAll("[data-f]").forEach(b => b.onclick = () => { freq = b.dataset.f; $("sheet").querySelectorAll("[data-f]").forEach(x => x.classList.toggle("on", x === b)); });
  $("go").onclick = () => { const a = parseFloat($("ra").value) || 0; if (a < INVEST.minGHS) return ($("err").textContent = `At least ₵${INVEST.minGHS}.`);
    S.recurring.push({ id: Date.now(), t, ghs: a, freq, next: Date.now() }); runRecurring(); save(); closeSheet(); toast("Auto-invest started"); render(); };
}
function compareSheet(t) {
  openSheet(`<h3>Compare ${esc(t)} with…</h3><select id="other" class="search" style="margin:10px 0">${INVEST.stocks.filter(s => s.t !== t)
    .map(s => `<option value="${s.t}">${esc(s.n)} (${s.t})</option>`).join("")}</select><div id="cmp"></div>`);
  const draw = () => { const o = $("other").value, A = STOCKS[t], B = STOCKS[o];
    const rowsFor = [["Price", money(price(t), A.c), money(price(o), B.c)], ["Today", chg(changePct(t)), chg(changePct(o))],
      ["1 month", chg(rangePct(t, 30)), chg(rangePct(o, 30))], ["1 year", chg(rangePct(t, 365)), chg(rangePct(o, 365))],
      ["Dividend", A.y ? fmt(A.y, 1) + "%" : "None", B.y ? fmt(B.y, 1) + "%" : "None"], ["Market", A.m, B.m], ["Sector", esc(A.s), esc(B.s)]];
    $("cmp").innerHTML = `<div class="line total" style="border:0"><span></span><span>${esc(t)}</span><span>${esc(o)}</span></div>` +
      rowsFor.map(r => `<div class="line"><span class="sub">${r[0]}</span><span>${r[1]}</span><span>${r[2]}</span></div>`).join(""); };
  $("other").onchange = draw; draw();
}
function moneySheet(kind) {
  const dep = kind === "deposit";
  openSheet(`<h3>${dep ? "Add practice money" : "Withdraw practice money"}</h3>
    <span class="sub">This copies how real ${dep ? "deposits" : "withdrawals"} will work. No real money moves.</span>
    <label class="f" style="margin-top:12px">${dep ? "Pay with" : "Send to"}<select id="via"><option>MTN MoMo</option><option>Telecel Cash</option><option>AirtelTigo Money</option><option>Bank account</option></select></label>
    <label class="f">Amount (₵)<input id="ma" inputmode="decimal" value="${dep ? 500 : Math.min(500, Math.floor(S.cash))}"></label>
    <p class="err" id="err"></p><button class="btn block" id="go">${dep ? "Add" : "Withdraw"}</button>`);
  $("go").onclick = () => { const a = parseFloat($("ma").value) || 0;
    if (a <= 0) return ($("err").textContent = "Enter an amount.");
    if (!dep && a > S.cash) return ($("err").textContent = `You have ${money(S.cash)}.`);
    if (dep && a > 100000) return ($("err").textContent = "Practice deposits are limited to ₵100,000.");
    S.cash = round(S.cash + (dep ? a : -a)); log(`${dep ? "Added" : "Withdrew"} ₵${fmt(a)} ${dep ? "from" : "to"} ${$("via").value} (practice)`);
    save(); closeSheet(); toast(dep ? "Practice money added" : "Withdrawal done (practice)"); render(); };
}
function waitlistSheet() {
  openSheet(`<h3>Join the real-trading waitlist</h3><span class="sub">We'll message ${esc(S.user.phone)} when ADT Invest opens for real money.</span>
    <form id="wl" novalidate><input type="hidden" name="type" value="invest-waitlist"><input type="hidden" name="name" value="${esc(S.user.name)}">
      <label class="f" style="margin-top:12px">What would you invest in first?<select name="interest"><option>Ghana shares</option><option>US shares</option><option>Both</option></select></label>
      <label class="f">About how much a month?<select name="monthly"><option>Under ₵100</option><option>₵100–500</option><option>₵500–2,000</option><option>Over ₵2,000</option></select></label>
      <p class="err" id="err"></p><button class="btn block">Join</button></form>`);
  $("wl").onsubmit = async e => { e.preventDefault();
    try { const r = await adtSend(e.target, { phone: S.user.phone });
      if (r.notReady) { S.waitlist = Date.now(); save(); closeSheet(); return toast("You're on the list. We'll confirm by SMS soon."); }
      if (!r.ok) throw 0; S.waitlist = Date.now(); save(); closeSheet(); toast("You're on the waitlist!"); }
    catch (err) { $("err").textContent = "Couldn't send. Check your connection and try again."; } };
}

// ---------- routing ----------
function render() {
  if (!S) return welcome();
  $("tabs").hidden = false; updateCash();
  const h = location.hash || "#home", [route, arg] = h.slice(1).split("/");
  const titles = { home: `Hi, ${S.user.name}`, discover: "Discover", learn: "Learn", account: "Account" };
  let html;
  if (route === "stock") { html = stock(arg); $("title").textContent = STOCKS[arg] ? STOCKS[arg].n : "Company"; }
  else if (route === "lesson") { html = lesson(arg); const l = LESSONS.find(x => x.id === +arg); $("title").textContent = l ? l.title : "Lesson"; }
  else { const r = titles[route] ? route : "home"; html = { home, discover, learn, account }[r](); $("title").textContent = titles[r]; }
  $("back").hidden = !(route === "stock" || route === "lesson");
  document.querySelectorAll(".tabs a").forEach(a => a.classList.toggle("on", a.dataset.tab === (route === "stock" ? "discover" : route === "lesson" ? "learn" : route)));
  const scroll = window.scrollY; $("view").innerHTML = html; wire();
  if (render.last === h) window.scrollTo(0, scroll); else window.scrollTo(0, 0);
  render.last = h;
}
function wire() {
  const v = $("view");
  const q = $("q"); if (q) q.oninput = () => { disc.q = q.value; const pos = q.selectionStart; render(); const n = $("q"); n.focus(); n.setSelectionRange(pos, pos); };
  v.querySelectorAll("[data-market]").forEach(b => b.onclick = () => { disc.market = b.dataset.market; render(); });
  v.querySelectorAll("[data-theme]").forEach(b => b.onclick = () => { disc.theme = disc.theme === b.dataset.theme ? "" : b.dataset.theme; render(); });
  v.querySelectorAll("[data-range]").forEach(b => b.onclick = () => { range = +b.dataset.range; render(); });
  v.querySelectorAll("[data-watch]").forEach(b => b.onclick = () => { const t = b.dataset.watch;
    S.watch = S.watch.includes(t) ? S.watch.filter(x => x !== t) : [...S.watch, t]; save(); render(); });
  v.querySelectorAll("[data-cancel]").forEach(b => b.onclick = () => { const o = S.orders.find(x => String(x.id) === b.dataset.cancel);
    if (o && o.status === "open") { o.status = "cancelled"; if (o.side === "buy") S.cash = round(S.cash + o.ghs); log(`Cancelled limit ${o.side} ${o.t}`); save(); render(); } });
  v.querySelectorAll("[data-stoprec]").forEach(b => b.onclick = () => { S.recurring = S.recurring.filter(r => String(r.id) !== b.dataset.stoprec); save(); render(); });
  v.querySelectorAll("[data-delalert]").forEach(b => b.onclick = () => { S.alerts = S.alerts.filter(a => String(a.id) !== b.dataset.delalert); save(); render(); });
  v.querySelectorAll("[data-act]").forEach(b => b.onclick = () => {
    const t = b.dataset.t, a = b.dataset.act;
    if (a === "buy") buySheet(t); else if (a === "sell") sellSheet(t); else if (a === "alert") alertSheet(t);
    else if (a === "recurring") recurringSheet(t); else if (a === "compare") compareSheet(t);
    else if (a === "deposit" || a === "withdraw") moneySheet(a); else if (a === "waitlist") waitlistSheet();
    else if (a === "share") { const url = location.origin + location.pathname + "?ref=" + S.user.ref, text = "Practise buying Ghana and US shares from ₵20 on ADT Invest";
      if (navigator.share) navigator.share({ title: "ADT Invest", text, url }).catch(() => {});
      else { try { navigator.clipboard.writeText(`${text}: ${url}`); toast("Invite link copied"); } catch (e) { toast(url); } } }
    else if (a === "reset" && confirmReset()) { S = fresh(S.user.name, S.user.phone); save(); toast("Practice account reset"); render(); }
  });
  const quiz = $("quiz");
  if (quiz) { const id = +location.hash.split("/")[1], l = LESSONS.find(x => x.id === id), picked = {};
    quiz.querySelectorAll("button[data-q]").forEach(b => b.onclick = () => { const qi = +b.dataset.q; if (picked[qi] != null) return;
      picked[qi] = +b.dataset.o; const ok = picked[qi] === l.quiz[qi][2];
      b.classList.add(ok ? "right" : "wrong");
      if (!ok) quiz.querySelector(`button[data-q="${qi}"][data-o="${l.quiz[qi][2]}"]`).classList.add("right");
      if (Object.keys(picked).length === l.quiz.length) { const score = l.quiz.filter((q, i) => picked[i] === q[2]).length;
        S.lessons[id] = score; save(); $("score").textContent = `You got ${score} of ${l.quiz.length}.`; } }); }
}
let resetArmed = 0;
function confirmReset() { if (Date.now() - resetArmed < 4000) return true; resetArmed = Date.now(); toast("Tap reset again to confirm"); return false; }

window.addEventListener("hashchange", () => { closeSheet(); render(); });
if (S) { runRecurring(); fillLimits(); save(); }
render();
setInterval(() => {
  if (document.hidden) return;
  tick();
  const typing = document.activeElement && /INPUT|SELECT|TEXTAREA/.test(document.activeElement.tagName);
  const inLesson = (location.hash || "").startsWith("#lesson");
  if ($("sheet").hidden && !typing && !inLesson && S) render();
}, 5000);
window.ADT_INVEST = { get state() { return S; }, buy, sell, tick, render, price };
})();
