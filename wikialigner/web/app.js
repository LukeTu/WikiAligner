import { getLanguage, pick, setLanguage, t, tv } from "./i18n.js";

// ====================================================================== helpers
const $ = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];

function el(tag, attrs = {}, ...children) {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (v === undefined || v === null || v === false) continue;
    if (k === "class") node.className = v;
    else if (k === "dataset") Object.assign(node.dataset, v);
    else if (k.startsWith("on")) node.addEventListener(k.slice(2), v);
    else if (k === "text") node.textContent = v;
    else node.setAttribute(k, v === true ? "" : v);
  }
  for (const c of children.flat()) if (c !== null && c !== undefined && c !== false) node.append(c);
  return node;
}

const api = {
  async request(method, path, body) {
    let res;
    try {
      res = await fetch(path, {
        method,
        headers: body ? { "Content-Type": "application/json" } : {},
        body: body ? JSON.stringify(body) : undefined,
      });
    } catch {
      // The browser only says "Failed to fetch": the local WikiAligner server is not running.
      throw new Error(t("e.offline"));
    }
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(typeof data.detail === "string" ? data.detail : `HTTP ${res.status}`);
    return data;
  },
  get(path, params) {
    const q = params ? "?" + new URLSearchParams(Object.entries(params).filter(([, v]) => v !== "" && v != null)) : "";
    return this.request("GET", path + q);
  },
  post(path, body = {}) { return this.request("POST", path, body); },
  del(path) { return this.request("DELETE", path); },
};

function debounce(fn, ms) {
  let h;
  return (...args) => { clearTimeout(h); h = setTimeout(() => fn(...args), ms); };
}

let toastTimer;
function toast(message, { error = false, action = null, ms = 5000 } = {}) {
  const box = $("#toast");
  box.replaceChildren(el("span", { text: message }));
  if (action) box.append(el("button", { text: action.label, onclick: () => { action.run(); box.hidden = true; } }));
  box.classList.toggle("error", error);
  box.hidden = false;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { box.hidden = true; }, ms);
}

function openExternal(url) { api.post("/api/open_url", { url }).catch((e) => toast(e.message, { error: true })); }

document.addEventListener("click", (e) => {
  const a = e.target.closest("a.ext");
  if (a) { e.preventDefault(); openExternal(a.href); }
});

const RTL = new Set(["ar", "arz", "he", "fa", "ur", "yi", "ps", "ckb", "dv", "sd", "ug", "azb", "mzn", "pnb"]);
const LANGS = [
  ["en", "English"], ["zh", "中文"], ["ru", "Русский"], ["de", "Deutsch"], ["fr", "Français"], ["es", "Español"],
  ["ja", "日本語"], ["it", "Italiano"], ["pt", "Português"], ["ar", "العربية"], ["fa", "فارسی"], ["uk", "Українська"],
  ["pl", "Polski"], ["nl", "Nederlands"], ["ko", "한국어"], ["tr", "Türkçe"], ["sv", "Svenska"], ["vi", "Tiếng Việt"],
  ["id", "Bahasa Indonesia"], ["he", "עברית"], ["cs", "Čeština"], ["hu", "Magyar"], ["fi", "Suomi"], ["el", "Ελληνικά"],
  ["ro", "Română"], ["th", "ไทย"], ["hi", "हिन्दी"], ["bn", "বাংলা"], ["ms", "Bahasa Melayu"], ["ca", "Català"],
  ["da", "Dansk"], ["no", "Norsk bokmål"], ["bg", "Български"], ["sr", "Српски"], ["hr", "Hrvatski"], ["sk", "Slovenčina"],
  ["lt", "Lietuvių"], ["lv", "Latviešu"], ["et", "Eesti"], ["sl", "Slovenščina"], ["ka", "ქართული"], ["hy", "Հայերեն"],
  ["kk", "Қазақша"], ["az", "Azərbaycanca"], ["ta", "தமிழ்"], ["ur", "اردو"], ["zh-yue", "粵語"], ["zh-classical", "文言"],
  ["wuu", "吴语"], ["my", "မြန်မာ"], ["km", "ខ្មែរ"], ["lo", "ລາວ"], ["tl", "Tagalog"], ["sw", "Kiswahili"],
];

function fmtDate(ts) { return ts ? ts.replace("T", " ").replace("Z", "").slice(0, 16) : ""; }
function pct(x) { return Math.round((x || 0) * 1000) / 10; }

function progressText(p) {
  if (!p) return t("p.queued");
  let prefix = "";
  if (p.startsWith("left ")) { prefix = t("p.left"); p = p.slice(5); }
  else if (p.startsWith("right ")) { prefix = t("p.right"); p = p.slice(6); }
  const [key, a, b] = p.split(" ");
  if (key === "list_revisions" && a) return prefix + t("p.list_revisions_n", { n: a });
  if (key === "probe") return prefix + t("p.probe", { n: a, date: b });
  if (key === "encode") return prefix + t("p.embed");
  return prefix + t("p." + key);
}

async function pollJob(job, onProgress) {
  while (true) {
    const j = await api.get(`/api/jobs/${job.id}`);
    if (j.status === "done") return j.result;
    if (j.status === "error") throw new Error(j.error);
    onProgress?.(j.progress);
    await new Promise((r) => setTimeout(r, 400));
  }
}

function attachSuggest(input, box, langOf, onPick) {
  let items = [], active = -1;
  const render = () => {
    box.replaceChildren(...items.map((title, i) => el("button", {
      type: "button", text: title, class: i === active ? "active" : "",
      onmousedown: (e) => { e.preventDefault(); pick(title); },
    })));
    box.hidden = items.length === 0;
  };
  const pick = (title) => { input.value = title; items = []; render(); onPick(title); };
  const fetchSuggestions = debounce(async () => {
    const q = input.value.trim();
    if (!q) { items = []; render(); return; }
    try { items = (await api.get("/api/search", { lang: langOf(), q })).titles; }
    catch (e) { items = []; toast(e.message, { error: true }); }
    active = -1;
    if (document.activeElement === input) render();
  }, 250);
  input.addEventListener("input", fetchSuggestions);
  input.addEventListener("blur", () => setTimeout(() => { box.hidden = true; }, 100));
  input.addEventListener("keydown", (e) => {
    if (box.hidden) { if (e.key === "Enter") onPick(input.value.trim()); return; }
    if (e.key === "ArrowDown") { active = Math.min(active + 1, items.length - 1); render(); e.preventDefault(); }
    else if (e.key === "ArrowUp") { active = Math.max(active - 1, 0); render(); e.preventDefault(); }
    else if (e.key === "Enter") { if (active >= 0) pick(items[active]); else { box.hidden = true; onPick(input.value.trim()); } e.preventDefault(); }
    else if (e.key === "Escape") { box.hidden = true; }
  });
}

// ====================================================================== source cards
class SourceCard {
  constructor(root, side) {
    this.root = root;
    this.side = side;
    this.info = null;
    root.append($("#source-card").content.cloneNode(true));
    this.q = (s) => $(s, root);
    this.type = "wiki";
    this.mode = "latest";
    this.q(".lang-input").value = side === "left" ? "en" : "zh";
    this.q(".text-lang").value = side === "left" ? "en" : "zh";

    $$(".card-head .seg button", root).forEach((b) => b.addEventListener("click", () => this.setType(b.dataset.type)));
    $$(".rev-mode button", root).forEach((b) => b.addEventListener("click", () => this.setMode(b.dataset.mode)));
    const reload = debounce(() => this.loadInfo(), 500);
    this.q(".lang-input").addEventListener("change", () => { this.onLangChange(); reload(); });
    attachSuggest(this.q(".title-input"), this.q(".suggest"), () => this.lang, () => this.loadInfo());
    this.q(".title-input").addEventListener("change", reload);
    this.q(".langlinks").addEventListener("change", (e) => {
      const [lang, ...rest] = e.target.value.split("|");
      if (!lang) return;
      this.other.set({ type: "wiki", lang, title: rest.join("|") });
      e.target.value = "";
    });
    this.q(".open-file").addEventListener("click", () => this.q(".file-input").click());
    this.q(".file-input").addEventListener("change", (e) => this.readFile(e.target.files[0]));
    this.relabel();
  }

  get lang() { return this.q(".lang-input").value.trim().toLowerCase(); }

  relabel() {
    const revisionMode = cards.left && cards.right && cards.left.lang === cards.right.lang && cards.left.type === "wiki" && cards.right.type === "wiki";
    const key = revisionMode ? (this.side === "left" ? "side.old" : "side.new") : (this.side === "left" ? "side.left" : "side.right");
    this.q(".side-label").textContent = t(key);
  }

  setType(type) {
    this.type = type;
    $$(".card-head .seg button", this.root).forEach((b) => b.classList.toggle("on", b.dataset.type === type));
    this.q(".src-wiki").hidden = type !== "wiki";
    this.q(".src-text").hidden = type !== "text";
    relabelCards();
  }

  setMode(mode) {
    this.mode = mode;
    $$(".rev-mode button", this.root).forEach((b) => b.classList.toggle("on", b.dataset.mode === mode));
    this.q(".rev-date").hidden = mode !== "date";
    this.q(".rev-id").hidden = mode !== "revid";
  }

  onLangChange() {
    relabelCards();
    const other = this.other;
    if (this.type === "wiki" && other.info) {
      const link = other.info.langlinks.find((l) => l.lang === this.lang);
      if (link) this.q(".title-input").value = link.title;
      else if (this.lang === other.info.lang) this.q(".title-input").value = other.info.title;
    }
  }

  get other() { return this.side === "left" ? cards.right : cards.left; }

  async loadInfo() {
    const title = this.q(".title-input").value.trim();
    const meta = this.q(".page-meta");
    meta.classList.remove("error");
    if (!title || !this.lang) { meta.textContent = ""; this.info = null; return; }
    try {
      const info = await api.get("/api/page", { lang: this.lang, title });
      this.info = info;
      if (info.title !== title) this.q(".title-input").value = info.title;
      meta.replaceChildren(
        el("a", { class: "ext", href: `https://${info.lang}.wikipedia.org/wiki/${encodeURIComponent(info.title)}`, text: info.title }),
        ` · ${info.qid || ""} · ${t("meta.langs", { n: info.langlinks.length + 1 })}`);
      const vrow = this.q(".variant-row"), vsel = this.q(".variant");
      vrow.hidden = info.variants.length === 0;
      const keep = vsel.value;
      vsel.replaceChildren(el("option", { value: "", text: t("var.orig") }),
        ...info.variants.map((v) => el("option", { value: v, text: `${t("var." + v)} (${v})` })));
      vsel.value = info.variants.includes(keep) ? keep : (info.lang === "zh" ? "zh-hans" : "");
      const links = this.q(".langlinks");
      const target = tv(this.side === "left" ? "side.right" : "side.left");
      links.replaceChildren(el("option", { value: "", text: t("links.choose", { n: info.langlinks.length, side: target }) }),
        ...info.langlinks.map((l) => el("option", { value: `${l.lang}|${l.title}`, text: `${l.lang} · ${l.autonym || ""} · ${l.title}` })));
      this.q(".links-row").hidden = info.langlinks.length === 0;
      if (this.other.type === "wiki" && !this.other.q(".title-input").value.trim()) this.other.onLangChange();
    } catch (e) {
      this.info = null;
      meta.textContent = e.message;
      meta.classList.add("error");
    }
  }

  async readFile(file) {
    if (!file) return;
    const buf = await file.arrayBuffer();
    let bin = "";
    const bytes = new Uint8Array(buf);
    for (let i = 0; i < bytes.length; i += 0x8000) bin += String.fromCharCode(...bytes.subarray(i, i + 0x8000));
    try {
      const { text } = await api.post("/api/read_file", { name: file.name, data: btoa(bin) });
      this.q(".text-body").value = text;
      if (!this.q(".text-name").value) this.q(".text-name").value = file.name;
    } catch (e) { toast(e.message, { error: true }); }
  }

  spec() {
    if (this.type === "text") {
      return { type: "text", lang: this.q(".text-lang").value.trim().toLowerCase(),
               text: this.q(".text-body").value, name: this.q(".text-name").value.trim() };
    }
    const s = { type: "wiki", lang: this.lang, title: this.q(".title-input").value.trim(),
                variant: this.q(".variant-row").hidden ? null : this.q(".variant").value || null };
    if (this.mode === "date" && this.q(".rev-date").value) s.date = this.q(".rev-date").value;
    if (this.mode === "revid" && this.q(".rev-id").value) s.revid = Number(this.q(".rev-id").value);
    return s;
  }

  validate() {
    const s = this.spec(), side = tv(this.side === "left" ? "side.left" : "side.right");
    if (s.type === "text" && !s.text.trim()) return t("e.noText", { side });
    if (s.type === "wiki" && !s.title && !s.revid) return t("e.noTitle", { side });
    return null;
  }

  set(s) {
    this.setType(s.type || "wiki");
    if (s.type === "text") {
      this.q(".text-lang").value = s.lang || "";
      this.q(".text-body").value = s.text || "";
      this.q(".text-name").value = s.name || "";
      return;
    }
    this.q(".lang-input").value = s.lang || "";
    this.q(".title-input").value = s.title || "";
    if (s.revid) { this.setMode("revid"); this.q(".rev-id").value = s.revid; }
    else if (s.date) { this.setMode("date"); this.q(".rev-date").value = s.date; }
    else this.setMode("latest");
    relabelCards();
    this.loadInfo();
  }
}

const cards = {};
function relabelCards() { cards.left?.relabel(); cards.right?.relabel(); }

// ====================================================================== alignment run
function readOptions() {
  return {
    model: $("#opt-model").value || MODELS.default,
    granularity: $("#opt-granularity").value,
    strategy: $("#opt-strategy").value,
    k: Number($("#opt-k").value) || 4,
    min_margin: Number($("#opt-margin").value) || 1.0,
    include_captions: $("#opt-captions").checked,
    include_lists: $("#opt-lists").checked,
    include_tables: $("#opt-tables").checked,
    include_infobox: $("#opt-infobox").checked,
    align_headings: $("#opt-headings").checked,
  };
}

async function runAlignment() {
  for (const c of [cards.left, cards.right]) {
    const err = c.validate();
    if (err) { toast(err, { error: true }); return; }
  }
  const btn = $("#run"), prog = $("#run-progress");
  btn.disabled = true;
  prog.hidden = false;
  prog.classList.remove("error");
  const show = (msg) => prog.replaceChildren(el("span", { class: "spinner" }), el("span", { text: msg }));
  show(t("p.queued"));
  try {
    const job = await api.post("/api/align", { left: cards.left.spec(), right: cards.right.spec(), options: readOptions() });
    const result = await pollJob(job, (p) => show(progressText(p)));
    prog.hidden = true;
    renderResult(result);
  } catch (e) {
    prog.replaceChildren(el("span", { text: t("e.failed", { msg: e.message }) }));
    prog.classList.add("error");
  } finally {
    btn.disabled = false;
  }
}

// ====================================================================== result view
const R = { result: null, bySrc: new Map(), byTgt: new Map(), unSrc: new Map(), unTgt: new Map(), selected: null };

function scoreOf(p) {
  if (p.kind === "identical") return Infinity;
  return $("#flt-score").value === "margin" ? (p.margin ?? 0) : p.cos;
}
function pairVisible(p) { return scoreOf(p) >= Number($("#flt-threshold").value); }
function pairsFor(side, id) { return (side === "left" ? R.bySrc : R.byTgt).get(id) || []; }
function docOf(side) { return side === "left" ? R.result.left : R.result.right; }
const isRevisionMode = () => R.result?.mode === "revision";

function renderResult(result) {
  R.result = result;
  R.bySrc = new Map(); R.byTgt = new Map();
  result.pairs.forEach((p) => {
    (R.bySrc.get(p.src) || R.bySrc.set(p.src, []).get(p.src)).push(p);
    (R.byTgt.get(p.tgt) || R.byTgt.set(p.tgt, []).get(p.tgt)).push(p);
  });
  R.unSrc = new Map(result.unmatched_src.map((u) => [u.id, u]));
  R.unTgt = new Map(result.unmatched_tgt.map((u) => [u.id, u]));
  R.selected = null;
  $("#empty").hidden = true;
  $("#result").hidden = false;
  $("#result").classList.toggle("mode-revision", isRevisionMode());
  $("#drawer").hidden = true;
  applyRecommendedThreshold();
  for (const side of ["left", "right"]) { renderHead(side); renderBody(side); }
  applyFilter();
  showView("align");
}

function setScoreMode(mode, keepValue) {
  const slider = $("#flt-threshold");
  $("#flt-score").value = mode;
  if (mode === "margin") { slider.min = 0.9; slider.max = 1.8; slider.step = 0.005; if (!keepValue || Number(slider.value) < 0.9) slider.value = 1.1; }
  else { slider.min = 0; slider.max = 1; slider.step = 0.01; if (!keepValue || Number(slider.value) > 1) slider.value = 0.7; }
  $("#flt-value").textContent = fmtThreshold();
}

function fmtThreshold() {
  return Number($("#flt-threshold").value).toFixed($("#flt-score").value === "margin" ? 3 : 2);
}

// Threshold the local benchmark recommends for the model behind the current result.
function recommendedThreshold() {
  const m = MODELS.list.find((x) => x.model_id === R.result?.model.id);
  return m?.benchmark?.recommended_threshold ?? null;
}

function applyRecommendedThreshold() {
  const th = recommendedThreshold();
  if (th == null) { setScoreMode("cos", false); }
  else { setScoreMode("margin", true); $("#flt-threshold").value = th; }
  $("#flt-value").textContent = fmtThreshold();
}

function updateResetButton() {
  const th = recommendedThreshold();
  $("#flt-reset").hidden = th == null ||
    ($("#flt-score").value === "margin" && Math.abs(Number($("#flt-threshold").value) - th) < 1e-6);
}

function docLabel(doc) {
  const rev = doc.revision;
  const parts = [el("strong", { text: doc.title }), el("span", { class: "chip", text: doc.lang })];
  if (rev) {
    parts.push(el("a", { class: "ext", href: doc.url, text: `rev ${rev.revid}` }), el("span", { class: "muted", text: fmtDate(rev.timestamp) }));
    if (rev.user) parts.push(el("span", { class: "muted", text: rev.user }));
  }
  if (doc.variant) parts.push(el("span", { class: "chip", text: doc.variant }));
  return parts;
}

function renderHead(side) { $(`#head-${side}`).replaceChildren(...docLabel(docOf(side))); }

function renderBody(side) {
  const doc = docOf(side), body = $(`#body-${side}`);
  body.dir = RTL.has(doc.lang) ? "rtl" : "auto";
  body.lang = doc.lang;
  const frag = document.createDocumentFragment();
  let blockEl = null, blockIdx = -1;
  for (const s of doc.segments) {
    if (s.block !== blockIdx) {
      blockIdx = s.block;
      const level = s.kind === "heading" ? ` h${Math.min(5, Math.max(2, (s.section.split(" / ").filter(Boolean).length) + 2))}` : "";
      blockEl = el(s.kind === "heading" ? "h4" : "div", { class: `blk ${s.kind}${level}` });
      frag.append(blockEl);
    }
    const span = el("span", { class: "seg-s" + (s.alignable ? "" : " inert"), dataset: { id: s.id, side } }, s.text);
    blockEl.append(span, " ");
  }
  body.replaceChildren(frag);
  body.scrollTop = 0;
}

function applyFilter() {
  if (!R.result) return;
  $("#flt-value").textContent = fmtThreshold();
  const onlyUnmatched = $("#flt-unmatched").checked, showIds = $("#flt-ids").checked;
  const scoreMode = $("#flt-score").value;
  let visibleCount = 0;
  R.result.pairs.forEach((p) => { if (pairVisible(p)) visibleCount++; });
  for (const side of ["left", "right"]) {
    const doc = docOf(side);
    for (const span of $$(".seg-s", $(`#body-${side}`))) {
      const id = Number(span.dataset.id), seg = doc.segments[id];
      span.classList.remove("matched", "identical", "modified", "unmatched", "dim");
      span.style.removeProperty("--a");
      span.querySelector(".sid")?.remove();
      if (!seg.alignable) continue;
      const vis = pairsFor(side, id).filter(pairVisible);
      if (vis.length) {
        const best = vis.reduce((a, b) => (scoreOf(b) > scoreOf(a) ? b : a));
        if (isRevisionMode()) span.classList.add(best.kind === "identical" ? "identical" : "modified");
        else {
          span.classList.add("matched");
          const x = scoreMode === "margin" ? (best.margin - 1) / 0.5 : (best.cos - 0.5) / 0.5;
          span.style.setProperty("--a", (0.08 + 0.3 * Math.min(1, Math.max(0, x))).toFixed(3));
        }
        if (onlyUnmatched) span.classList.add("dim");
        if (showIds) span.prepend(el("span", { class: "sid", text: vis.map((p) => (side === "left" ? p.tgt : p.src)).join(",") + "→" }));
      } else {
        span.classList.add("unmatched");
      }
      if (showIds) span.append(el("span", { class: "sid", text: `#${id}` }));
    }
  }
  renderStats(visibleCount);
  renderLegend();
  updateResetButton();
}

function renderStats(visibleCount) {
  const r = R.result, s = r.stats;
  const left = tv(isRevisionMode() ? "side.old" : "side.left"), right = tv(isRevisionMode() ? "side.new" : "side.right");
  $("#stats").replaceChildren(...[
    el("span", { class: "chip accent", text: t("mode." + r.mode) }),
    el("span", { class: "chip", text: t("stat.pairs", { n: s.pairs }) }),
    el("span", { class: "chip", text: t("stat.visible", { n: visibleCount }) }),
    isRevisionMode() ? el("span", { class: "chip", text: t("stat.identical", { n: s.identical }) }) : null,
    el("span", { class: "chip", text: t("stat.coverage", { side: left, p: pct(s.coverage_src) }) }),
    el("span", { class: "chip", text: t("stat.coverage", { side: right, p: pct(s.coverage_tgt) }) }),
    el("span", { class: "chip", text: r.model.id.split("/").pop() }),
    el("span", { class: "chip", text: t("stat.seconds", { s: s.seconds }) }),
  ].filter(Boolean));
}

function renderLegend() {
  const sw = (bg, label, extra = "") => el("span", {}, el("i", { style: `background:${bg};${extra}` }), label);
  $("#legend").replaceChildren(...(isRevisionMode()
    ? [sw("var(--identical)", t("legend.identical")), sw("var(--modified)", t("legend.modified")),
       sw("var(--removed)", t("legend.removed")), sw("var(--added)", t("legend.added"))]
    : [sw("rgba(var(--pair), .32)", t("legend.matched")),
       sw("transparent", t("legend.unmatched"), "border-bottom:2px dashed var(--unmatched-line);height:6px;border-radius:0")]));
}

function counterpartSpans(side, id) {
  const other = side === "left" ? "right" : "left";
  return pairsFor(side, id).filter(pairVisible)
    .map((p) => $(`#body-${other} .seg-s[data-id="${side === "left" ? p.tgt : p.src}"]`)).filter(Boolean);
}

function onSegHover(e) {
  const span = e.target.closest(".seg-s");
  $$(".seg-s.hl").forEach((s) => s.classList.remove("hl"));
  if (!span || span.classList.contains("inert")) return;
  const side = span.dataset.side, id = Number(span.dataset.id);
  const partners = counterpartSpans(side, id);
  if (partners.length) { span.classList.add("hl"); partners.forEach((s) => s.classList.add("hl")); }
}

function selectSegment(side, id, scroll = true) {
  $$(".seg-s.sel").forEach((s) => s.classList.remove("sel"));
  const span = $(`#body-${side} .seg-s[data-id="${id}"]`);
  if (!span) return;
  span.classList.add("sel");
  const partners = counterpartSpans(side, id);
  partners.forEach((s) => s.classList.add("sel"));
  if (scroll) {
    span.scrollIntoView({ block: "nearest", behavior: "smooth" });
    partners[0]?.scrollIntoView({ block: "center", behavior: "smooth" });
  }
  R.selected = { side, id };
  renderDrawer(side, id);
}

function onSegClick(e) {
  const span = e.target.closest(".seg-s");
  if (!span || span.classList.contains("inert")) return;
  selectSegment(span.dataset.side, Number(span.dataset.id));
}

// ---------------------------------------------------------------------- drawer
function baseLang(lang) {
  if (lang.startsWith("zh") || ["wuu", "gan", "lzh"].includes(lang)) return "zh";
  return lang.split("-")[0];
}

function translateLinks(text, from, to) {
  const f = baseLang(from), tl = baseLang(to), q = encodeURIComponent(text);
  const services = [
    ["Bing", `https://www.bing.com/translator?from=${f === "zh" ? "zh-Hans" : f}&to=${tl === "zh" ? "zh-Hans" : tl}&text=${q}`],
    ["DeepL", `https://www.deepl.com/translator#${f}/${tl}/${q}`],
    ["Google", `https://translate.google.com/?sl=${f}&tl=${tl}&text=${q}&op=translate`],
  ];
  return services.map(([svc, url]) => el("a", { class: "ext", href: url, text: t("btn.translate", { svc }) }));
}

function sideBox(side, id, extra = []) {
  const doc = docOf(side), seg = doc.segments[id];
  return el("div", { class: "side", dir: RTL.has(doc.lang) ? "rtl" : "auto", lang: doc.lang },
    el("div", { class: "meta" }, el("span", { text: `${doc.lang} #${id}` }), seg.section ? el("span", { text: seg.section }) : null, ...extra),
    el("div", { text: seg.text }));
}

function renderDrawer(side, id) {
  const drawer = $("#drawer"), r = R.result;
  const other = side === "left" ? "right" : "left";
  const doc = docOf(side), otherDoc = docOf(other);
  const pairs = pairsFor(side, id);
  const visible = pairs.filter(pairVisible);
  const content = [];
  const close = el("button", { class: "ghost small", text: t("btn.close"), onclick: () => { drawer.hidden = true; $$(".seg-s.sel").forEach((s) => s.classList.remove("sel")); } });

  if (visible.length || pairs.length) {
    content.push(el("div", { class: "drawer-head" }, el("h3", { text: t("d.pair") + (visible.length ? "" : ` — ${t("d.reason.threshold")}`) }), close));
    for (const p of (visible.length ? visible : pairs)) {
      const scores = p.kind === "identical" ? t("d.identical")
        : t("d.scores", { cos: p.cos.toFixed(3), margin: (p.margin ?? 0).toFixed(3) });
      const ratio = p.char_ratio != null && p.kind !== "identical" ? " · " + t("d.charRatio", { r: p.char_ratio }) : "";
      content.push(el("div", { class: "muted", text: scores + ratio }));
      content.push(el("div", { class: "pair-view" }, sideBox("left", p.src), sideBox("right", p.tgt)));
      content.push(traceActions(p.src, p.tgt));
    }
  } else {
    const info = (side === "left" ? R.unSrc : R.unTgt).get(id);
    content.push(el("div", { class: "drawer-head" }, el("h3", { text: t("d.unmatched") }), close));
    content.push(el("div", { class: "pair-view" }, sideBox(side, id), info && info.best != null
      ? el("div", { class: "side" },
          el("div", { class: "meta" }, el("span", { text: `${t("d.best")}: ${otherDoc.lang} #${info.best}` }),
            el("span", { text: `margin ${info.margin}` })),
          el("div", { text: otherDoc.segments[info.best].text }),
          el("button", { class: "link", text: "→", onclick: () => selectSegment(other, info.best) }))
      : el("div")));
    if (info) content.push(el("div", { class: "muted", text: t("d.reason." + info.reason) }));
    content.push(traceActions(side === "left" ? id : null, side === "right" ? id : null));
  }
  drawer.replaceChildren(...content);
  drawer.hidden = false;
}

function traceActions(srcId, tgtId) {
  const r = R.result, box = el("div", { class: "actions" });
  const leftWiki = r.left.source === "wiki", rightWiki = r.right.source === "wiki";
  const fuzzy = el("input", { type: "checkbox" });
  const traceTarget = el("div");
  const req = (side, id) => {
    const doc = docOf(side);
    return { lang: doc.lang, title: doc.title, revid: doc.revision.revid, text: doc.segments[id].text,
             variant: doc.variant, fuzzy: fuzzy.checked ? 0.85 : null };
  };
  if (srcId != null && tgtId != null && leftWiki && rightWiki) {
    box.append(el("button", { class: "primary small", text: t("btn.trace"),
      onclick: () => runTrace("/api/trace_pair", { left: req("left", srcId), right: req("right", tgtId) }, traceTarget) }));
  } else {
    const side = srcId != null ? "left" : "right", id = srcId ?? tgtId;
    if (docOf(side).source === "wiki") box.append(el("button", { class: "primary small", text: t("btn.traceOne"),
      onclick: () => runTrace("/api/trace", req(side, id), traceTarget, side) }));
  }
  if (box.children.length) box.append(el("label", { class: "check" }, fuzzy, t("btn.fuzzy")));
  const src = srcId ?? tgtId, from = srcId != null ? r.left.lang : r.right.lang, to = srcId != null ? r.right.lang : r.left.lang;
  if (r.left.lang !== r.right.lang) box.append(...translateLinks(docOf(srcId != null ? "left" : "right").segments[src].text, from, to));
  return el("div", { class: "actions-wrap" }, box, traceTarget);
}

async function runTrace(path, body, target, singleSide) {
  target.replaceChildren(el("div", { class: "trace-box" }, el("span", {}, el("span", { class: "spinner" }), " ", t("t.running"))));
  const status = target.querySelector(".trace-box > span");
  try {
    const job = await api.post(path, body);
    const res = await pollJob(job, (p) => { status.replaceChildren(el("span", { class: "spinner" }), " ", progressText(p)); });
    target.replaceChildren(singleSide ? traceBox({ [singleSide]: res }) : traceBox(res));
  } catch (e) {
    target.replaceChildren(el("div", { class: "trace-box", text: t("e.failed", { msg: e.message }) }));
  }
}

function traceCard(tr) {
  const rev = tr.revision;
  return el("div", {},
    el("div", { class: "verdict", text: t("t.first", { date: fmtDate(rev.timestamp) }) }),
    el("div", { class: "muted" }, `${tr.lang} · rev ${rev.revid} · ${t("t.by", { user: rev.user })}`,
      tr.is_page_creation ? ` · ${t("t.creation")}` : "", " ",
      tr.content_translation ? el("span", { class: "tag ct", text: t("t.ct") }) : null),
    rev.comment ? el("div", { class: "muted", text: `“${rev.comment}”` }) : null,
    el("div", { class: "actions" },
      el("a", { class: "ext", href: tr.url, text: t("btn.viewRev") }),
      el("a", { class: "ext", href: tr.diff_url, text: t("btn.diff") }),
      el("span", { class: "muted", text: t("t.searched", { n: tr.revisions_searched, f: tr.fetches }) })));
}

function duration(a, b) {
  const ms = Math.abs(new Date(a) - new Date(b));
  if (ms >= 86400000) return t("t.days", { n: Math.round(ms / 86400000) });
  if (ms >= 3600000) return t("t.hours", { n: Math.round(ms / 3600000) });
  return t("t.minutes", { n: Math.max(1, Math.round(ms / 60000)) });
}

function traceBox(res) {
  const parts = [];
  if (res.left && res.right) {
    const c = res.comparison;
    const sideName = c.earlier === "left" ? `${res.left.lang}` : `${res.right.lang}`;
    parts.push(el("div", { class: "verdict", text: c.earlier
      ? t("t.earlier", { side: sideName, d: duration(c.left_timestamp, c.right_timestamp) }) : t("t.same") }));
  }
  parts.push(el("div", { class: "trace-grid" }, res.left ? traceCard(res.left) : el("div"), res.right ? traceCard(res.right) : el("div")));
  parts.push(el("div", { class: "muted", text: t("t.caveat") }));
  return el("div", { class: "trace-box" }, ...parts);
}

// ---------------------------------------------------------------------- export
async function exportResult(fmt) {
  $("#export-menu").hidden = true;
  if (!R.result) return;
  try {
    const { path } = await api.post("/api/export", { run_id: R.result.id, format: fmt });
    toast(t("exp.saved", { path }), { ms: 9000, action: { label: t("btn.reveal"), run: () => api.post("/api/reveal", { path }) } });
  } catch (e) { toast(e.message, { error: true }); }
}

// ====================================================================== history view
const H = { lang: "", title: "", cont: null, rows: [], selected: [] };

async function loadHistory(more = false) {
  if (!more) {
    H.lang = $("#h-lang").value.trim().toLowerCase();
    H.title = $("#h-title").value.trim();
    H.cont = null; H.rows = []; H.selected = [];
    if (!H.title) return;
  }
  const btn = $("#h-load");
  btn.disabled = true;
  try {
    const data = await api.get("/api/revisions", { lang: H.lang, title: H.title, limit: 100,
      start: !more ? $("#h-start").value : null, cont: H.cont });
    H.rows.push(...data.revisions);
    H.cont = data.continue;
    renderHistory();
  } catch (e) { toast(e.message, { error: true }); }
  finally { btn.disabled = false; }
}

function renderHistory() {
  const tbody = $("#h-table tbody");
  if (!H.rows.length) { tbody.replaceChildren(el("tr", {}, el("td", { colspan: 6, text: t("hist.empty") }))); }
  else tbody.replaceChildren(...H.rows.map((r, i) => {
    const older = H.rows[i + 1];
    const delta = older ? r.size - older.size : null;
    const cb = el("input", { type: "checkbox", checked: H.selected.includes(r.revid) });
    cb.addEventListener("change", () => {
      if (cb.checked) { H.selected.push(r.revid); if (H.selected.length > 2) H.selected.shift(); }
      else H.selected = H.selected.filter((x) => x !== r.revid);
      renderHistory();
    });
    return el("tr", {},
      el("td", {}, cb),
      el("td", { class: "time", text: fmtDate(r.timestamp) }),
      el("td", { text: r.user }),
      el("td", { class: "num" }, String(r.size), delta != null
        ? el("span", { class: delta >= 0 ? "delta-pos" : "delta-neg", text: ` ${delta >= 0 ? "+" : ""}${delta}` }) : null),
      el("td", {}, el("span", { text: r.comment }), " ",
        ...r.tags.map((tag) => el("span", { class: "tag" + (r.content_translation && tag.startsWith("content") ? " ct" : ""),
          text: r.content_translation && tag.startsWith("content") ? t("t.ct") : tag }))),
      el("td", {}, el("a", { class: "ext", href: r.diff_url, text: t("btn.diff") })));
  }));
  $("#h-more").hidden = !H.cont;
  $("#h-actions").hidden = H.selected.length === 0;
  $("#h-selected").textContent = t("hist.selected", { n: H.selected.length });
  $("#h-compare").disabled = H.selected.length !== 2;
}

function historyTo(side) {
  const revid = H.selected[H.selected.length - 1];
  cards[side].set({ type: "wiki", lang: H.lang, title: H.title, revid });
  showView("align");
}

function historyCompare() {
  const [a, b] = [...H.selected].sort((x, y) => x - y);
  cards.left.set({ type: "wiki", lang: H.lang, title: H.title, revid: a });
  cards.right.set({ type: "wiki", lang: H.lang, title: H.title, revid: b });
  showView("align");
  runAlignment();
}

// ====================================================================== runs view
async function loadRuns() {
  const tbody = $("#runs-table tbody");
  const { runs } = await api.get("/api/runs");
  const label = (d) => `${d.title} · ${d.lang}${d.timestamp ? " · " + d.timestamp.slice(0, 10) : ""}`;
  if (!runs.length) { tbody.replaceChildren(el("tr", {}, el("td", { colspan: 5, text: t("runs.empty") }))); return; }
  tbody.replaceChildren(...runs.map((r) => el("tr", {},
    el("td", { class: "time", text: fmtDate(r.created.replace(/([+-]\d{4})$/, "")) }),
    el("td", { text: label(r.left) }),
    el("td", { text: label(r.right) }),
    el("td", { class: "num", text: String(r.stats.pairs) }),
    el("td", {},
      el("button", { class: "ghost small", text: t("btn.open"), onclick: async () => renderResult(await api.get(`/api/runs/${r.id}`)) }), " ",
      el("button", { class: "ghost small", text: t("btn.delete"), onclick: async () => { await api.del(`/api/runs/${r.id}`); loadRuns(); } })))));
}

// ====================================================================== models
const MODELS = { list: [], setup: null, memory: null, default: "harrier-270m" };
const TIER_ORDER = ["recommended", "alternative", "light", "general", "large", "custom"];

async function loadModels() {
  const m = await api.get("/api/models");
  MODELS.list = m.models;
  MODELS.setup = m.benchmark_setup;
  MODELS.memory = m.memory_gb;
  MODELS.default = m.default;
  renderModelSelect();
  return m;
}

function modelOptionLabel(x) {
  const parts = [x.label];
  if (x.benchmark) parts.push(`F1 ${x.benchmark.f1.toFixed(3)}`);
  if (x.download) parts.push(x.download);
  return parts.join(" · ");
}

function renderModelSelect() {
  const select = $("#opt-model"), keep = select.value;
  const groups = TIER_ORDER.map((tier) => {
    const items = MODELS.list.filter((x) => x.tier === tier);
    if (!items.length) return null;
    return el("optgroup", { label: t("tier." + tier) },
      ...items.map((x) => el("option", { value: x.key, text: modelOptionLabel(x) })));
  }).filter(Boolean);
  select.replaceChildren(...groups);
  select.value = MODELS.list.some((x) => x.key === keep) ? keep : MODELS.default;
}

function renderModelsTable() {
  const best = Math.max(0, ...MODELS.list.map((x) => x.benchmark?.f1 ?? 0));
  const sorted = [...MODELS.list].sort((a, b) =>
    TIER_ORDER.indexOf(a.tier) - TIER_ORDER.indexOf(b.tier) || (b.benchmark?.f1 ?? 0) - (a.benchmark?.f1 ?? 0));
  $("#models-table tbody").replaceChildren(...sorted.map((x) => {
    const b = x.benchmark;
    const tooBig = MODELS.memory && x.min_ram_gb && MODELS.memory < x.min_ram_gb;
    const status = x.loaded ? t("model.loaded") : x.downloaded ? t("model.downloaded") : t("model.notDownloaded");
    const download = x.downloaded ? null : el("button", { type: "button", class: "ghost small", text: t("model.prepare"),
      onclick: async (e) => {
        e.target.disabled = true;
        e.target.replaceChildren(el("span", { class: "spinner" }));
        try { await pollJob(await api.post(`/api/models/${encodeURIComponent(x.key)}/load`)); }
        catch (err) { toast(err.message, { error: true }); }
        loadSettings();
      } });
    const note = x.note_zh ? pick(x, "note") : "";
    return el("tr", {},
      el("td", { class: "pick" }, el("input", { type: "radio", name: "default_model", value: x.key,
        checked: x.key === MODELS.default, "aria-label": t("m.setDefault") })),
      el("td", {},
        el("div", {}, el("span", { class: "model-name", text: x.label }),
          el("span", { class: `tier ${x.tier}`, text: t("tier." + x.tier) })),
        el("div", { class: "model-id", text: x.model_id + (x.params ? ` · ${x.params}` : "") }),
        el("div", { class: "model-note" }, note,
          b ? "\n" + t("m.thresholdNote", { th: b.recommended_threshold, p: Math.round(b.precision * 100) }) : "",
          x.min_ram_gb >= 16 || tooBig ? "\n" + t("m.ram", { n: x.min_ram_gb }) : "",
          ...(x.sources || []).map((u, i) => [i === 0 ? "\n" : "", el("a", { class: "ext", href: u, text: new URL(u).hostname.replace("www.", "") + " ↗" })]))),
      el("td", { title: b ? Object.entries(b.per_language).map(([l, f]) => `${l} ${f.toFixed(3)}`).join("  ") : null },
        b ? el("div", { class: "f1-bar" },
        el("span", { class: "track" }, el("i", { style: `width:${Math.max(4, ((b.f1 - 0.8) / Math.max(0.01, best - 0.8)) * 100)}%` })),
        b.f1.toFixed(3)) : el("span", { class: "muted", text: t("m.notBenched") })),
      el("td", { class: "num", text: b?.sentences_per_second ? t("m.perSec", { n: Math.round(b.sentences_per_second) }) : "–" }),
      el("td", { class: "num", text: x.download || "–" }),
      el("td", { class: "num", text: x.languages || "–" }),
      el("td", { text: x.license || "–" }),
      el("td", {}, el("div", { class: "muted", text: status }), download));
  }));
  const setup = MODELS.setup;
  $("#bench-method").textContent = setup
    ? t("m.methodText", { n: setup.languages.length, langs: setup.languages.join(", ") }) + `\n${setup.machine}`
    : "";
}

// ====================================================================== settings view
async function loadSettings() {
  const [s] = await Promise.all([api.get("/api/settings"), loadModels()]);
  const form = $("#settings-form");
  for (const [k, v] of Object.entries(s)) if (form.elements[k] && k !== "default_model") form.elements[k].value = v ?? "";
  form.elements.export_dir.placeholder = s.export_dir_resolved;
  $("#cache-size").textContent = t("set.cache", { size: `${(s.cache_bytes / 1048576).toFixed(1)} MB` });
  renderModelsTable();
  return s;
}

async function saveSettings(e) {
  e.preventDefault();
  const body = Object.fromEntries(new FormData($("#settings-form")));
  try { await api.post("/api/settings", body); toast(t("set.saved")); loadSettings(); }
  catch (err) { toast(err.message, { error: true }); }
}

// ====================================================================== shell
function showView(name) {
  $$(".tabs button").forEach((b) => b.classList.toggle("active", b.dataset.view === name));
  $$(".view").forEach((v) => v.classList.toggle("active", v.id === `view-${name}`));
  if (name === "runs") loadRuns().catch((e) => toast(e.message, { error: true }));
  if (name === "settings") loadSettings().catch((e) => toast(e.message, { error: true }));
}

function refreshLanguage() {
  $$("#ui-lang button").forEach((b) => b.classList.toggle("on", b.dataset.lang === getLanguage()));
  relabelCards();
  for (const side of ["left", "right"]) cards[side]?.info && cards[side].loadInfo();
  renderModelSelect();
  if ($("#view-settings").classList.contains("active")) renderModelsTable();
  if ($("#view-runs").classList.contains("active")) loadRuns().catch(() => {});
  if (R.result) { applyFilter(); if (R.selected) renderDrawer(R.selected.side, R.selected.id); }
  if (H.rows.length) renderHistory();
}

const EXAMPLES = {
  nemtsov: [
    { type: "wiki", lang: "en", title: "Assassination of Boris Nemtsov", date: "2015-03-10" },
    { type: "wiki", lang: "ru", title: "Убийство Бориса Немцова", date: "2015-03-10" },
  ],
  "nemtsov-rev": [
    { type: "wiki", lang: "en", title: "Assassination of Boris Nemtsov", date: "2015-03-10" },
    { type: "wiki", lang: "en", title: "Assassination of Boris Nemtsov" },
  ],
};

async function init() {
  $("#lang-list").replaceChildren(...LANGS.map(([code, name]) => el("option", { value: code, label: name })));
  cards.left = new SourceCard($('.source-card[data-side="left"]'), "left");
  cards.right = new SourceCard($('.source-card[data-side="right"]'), "right");

  $$(".tabs button").forEach((b) => b.addEventListener("click", () => showView(b.dataset.view)));
  $("#run").addEventListener("click", runAlignment);
  $("#swap").addEventListener("click", () => {
    const a = cards.left.spec(), b = cards.right.spec();
    cards.left.set(b); cards.right.set(a);
  });
  $("#same-article").addEventListener("click", () => {
    const s = cards.left.spec();
    cards.right.set({ type: "wiki", lang: s.lang, title: s.title });
    if (cards.left.mode === "latest") { cards.left.setMode("date"); cards.left.q(".rev-date").focus(); }
  });
  $("#same-date").addEventListener("click", () => {
    const d = cards.left.q(".rev-date").value;
    if (!d) { cards.left.setMode("date"); cards.left.q(".rev-date").focus(); return; }
    cards.right.setMode("date");
    cards.right.q(".rev-date").value = d;
  });
  $$("[data-example]").forEach((b) => b.addEventListener("click", () => {
    const [l, r] = EXAMPLES[b.dataset.example];
    cards.left.set(l); cards.right.set(r);
    runAlignment();
  }));

  for (const side of ["left", "right"]) {
    const body = $(`#body-${side}`);
    body.addEventListener("mouseover", onSegHover);
    body.addEventListener("mouseleave", () => $$(".seg-s.hl").forEach((s) => s.classList.remove("hl")));
    body.addEventListener("click", onSegClick);
  }
  $("#flt-threshold").addEventListener("input", applyFilter);
  $("#flt-score").addEventListener("change", (e) => { setScoreMode(e.target.value, false); applyFilter(); });
  $("#flt-ids").addEventListener("change", applyFilter);
  $("#flt-unmatched").addEventListener("change", applyFilter);
  $("#export-btn").addEventListener("click", () => { $("#export-menu").hidden = !$("#export-menu").hidden; });
  $$("#export-menu button").forEach((b) => b.addEventListener("click", () => exportResult(b.dataset.fmt)));
  document.addEventListener("click", (e) => { if (!e.target.closest(".menu")) $("#export-menu").hidden = true; });

  attachSuggest($("#h-title"), $("#view-history .suggest"), () => $("#h-lang").value.trim(), () => loadHistory());
  $("#h-load").addEventListener("click", () => loadHistory());
  $("#h-more").addEventListener("click", () => loadHistory(true));
  $("#h-compare").addEventListener("click", historyCompare);
  $("#h-to-left").addEventListener("click", () => historyTo("left"));
  $("#h-to-right").addEventListener("click", () => historyTo("right"));

  $("#settings-form").addEventListener("submit", saveSettings);
  $("#clear-cache").addEventListener("click", async () => { await api.post("/api/cache/clear"); loadSettings(); });
  $$("#ui-lang button").forEach((b) => b.addEventListener("click", () => {
    setLanguage(b.dataset.lang);
    refreshLanguage();
    api.post("/api/settings", { ui_language: b.dataset.lang }).catch(() => {});
  }));
  $("#flt-reset").addEventListener("click", () => { applyRecommendedThreshold(); applyFilter(); });

  const health = await api.get("/api/health");
  $("#version").textContent = "v" + health.version;
  const s = await loadSettings();
  setLanguage(s.ui_language || "bi");
  refreshLanguage();

  // Deep links: #history, #runs, #settings, or #run=<id> to open a saved result.
  const hash = decodeURIComponent(location.hash.slice(1));
  if (["history", "runs", "settings"].includes(hash)) showView(hash);
  else if (hash.startsWith("run=")) renderResult(await api.get(`/api/runs/${hash.slice(4)}`));
}

init().catch((e) => toast(e.message, { error: true }));
