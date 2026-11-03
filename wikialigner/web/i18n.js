// UI strings. Keys used in index.html via data-i18n / data-i18n-placeholder, and in app.js via t().
export const STRINGS = {
  zh: {
    "tab.align": "对齐", "tab.history": "修订历史", "tab.runs": "记录", "tab.settings": "设置",
    "side.left": "左侧", "side.right": "右侧", "side.old": "旧版本", "side.new": "新版本",
    "src.wiki": "维基百科", "src.text": "文本 / 文件", "src.variant": "字形",
    "var.orig": "原文（不转换）", "var.zh-hans": "简体", "var.zh-hant": "繁體", "var.zh-cn": "大陆简体",
    "var.zh-tw": "台湾正体", "var.zh-hk": "香港繁體", "var.sr-ec": "Ћирилица", "var.sr-el": "Latinica",
    "rev.latest": "最新", "rev.date": "按日期", "rev.revid": "修订号",
    "ph.title": "条目标题", "ph.name": "名称", "ph.text": "粘贴文本；空行分隔段落",
    "btn.swap": "⇅ 交换左右", "btn.sameArticle": "右侧用同一条目（比较修订）", "btn.sameDate": "右侧用相同日期",
    "btn.run": "开始对齐", "btn.export": "导出 ▾", "btn.openFile": "打开文件…", "btn.loadHistory": "查看修订历史",
    "btn.compare": "比较所选两个版本", "btn.toLeft": "设为左侧", "btn.toRight": "设为右侧", "btn.more": "加载更多",
    "btn.clearCache": "清除网页缓存", "btn.save": "保存设置", "btn.open": "打开", "btn.delete": "删除",
    "btn.reveal": "在文件夹中显示", "btn.trace": "追溯两句的首次出现", "btn.traceOne": "追溯此句首次出现",
    "btn.translate": "在 {svc} 中翻译", "btn.close": "关闭", "btn.viewRev": "查看该修订", "btn.diff": "查看改动",
    "btn.download": "下载", "btn.fuzzy": "允许措辞小改动",
    "opt.title": "对齐选项", "opt.model": "模型", "opt.granularity": "切分粒度", "opt.strategy": "匹配方式",
    "opt.include": "包含内容", "opt.minMargin": "最低 margin",
    "gran.sentence": "句子", "gran.clause": "分句（更细，长句拆开）", "gran.paragraph": "段落",
    "strat.greedy": "一对一（默认）", "strat.many": "允许一对多（拆句、合句）", "strat.mutual": "仅互为最佳（更严格）",
    "inc.captions": "图片说明", "inc.lists": "列表", "inc.tables": "表格", "inc.infobox": "信息框", "inc.headings": "对齐标题",
    "flt.score": "按", "flt.cos": "余弦相似度", "flt.ids": "编号", "flt.unmatched": "只看未对齐",
    "empty.title": "选择两篇文本，找出彼此对应的句子",
    "empty.body": "左右两侧可以是同一条目的不同语言版本（找译文），也可以是同一条目的两个历史版本（看改动）。历史版本可按日期或修订号指定。",
    "ex.nemtsov": "示例：涅姆佐夫遇刺 · 英文 / 俄文 · 2015-03-10", "ex.nemtsovRev": "示例：同一英文条目 · 2015-03-10 / 现在",
    "hist.before": "早于", "hist.time": "时间 (UTC)", "hist.user": "编辑者", "hist.size": "大小", "hist.comment": "编辑摘要",
    "hist.hint": "勾选两个版本可直接比较；“内容翻译”标记表示该次编辑用维基百科的内容翻译工具完成，是判断翻译方向的有力线索。",
    "hist.selected": "已选 {n} 个版本", "hist.empty": "没有找到修订。",
    "runs.title": "保存的对齐结果", "runs.hint": "每次对齐都会自动保存在本机，打开时无需重新计算。",
    "runs.time": "时间", "runs.left": "左侧", "runs.right": "右侧", "runs.pairs": "句对", "runs.empty": "还没有保存的结果。",
    "set.defaultModel": "默认模型", "set.custom": "其他模型（每行一个 Hugging Face 模型名）", "set.mirror": "模型下载地址",
    "set.mirrorDefault": "huggingface.co（默认）", "set.mirrorCn": "hf-mirror.com（中国大陆可用的镜像）",
    "set.restart": "更改后需重启应用生效。", "set.proxy": "网络代理（访问维基百科用，留空则使用系统代理）",
    "set.exportDir": "导出文件夹（留空为“下载/WikiAligner”）", "set.cache": "网页缓存 {size}", "set.saved": "设置已保存",
    "model.downloaded": "已下载", "model.notDownloaded": "首次使用时下载", "model.loaded": "已加载", "model.prepare": "预先下载",
    "p.fetch_left": "正在获取左侧文本…", "p.fetch_right": "正在获取右侧文本…", "p.load_model": "正在加载模型…",
    "p.download_model": "正在下载模型（仅首次，可能需要几分钟）…", "p.embed": "正在计算句向量…", "p.align": "正在匹配句子…",
    "p.list_revisions": "正在读取修订列表…", "p.list_revisions_n": "已读取 {n} 个修订…", "p.probe": "正在检查 {date} 的版本（第 {n} 次）…",
    "p.queued": "排队中…", "p.left": "左侧：", "p.right": "右侧：",
    "stat.pairs": "{n} 对", "stat.identical": "其中 {n} 句未改动", "stat.coverage": "{side}覆盖 {p}%", "stat.seconds": "{s} 秒",
    "stat.visible": "当前阈值下 {n} 对",
    "legend.matched": "已对齐（颜色越深分数越高）", "legend.unmatched": "未对齐", "legend.identical": "未改动",
    "legend.modified": "有改动", "legend.removed": "已删除", "legend.added": "新增",
    "d.pair": "句对", "d.unmatched": "未对齐的句子", "d.reason.weak": "最接近的对应句分数低于阈值",
    "d.reason.taken": "最接近的对应句已与另一句配对", "d.reason.threshold": "已配对，但分数低于当前显示阈值",
    "d.best": "最接近的对应句", "d.scores": "余弦 {cos} · margin {margin}", "d.charRatio": "字面相似度 {r}",
    "d.identical": "完全相同",
    "t.running": "正在追溯（按修订历史二分查找）…", "t.first": "首次出现：{date}", "t.by": "编辑者 {user}",
    "t.creation": "条目创建时即有", "t.ct": "内容翻译工具", "t.searched": "检索了 {n} 个修订中的 {f} 个",
    "t.earlier": "{side} 版本中的句子出现得更早（早 {d}）。这是判断翻译方向的线索，不是定论：也可能双方都译自第三种语言，或同一编辑者同时修改了两边。",
    "t.same": "两句出现时间相同。", "t.days": "{n} 天", "t.hours": "{n} 小时", "t.minutes": "{n} 分钟",
    "t.caveat": "假设句子出现后一直保留；若曾删除再加回，结果是其中一次出现的时间。",
    "e.noTitle": "请填写{side}的条目标题", "e.noText": "请粘贴{side}的文本", "e.failed": "失败：{msg}",
    "exp.saved": "已保存到 {path}", "mode.crosslingual": "跨语言", "mode.revision": "修订对比",
    "links.choose": "其他语言版本（{n}）→ 填入{side}", "meta.latest": "最新修订 {date}", "meta.langs": "{n} 种语言",
  },
  en: {
    "tab.align": "Align", "tab.history": "History", "tab.runs": "Saved", "tab.settings": "Settings",
    "side.left": "Left", "side.right": "Right", "side.old": "Older", "side.new": "Newer",
    "src.wiki": "Wikipedia", "src.text": "Text / file", "src.variant": "Script",
    "var.orig": "Original (no conversion)", "var.zh-hans": "Simplified", "var.zh-hant": "Traditional", "var.zh-cn": "Mainland",
    "var.zh-tw": "Taiwan", "var.zh-hk": "Hong Kong", "var.sr-ec": "Cyrillic", "var.sr-el": "Latin",
    "rev.latest": "Latest", "rev.date": "As of date", "rev.revid": "Revision ID",
    "ph.title": "Article title", "ph.name": "Name", "ph.text": "Paste text; blank lines separate paragraphs",
    "btn.swap": "⇅ Swap sides", "btn.sameArticle": "Same article on the right (compare revisions)", "btn.sameDate": "Same date on the right",
    "btn.run": "Align", "btn.export": "Export ▾", "btn.openFile": "Open file…", "btn.loadHistory": "Show history",
    "btn.compare": "Compare the two selected", "btn.toLeft": "Use as left", "btn.toRight": "Use as right", "btn.more": "Load more",
    "btn.clearCache": "Clear page cache", "btn.save": "Save settings", "btn.open": "Open", "btn.delete": "Delete",
    "btn.reveal": "Show in folder", "btn.trace": "Trace when both sentences first appeared", "btn.traceOne": "Trace first appearance",
    "btn.translate": "Translate in {svc}", "btn.close": "Close", "btn.viewRev": "View revision", "btn.diff": "View change",
    "btn.download": "Download", "btn.fuzzy": "Allow small wording changes",
    "opt.title": "Alignment options", "opt.model": "Model", "opt.granularity": "Granularity", "opt.strategy": "Matching",
    "opt.include": "Include", "opt.minMargin": "Minimum margin",
    "gran.sentence": "Sentence", "gran.clause": "Clause (splits long sentences)", "gran.paragraph": "Paragraph",
    "strat.greedy": "One-to-one (default)", "strat.many": "Allow one-to-many (splits, merges)", "strat.mutual": "Mutual best only (stricter)",
    "inc.captions": "Captions", "inc.lists": "Lists", "inc.tables": "Tables", "inc.infobox": "Infobox", "inc.headings": "Align headings",
    "flt.score": "Filter by", "flt.cos": "Cosine", "flt.ids": "IDs", "flt.unmatched": "Unmatched only",
    "empty.title": "Pick two texts to find the sentences that correspond",
    "empty.body": "The two sides can be language editions of one article (to find translations) or two revisions of one article (to see what changed). Revisions can be chosen by date or by revision ID.",
    "ex.nemtsov": "Example: Assassination of Boris Nemtsov · en / ru · 2015-03-10", "ex.nemtsovRev": "Example: same English article · 2015-03-10 / now",
    "hist.before": "Before", "hist.time": "Time (UTC)", "hist.user": "Editor", "hist.size": "Size", "hist.comment": "Summary",
    "hist.hint": "Tick two revisions to compare them. The “Content Translation” tag means the edit was made with Wikipedia's translation tool, a strong clue about translation direction.",
    "hist.selected": "{n} selected", "hist.empty": "No revisions found.",
    "runs.title": "Saved alignments", "runs.hint": "Every alignment is saved on this computer and opens without recomputing.",
    "runs.time": "Time", "runs.left": "Left", "runs.right": "Right", "runs.pairs": "Pairs", "runs.empty": "Nothing saved yet.",
    "set.defaultModel": "Default model", "set.custom": "Other models (one Hugging Face model id per line)", "set.mirror": "Model download source",
    "set.mirrorDefault": "huggingface.co (default)", "set.mirrorCn": "hf-mirror.com (mirror reachable from mainland China)",
    "set.restart": "Takes effect after restarting the app.", "set.proxy": "Proxy for Wikipedia (empty: use the system proxy)",
    "set.exportDir": "Export folder (empty: Downloads/WikiAligner)", "set.cache": "Page cache {size}", "set.saved": "Settings saved",
    "model.downloaded": "Downloaded", "model.notDownloaded": "Downloads on first use", "model.loaded": "Loaded", "model.prepare": "Download now",
    "p.fetch_left": "Fetching the left text…", "p.fetch_right": "Fetching the right text…", "p.load_model": "Loading the model…",
    "p.download_model": "Downloading the model (first time only; may take a few minutes)…", "p.embed": "Embedding sentences…", "p.align": "Matching sentences…",
    "p.list_revisions": "Reading the revision list…", "p.list_revisions_n": "Read {n} revisions…", "p.probe": "Checking the revision of {date} (probe {n})…",
    "p.queued": "Queued…", "p.left": "Left: ", "p.right": "Right: ",
    "stat.pairs": "{n} pairs", "stat.identical": "{n} unchanged", "stat.coverage": "{side} coverage {p}%", "stat.seconds": "{s} s",
    "stat.visible": "{n} at this threshold",
    "legend.matched": "Aligned (darker = higher score)", "legend.unmatched": "Unmatched", "legend.identical": "Unchanged",
    "legend.modified": "Changed", "legend.removed": "Removed", "legend.added": "Added",
    "d.pair": "Pair", "d.unmatched": "Unmatched sentence", "d.reason.weak": "Its closest counterpart scores below the threshold",
    "d.reason.taken": "Its closest counterpart is paired with another sentence", "d.reason.threshold": "Paired, but below the display threshold",
    "d.best": "Closest counterpart", "d.scores": "cosine {cos} · margin {margin}", "d.charRatio": "character similarity {r}",
    "d.identical": "Identical",
    "t.running": "Tracing (bisecting the revision history)…", "t.first": "First appeared: {date}", "t.by": "by {user}",
    "t.creation": "present when the article was created", "t.ct": "Content Translation", "t.searched": "checked {f} of {n} revisions",
    "t.earlier": "The {side} sentence appeared first ({d} earlier). This is a clue to translation direction, not proof: both may come from a third language, or one editor may have changed both.",
    "t.same": "Both sentences appeared at the same time.", "t.days": "{n} days", "t.hours": "{n} hours", "t.minutes": "{n} minutes",
    "t.caveat": "Assumes a sentence stays once added; if it was removed and re-added, this is one of the times it appeared.",
    "e.noTitle": "Enter an article title for the {side} side", "e.noText": "Paste text for the {side} side", "e.failed": "Failed: {msg}",
    "exp.saved": "Saved to {path}", "mode.crosslingual": "Cross-lingual", "mode.revision": "Revision comparison",
    "links.choose": "Other language editions ({n}) → fill the {side} side", "meta.latest": "latest revision {date}", "meta.langs": "{n} languages",
  },
};

// Strings added for the model chooser and the bilingual mode.
Object.assign(STRINGS.zh, {
  "ui.zh": "中文", "ui.en": "English", "ui.bi": "中英对照",
  "set.models": "句向量模型", "set.modelsIntro": "不同模型在找译文上的表现差别明显。下表综合了公开评测和在本机用 WikiAligner 实际对齐流程做的测试；“推荐阈值”会在打开结果时自动应用。",
  "m.model": "模型", "m.tier": "定位", "m.size": "下载", "m.langs": "语言", "m.f1": "本机 F1", "m.speed": "速度",
  "m.license": "许可", "m.status": "状态", "m.perSec": "{n} 句/秒", "m.default": "默认", "m.setDefault": "设为默认",
  "m.ram": "建议内存 ≥ {n} GB", "m.notBenched": "未测", "m.method": "本机评测方法", "m.sources": "来源",
  "m.methodText": "NTREX-128 新闻平行语料，{langs} 共 {n} 种语言。每组 300 句英文，其中一半有译文，目标语言一侧另加 150 句无关句子；用 WikiAligner 的一对一匹配，按 margin 阈值计算 F1。维基百科上的真实译文往往更自由，实际分数会更低。",
  "m.thresholdNote": "推荐阈值 margin ≥ {th}（在评测中精确率约 {p}%）",
  "e.offline": "连不上 WikiAligner 的本地服务，应用可能已经关闭。请重新启动 WikiAligner。",
  "tier.recommended": "推荐", "tier.alternative": "备选", "tier.light": "轻量",
  "tier.general": "通用检索（找译文较弱）", "tier.large": "大模型", "tier.custom": "自定义",
  "flt.recommended": "推荐阈值", "flt.reset": "恢复推荐值",
});
Object.assign(STRINGS.en, {
  "ui.zh": "中文", "ui.en": "English", "ui.bi": "Bilingual",
  "set.models": "Sentence-embedding models", "set.modelsIntro": "Models differ clearly at finding translations. The table combines published benchmarks with tests run on this computer through WikiAligner's own alignment. The recommended threshold is applied automatically when a result opens.",
  "m.model": "Model", "m.tier": "Role", "m.size": "Download", "m.langs": "Languages", "m.f1": "Local F1", "m.speed": "Speed",
  "m.license": "Licence", "m.status": "Status", "m.perSec": "{n} sent/s", "m.default": "Default", "m.setDefault": "Make default",
  "m.ram": "Needs ≥ {n} GB memory", "m.notBenched": "not tested", "m.method": "How the local test works", "m.sources": "Sources",
  "m.methodText": "NTREX-128 news parallel corpus, {n} languages ({langs}). Each episode has 300 English sentences, half of them translated, plus 150 unrelated sentences on the target side; WikiAligner's one-to-one matching is scored by F1 at a margin threshold. Real Wikipedia translations are often freer, so expect lower scores there.",
  "m.thresholdNote": "recommended threshold margin ≥ {th} (about {p}% precision in the test)",
  "e.offline": "Cannot reach WikiAligner's local server; the app may have been closed. Restart WikiAligner.",
  "tier.recommended": "Recommended", "tier.alternative": "Alternative", "tier.light": "Lightweight",
  "tier.general": "General retrieval (weak at translations)", "tier.large": "Large", "tier.custom": "Custom",
  "flt.recommended": "Recommended threshold", "flt.reset": "Reset to recommended",
});

// "zh", "en", or "bi" (Chinese and English together).
let current = "bi";

function single(lang, key, vars) {
  const s = STRINGS[lang][key] ?? STRINGS.zh[key] ?? key;
  return s.replace(/\{(\w+)\}/g, (_, k) => {
    const v = vars[k];
    if (v && typeof v === "object") return v[lang] ?? v.zh;  // a translated value, see tv()
    return v ?? `{${k}}`;
  });
}

// A translated value to pass into another string, so bilingual mode does not repeat it.
export function tv(key) { return { zh: single("zh", key, {}), en: single("en", key, {}) }; }

export function setLanguage(mode) {
  current = ["zh", "en", "bi"].includes(mode) ? mode : "bi";
  document.documentElement.lang = current === "en" ? "en" : "zh";
  document.body.classList.toggle("bilingual", current === "bi");
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    const key = el.dataset.i18n;
    if (current !== "bi" || el.tagName === "OPTION") { el.textContent = t(key); return; }
    const zh = single("zh", key, {}), en = single("en", key, {});
    if (zh === en) { el.textContent = zh; return; }
    const a = document.createElement("span"); a.className = "l-zh"; a.textContent = zh;
    const b = document.createElement("span"); b.className = "l-en"; b.textContent = en;
    el.replaceChildren(a, b);
  });
  document.querySelectorAll("[data-i18n-placeholder]").forEach((el) => { el.placeholder = t(el.dataset.i18nPlaceholder, {}, " / "); });
}

export function getLanguage() { return current; }

// In bilingual mode short strings are joined on one line and long ones on two;
// containers that show long text use white-space: pre-line.
export function t(key, vars = {}, sep = null) {
  if (current !== "bi") return single(current, key, vars);
  const zh = single("zh", key, vars), en = single("en", key, vars);
  if (zh === en) return zh;
  return zh + (sep ?? (zh.length + en.length > 60 ? "\n" : " · ")) + en;
}

// Pick the field for the current language from an object with *_zh / *_en fields.
export function pick(obj, field) {
  if (current === "zh") return obj[`${field}_zh`];
  if (current === "en") return obj[`${field}_en`];
  return `${obj[`${field}_zh`]}\n${obj[`${field}_en`]}`;
}
