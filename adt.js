// Shared settings and helpers for ADT Work pages.

// Where claim and delivery forms are sent. Create a free form at https://formspree.io
// (or any service that accepts a POST) and paste its endpoint here, e.g.
// "https://formspree.io/f/abcdwxyz". Until it is set, the forms say claims open soon.
const ADT_FORM_ENDPOINT = "";

// African country calling codes. Sign-up requires one of these.
const AFRICAN_CODES = [
  ["+234", "Nigeria"], ["+233", "Ghana"], ["+254", "Kenya"], ["+27", "South Africa"], ["+20", "Egypt"],
  ["+251", "Ethiopia"], ["+255", "Tanzania"], ["+256", "Uganda"], ["+250", "Rwanda"], ["+212", "Morocco"],
  ["+213", "Algeria"], ["+216", "Tunisia"], ["+218", "Libya"], ["+221", "Senegal"], ["+225", "Côte d'Ivoire"],
  ["+237", "Cameroon"], ["+243", "DR Congo"], ["+242", "Republic of the Congo"], ["+244", "Angola"],
  ["+258", "Mozambique"], ["+260", "Zambia"], ["+263", "Zimbabwe"], ["+265", "Malawi"], ["+267", "Botswana"],
  ["+264", "Namibia"], ["+266", "Lesotho"], ["+268", "Eswatini"], ["+261", "Madagascar"], ["+230", "Mauritius"],
  ["+248", "Seychelles"], ["+269", "Comoros"], ["+252", "Somalia"], ["+253", "Djibouti"], ["+291", "Eritrea"],
  ["+249", "Sudan"], ["+211", "South Sudan"], ["+257", "Burundi"], ["+235", "Chad"], ["+236", "Central African Republic"],
  ["+241", "Gabon"], ["+240", "Equatorial Guinea"], ["+239", "São Tomé and Príncipe"], ["+238", "Cabo Verde"],
  ["+220", "The Gambia"], ["+222", "Mauritania"], ["+223", "Mali"], ["+224", "Guinea"], ["+245", "Guinea-Bissau"],
  ["+226", "Burkina Faso"], ["+227", "Niger"], ["+228", "Togo"], ["+229", "Benin"], ["+231", "Liberia"],
  ["+232", "Sierra Leone"], ["+262", "Réunion / Mayotte"]
];

function adtPhoneSelect(select) {
  const sorted = [...AFRICAN_CODES].sort((a, b) => a[1].localeCompare(b[1]));
  select.innerHTML = '<option value="">Country</option>' +
    sorted.map(([code, name]) => `<option value="${code}">${name} (${code})</option>`).join("");
}

// Returns the full number in +XXX format if valid, or null.
function adtValidPhone(code, local) {
  if (!AFRICAN_CODES.some(([c]) => c === code)) return null;
  const digits = String(local || "").replace(/[\s\-().]/g, "").replace(/^0+/, "");
  if (!/^\d{6,11}$/.test(digits)) return null;
  return code + digits;
}

async function adtLoadTasks() {
  const res = await fetch("tasks.json", { cache: "no-cache" });
  if (!res.ok) throw new Error("tasks.json " + res.status);
  return (await res.json()).tasks;
}

function adtEsc(s) {
  return String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

// Minimal **bold** and `code` formatting for task text.
function adtFmt(s) {
  return adtEsc(s).replace(/\*\*(.+?)\*\*/g, "<b>$1</b>").replace(/`(.+?)`/g, "<code>$1</code>");
}

async function adtSend(form, extra) {
  const data = Object.fromEntries(new FormData(form).entries());
  Object.assign(data, extra || {});
  if (!ADT_FORM_ENDPOINT) return { ok: false, notReady: true };
  const res = await fetch(ADT_FORM_ENDPOINT, {
    method: "POST", headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify(data)
  });
  return { ok: res.ok };
}
