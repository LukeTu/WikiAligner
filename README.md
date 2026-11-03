# WikiAligner

Find corresponding sentences across Wikipedia language editions, or across two revisions of one article. A desktop app for macOS and Windows; no server needed.

在维基百科的不同语言版本之间、或同一条目的不同历史版本之间，找出彼此对应的句子。这是一个可在 macOS 和 Windows 上运行的桌面应用，不需要服务器。

**[Download the latest release / 下载最新版本](https://github.com/LukeTu/WikiAligner/releases/latest)** · [English](#english) · [中文](#中文)

## Paper / 论文

WikiAligner was introduced in this paper. The method and the planned improvements described there are the basis of this version.

WikiAligner 最早发表于下面这篇论文。这一版的方法和新增功能都以论文为基础。

> Tu, Z., Wang, M., Shuttleworth, M., & Hua, Z. (2022). Using bitext mining to identify translated material: Practical assessment and new applications. In *Translating and the Computer 44*, 24–25 November 2022, Luxembourg (pp. 147–152). Geneva: Editions Tradulex, 2023. ISBN 978-2-9701733-0-4.

[Proceedings PDF, p. 147 / 论文集 PDF，第 147 页](https://asling.org/tc44/wp-content/uploads/2025/03/TC44-luxembourg2022.pdf#page=147) · [Conference slides / 会议幻灯片](https://asling.org/tc44/slides/TC44-Zhilu_TU-Using%20bitext%20mining%20to%20identify%20translated%20material(v3).pdf) · [TC44 conference site / TC44 会议网站](https://asling.org/tc44/)

```bibtex
@inproceedings{tu2022bitext,
  author    = {Tu, Zhilu and Wang, Minghao and Shuttleworth, Mark and Hua, Zhiwen},
  title     = {Using bitext mining to identify translated material: practical assessment and new applications},
  booktitle = {Translating and the Computer 44},
  pages     = {147--152},
  year      = {2022},
  address   = {Geneva},
  publisher = {Editions Tradulex},
  isbn      = {978-2-9701733-0-4},
  note      = {Conference held 24--25 November 2022, Luxembourg; proceedings published September 2023},
  url       = {https://asling.org/tc44/wp-content/uploads/2025/03/TC44-luxembourg2022.pdf}
}
```

---

## English

### What it does

- **Cross-language alignment**: finds likely translation pairs between two language editions of an article. Pairs are coloured by score; hover to highlight, click for details.
- **Historical versions**: each side can use the latest version, the version current on a given date, or a specific revision ID. Using the same date on both sides aligns the two editions as they stood at that moment.
- **Revision comparison**: with two revisions of one article, shows which sentences are unchanged, changed (with character similarity), removed or added.
- **Revision history**: lists revisions with time, editor, size change, summary and tags, and marks edits made with Wikipedia's Content Translation tool. Tick two revisions to compare them.
- **First-appearance tracing**: for a sentence pair, searches each article's history for the revision where each sentence first appeared and compares the dates, which gives a clue to translation direction. Small wording changes can optionally be allowed.
- **Your own text**: either side can be pasted text or a .txt, .md or .docx file.
- **Export**: Excel (pairs, unmatched sentences on each side, metadata), CSV or JSON. Metadata records revision IDs, links, model, parameters and the CC BY-SA licence note.
- **Saved results**: every result is saved on your computer and reopens without recomputing.
- **Bilingual interface**: switch between 中, EN and 中/EN at the top right. 中/EN shows Chinese and English together and is the default.
- **Model choice**: nine models in five groups. The Settings page compares them, and each result opens with a threshold recommended for its model.

### Install

Runs on Macs with Apple silicon (M1 or later) and 64-bit Windows 10/11. The installers include the default model (Harrier 270M), so nothing else needs downloading. Wikipedia access is needed in use. Other models download the first time you use them.

**macOS**: paste this into Terminal. It downloads, installs and opens the app:

```bash
curl -fsSL https://github.com/LukeTu/WikiAligner/releases/latest/download/install_mac.sh | bash
```

Or download `WikiAligner-macOS-arm64.dmg` from the [Releases page](https://github.com/LukeTu/WikiAligner/releases/latest) and drag the app to Applications. The first time macOS blocks it, open System Settings → Privacy & Security and click **Open Anyway**.

**Windows**: download and run `WikiAligner-Windows-x64-Setup.exe` from the [Releases page](https://github.com/LukeTu/WikiAligner/releases/latest). No administrator rights are needed. If SmartScreen appears, click **More info → Run anyway**. Or run this in PowerShell:

```powershell
irm https://github.com/LukeTu/WikiAligner/releases/latest/download/install_windows.ps1 | iex
```

These warnings appear because the app is not signed with a paid Apple or Microsoft certificate.

**Hand it to an AI assistant**: if the installers do not work, give `WikiAligner-handoff.zip` to an AI coding agent such as Claude Code and say: "Unzip this and follow HANDOFF.md to install WikiAligner on this computer."

Intel Macs are not supported, because current PyTorch has no Intel Mac builds.

In mainland China, Wikipedia needs a proxy. The app uses the system proxy by default, and you can set another under Settings. If huggingface.co cannot be reached, model downloads switch to the hf-mirror.com mirror automatically.

### Changes since the first version

Improvements planned in the paper that this version delivers:

| Planned in the paper | In this version |
|---|---|
| Use the MediaWiki parse output to avoid losing text and to reach historical versions | Fetches rendered HTML by revision ID, keeping sections, lists and captions, with tables and infoboxes optional. Works with any revision. Chinese can be converted between Simplified and Traditional |
| Compare revisions in one language (intralingual alignment) | Switches to revision comparison automatically when both sides share a language |
| Finer segmentation to reveal translation units inside long sentences | Sentence, clause or paragraph granularity, plus optional one-to-many matching for split and merged sentences |
| Support other embedding models | Harrier, LaBSE, Multilingual E5, BGE-M3, MiniLM and Qwen3, or any Hugging Face model name |
| Align uploaded files | Paste text or open a .txt, .md or .docx file |

Other changes:

- Runs entirely on your computer, with no server to deploy.
- Any language can be the starting point; an article no longer needs an English version.
- Sentence numbering is consistent everywhere, so the screen and the Excel export always agree.
- Short articles align correctly, because the number of neighbours k now adapts to article length.
- Chinese keeps its last sentence, and Japanese, Thai, Burmese and Khmer are segmented.
- Translation links open Bing, DeepL or Google in your browser, so the app needs no API key.
- The local server listens on 127.0.0.1 only and refuses requests for other host names.

The first version's code remains in the repository's history.

### Choosing a model

Published benchmarks have no ranking for finding translations within one article; MTEB bitext-mining scores average several different tasks. So this version also tests each model through WikiAligner's own alignment (`scripts/benchmark_models.py`):

- Corpus: NTREX-128 news parallel corpus, ten languages (Chinese, Russian, German, Japanese, Arabic, Korean, Thai, Swahili, Tamil, Amharic).
- Setup: three episodes per language, each with 300 English sentences, half of them translated, plus 150 unrelated sentences on the target side. One-to-one matching, scored by F1 at the best margin threshold.
- Machine: Apple silicon Mac (MPS), 2026-10-31. The Windows version uses the CPU only, so it runs slower.

| Model | Group | Local F1 | Sentences/s | Download | Published | Notes |
|---|---|---|---|---|---|---|
| Harrier OSS v1 270M | Recommended (default, included) | 0.991 | 136 | 0.5 GB | Multilingual MTEB v2 average 66.5 | Released April 2026. Steady in all ten languages. About 50 sentences/s on four CPU threads, slightly faster than LaBSE (about 41) |
| LaBSE | Recommended | 0.991 | 385 | 1.9 GB | BUCC 98.8 | Used in the paper, so results stay comparable. Fastest on Apple silicon. Slightly weaker on Thai; input is limited to 256 tokens |
| Harrier OSS v1 0.6B | Alternative | 0.990 | 26 | 1.2 GB | Multilingual MTEB v2 average 69.0 | Scores like the 270M version but runs far slower |
| Multilingual E5 large instruct | Alternative | 0.989 | 92 | 2.2 GB | MTEB bitext 80.1 | Highest recall |
| BGE-M3 | Alternative | 0.983 | 95 | 2.3 GB | MTEB bitext 79.1; top cluster in a 2026 robustness study | Handles longer input, so it suits paragraphs. Weaker on Amharic |
| Multilingual E5 small | Lightweight | 0.965 | 860 | 0.5 GB | | Small and fast |
| Multilingual MiniLM | Lightweight | 0.790 | 926 | 0.5 GB | | Close to useless on Swahili, Tamil and Amharic |
| Qwen3-Embedding 0.6B | General retrieval | 0.941 | 25 | 1.2 GB | MTEB bitext 72.2 | Weak at finding translations; not advised |
| Qwen3-Embedding 4B | Large | not tested | | 8 GB | MTEB bitext 79.4 | Needs 16 GB+ of memory |

- News translations are much cleaner than Wikipedia's, and the top five models differ by only about one point here. On a real article (Assassination of Boris Nemtsov, en/ru, 2015-03-10), LaBSE, Harrier 270M, E5 large and BGE-M3 each found 19–26 pairs at their recommended thresholds, and all four agreed on 15. When in doubt, run two models and compare.
- Score ranges differ by model, so each has its own recommended margin threshold: the lowest that reaches 97% precision in this test.
- Models that need an instruction or prefix (E5, Harrier, Qwen3) get it automatically.
- To rerun the test or add a model, run `uv run python scripts/benchmark_models.py [model keys]`. Results go to `wikialigner/model_benchmark.json`, which the app reads directly.

Sources: [MMTEB robustness study](https://arxiv.org/abs/2605.31142), [MTEB table in the Qwen3-Embedding report](https://github.com/QwenLM/Qwen3-Embedding), [Multilingual E5 technical report](https://arxiv.org/abs/2402.05672), [Harrier OSS v1 model card](https://huggingface.co/microsoft/harrier-oss-v1-270m), [LaBSE](https://arxiv.org/abs/2007.01852).

### Run from source

Double-click `scripts/start_mac.command` on macOS or `scripts/start_windows.bat` on Windows. The first start installs [uv](https://docs.astral.sh/uv/), Python 3.12 and the dependencies (about 1 GB). Later starts take seconds. From a terminal:

```bash
uv run -m wikialigner            # open the app window
uv run -m wikialigner --browser  # use the default browser instead
uv run pytest                    # run the tests (no network needed)
```

To publish a release, push a `v*` tag. `.github/workflows/build.yml` then builds both installers on GitHub Actions, installs each one, runs `packaging/smoke_test.py`, and publishes the Release only if everything passes. `HANDOFF.md` has the steps for building locally.

### Where data is stored

| What | macOS | Windows |
|---|---|---|
| Settings, saved results | `~/Library/Application Support/WikiAligner` | `%LOCALAPPDATA%\WikiAligner` |
| Wikipedia page cache | `~/Library/Caches/WikiAligner` | `%LOCALAPPDATA%\WikiAligner\Cache` |
| Downloaded models | `~/.cache/huggingface` | `%USERPROFILE%\.cache\huggingface` |
| Exports | `Downloads/WikiAligner` (can be changed in Settings) | same |
| Log (installed app) | `~/Library/Application Support/WikiAligner/wikialigner.log` | `%LOCALAPPDATA%\WikiAligner\wikialigner.log` |

### Project layout

```
wikialigner/
  wiki.py       Wikipedia access: search, language links, revisions, HTML by revision (cached)
  extract.py    HTML to ordered text blocks
  segment.py    multilingual sentence and clause segmentation
  models.py     model list, loading, vector cache
  model_benchmark.json  local benchmark results
  align.py      margin scoring (Artetxe & Schwenk 2019) and three matching strategies
  pipeline.py   from two sources to one alignment result
  history.py    first-appearance tracing (bisects the revision history)
  export.py     Excel, CSV and JSON export
  jobs.py       background jobs and saved results
  server.py     local HTTP API
  desktop.py    starts the server and opens the window
  web/          interface (plain HTML, CSS and JS; no build step)
tests/          unit and API tests (no network)
scripts/        double-click start scripts, model benchmark
packaging/      installers, install scripts, smoke test
```

### Known limitations

- Pairs are candidates for human review. High similarity shows that two sentences say the same thing, not that one was translated from the other.
- Recommended thresholds come from the news-corpus test above and have not been calibrated against a Wikipedia gold standard. Custom models have no benchmark and start at cosine ≥ 0.70.
- First-appearance tracing assumes a sentence stays once added; if it was removed and re-added, the result is one of the times it appeared. Each search reads 10–15 historical versions and usually takes 30–60 seconds.
- Old revisions are rendered by Wikipedia with today's templates, so they can differ slightly from what readers saw at the time.
- Thai and Lao have no sentence punctuation, so they are split approximately at spaces.
- Each release is installed and tested automatically on GitHub's Mac and Windows machines. The native window on Windows has not yet been confirmed on a physical PC; if it fails, the app opens in the browser instead.

### Licence

Code: Apache-2.0. The alignment scoring is adapted from the sentence-transformers bitext-mining example (Apache-2.0). Wikipedia text: CC BY-SA 4.0; credit the article links when reusing it. The installers include Microsoft's Harrier OSS v1 270M model (MIT) and open-source components such as PyTorch (BSD) and Transformers (Apache-2.0), under their own licences.

---

## 中文

### 能做什么

- **跨语言对齐**：在同一条目的两个语言版本之间，逐句找出可能的译文对，并按分数着色；悬停高亮，点击查看详情。
- **历史版本**：每一侧都可以取最新版本、某个日期当时的版本，或指定的修订号。两侧取同一日期，就是那个时间点的跨语言对齐。
- **修订对比**：两侧选同一条目的两个版本，结果标出未改动、有改动（附字面相似度）、删除和新增的句子。
- **修订历史**：列出每次修订的时间、编辑者、大小增减、摘要和标签，并标出用维基百科内容翻译工具完成的编辑。勾选两个版本即可直接比较。
- **追溯首次出现**：对一个句对，在各自条目的修订历史中查找每句首次出现的修订并比较日期，作为判断翻译方向的线索。可选允许措辞的小改动。
- **你自己的文本**：任一侧都可以粘贴文本，或打开 .txt、.md、.docx 文件。
- **导出**：Excel（句对、两侧未对齐句、元数据）、CSV 或 JSON。元数据记录修订号、链接、模型、参数和 CC BY-SA 许可说明。
- **自动保存**：每次结果都保存在你的电脑上，再次打开无需重新计算。
- **双语界面**：右上角可切换“中”“EN”“中/EN”。“中/EN”同时显示中英文，是默认模式。
- **模型选择**：提供 9 个模型，分为 5 组。“设置”页可以对比，打开结果时会自动套用该模型的推荐阈值。

### 安装

支持 Apple 芯片的 Mac（M1 及以后）和 64 位 Windows 10/11。安装包已附带默认模型（Harrier 270M），无需另外下载；使用时需要能访问维基百科。其他模型在第一次使用时下载。

**macOS**：把下面这行粘贴到“终端”，会自动下载、安装并打开：

```bash
curl -fsSL https://github.com/LukeTu/WikiAligner/releases/latest/download/install_mac.sh | bash
```

也可以从 [Releases 页面](https://github.com/LukeTu/WikiAligner/releases/latest)下载 `WikiAligner-macOS-arm64.dmg`，把应用拖到“应用程序”。第一次打开被系统拦下时，到“系统设置 → 隐私与安全性”，点“仍要打开”。

**Windows**：从 [Releases 页面](https://github.com/LukeTu/WikiAligner/releases/latest)下载并运行 `WikiAligner-Windows-x64-Setup.exe`，不需要管理员权限。如果出现 SmartScreen 提示，点“更多信息 → 仍要运行”。也可以在 PowerShell 里运行：

```powershell
irm https://github.com/LukeTu/WikiAligner/releases/latest/download/install_windows.ps1 | iex
```

出现这些提示，是因为应用没有购买 Apple 或微软的代码签名证书。

**交给 AI 部署**：如果安装包用不了，把 `WikiAligner-handoff.zip` 交给 Claude Code 这类 AI 编程助手，并告诉它：“解压后按 HANDOFF.md 把 WikiAligner 装到这台电脑上。”

Intel 芯片的 Mac 不受支持，因为目前的 PyTorch 已不再提供 Intel Mac 版本。

在中国大陆访问维基百科需要代理。应用默认使用系统代理，也可以在“设置”里另外填写。如果连不上 huggingface.co，模型下载会自动改用 hf-mirror.com 镜像。

### 和第一版相比

论文中计划的改进，这一版已经做到的：

| 论文中的计划 | 这一版的做法 |
|---|---|
| 使用 MediaWiki 的解析结果，避免丢失文本，并能取得历史版本 | 按修订号取渲染后的 HTML，保留章节、列表和图片说明，表格和信息框可选；支持任意修订版本，中文可选简繁转换 |
| 对比同一语言的不同修订（intralingual alignment） | 两侧语言相同时，自动切换为修订对比 |
| 更细的切分，找出长句中的翻译单位 | 可选句子、分句、段落三种粒度，并可选“一对多”匹配，处理拆句和合句 |
| 接入其他句向量模型 | 提供 Harrier、LaBSE、Multilingual E5、BGE-M3、MiniLM、Qwen3，也可填写任意 Hugging Face 模型名 |
| 对齐上传的文件 | 可粘贴文本，或打开 .txt、.md、.docx 文件 |

其他变化：

- 完全在你的电脑上运行，不需要部署服务器。
- 任何语言都可以作为起点，条目不再必须有英文版。
- 句子编号全程一致，屏幕显示和 Excel 导出始终对得上。
- 短条目也能正确对齐，因为近邻数 k 会随文章长度调整。
- 中文不再丢失最后一句，日语、泰语、缅甸语、高棉语可以分句。
- 翻译链接在浏览器中打开 Bing、DeepL 或 Google，应用不需要任何 API 密钥。
- 本地服务只监听 127.0.0.1，并拒绝发给其他主机名的请求。

第一版的代码保留在仓库的提交历史里。

### 模型怎么选

公开评测里没有针对“在一篇条目内找译文”的排行榜，MTEB 的 bitext mining 分数是多种任务的平均。所以这一版还用 WikiAligner 自己的对齐流程测试了每个模型（`scripts/benchmark_models.py`）：

- 语料：NTREX-128 新闻平行语料，10 种语言（中、俄、德、日、阿、韩、泰、斯瓦希里、泰米尔、阿姆哈拉）。
- 设置：每种语言 3 组，每组 300 句英文，其中一半有译文；目标语言一侧另加 150 句无关句子。使用一对一匹配，取最佳 margin 阈值下的 F1。
- 环境：Apple 芯片 Mac（MPS），2026-10-31。Windows 版只用 CPU，会慢一些。

| 模型 | 分组 | 本机 F1 | 句/秒 | 下载 | 公开评测 | 说明 |
|---|---|---|---|---|---|---|
| Harrier OSS v1 270M | 推荐（默认，随安装包附带） | 0.991 | 136 | 0.5 GB | 多语言 MTEB v2 平均 66.5 | 2026 年 4 月发布；十种语言都稳定；4 个 CPU 线程上每秒约 50 句，比 LaBSE（约 41 句）略快 |
| LaBSE | 推荐 | 0.991 | 385 | 1.9 GB | BUCC 98.8 | 论文使用的模型，结果可比较；Apple 芯片上最快；泰语略弱，输入上限 256 token |
| Harrier OSS v1 0.6B | 备选 | 0.990 | 26 | 1.2 GB | 多语言 MTEB v2 平均 69.0 | 分数和 270M 版相当，但慢得多 |
| Multilingual E5 large instruct | 备选 | 0.989 | 92 | 2.2 GB | MTEB bitext 80.1 | 召回率最高 |
| BGE-M3 | 备选 | 0.983 | 95 | 2.3 GB | MTEB bitext 79.1；2026 年稳健性研究第一梯队 | 能处理较长输入，适合按段落对齐；阿姆哈拉语较弱 |
| Multilingual E5 small | 轻量 | 0.965 | 860 | 0.5 GB | | 小而快 |
| Multilingual MiniLM | 轻量 | 0.790 | 926 | 0.5 GB | | 斯瓦希里语、泰米尔语、阿姆哈拉语上基本失效 |
| Qwen3-Embedding 0.6B | 通用检索 | 0.941 | 25 | 1.2 GB | MTEB bitext 72.2 | 找译文较弱，不建议使用 |
| Qwen3-Embedding 4B | 大模型 | 未测 | | 8 GB | MTEB bitext 79.4 | 需要 16 GB 以上内存 |

- 新闻译文比维基百科上的译文规整得多，这个测试里前五名只差约 1 个百分点。用真实条目（涅姆佐夫遇刺，英文对俄文，2015-03-10）实测时，LaBSE、Harrier 270M、E5 large、BGE-M3 按各自推荐阈值分别找出 19–26 对，其中 15 对四个模型都找到了。拿不准时，可以用两个模型各跑一次再对照。
- 各模型的分数范围不同，所以各有推荐的 margin 阈值，取值是这个测试中精确率达到 97% 的最低阈值。
- 需要指令或前缀的模型（E5、Harrier、Qwen3）会自动添加。
- 要重跑测试或加入新模型，运行 `uv run python scripts/benchmark_models.py [模型键]`。结果写入 `wikialigner/model_benchmark.json`，应用会直接读取。

来源：[MMTEB 稳健性研究](https://arxiv.org/abs/2605.31142)、[Qwen3-Embedding 报告中的 MTEB 表](https://github.com/QwenLM/Qwen3-Embedding)、[Multilingual E5 技术报告](https://arxiv.org/abs/2402.05672)、[Harrier OSS v1 模型卡](https://huggingface.co/microsoft/harrier-oss-v1-270m)、[LaBSE](https://arxiv.org/abs/2007.01852)。

### 从源码运行

macOS 双击 `scripts/start_mac.command`，Windows 双击 `scripts/start_windows.bat`。第一次运行会自动安装 [uv](https://docs.astral.sh/uv/)、Python 3.12 和依赖（约 1 GB），之后几秒即可启动。也可以用命令行：

```bash
uv run -m wikialigner            # 打开应用窗口
uv run -m wikialigner --browser  # 改用默认浏览器打开
uv run pytest                    # 运行测试（不需要联网）
```

发布新版本时，推送 `v*` 标签即可。`.github/workflows/build.yml` 会在 GitHub Actions 上打包两个平台的安装包，分别安装并运行 `packaging/smoke_test.py`，全部通过后才发布 Release。本地打包的步骤见 `HANDOFF.md`。

### 数据存放位置

| 内容 | macOS | Windows |
|---|---|---|
| 设置、保存的结果 | `~/Library/Application Support/WikiAligner` | `%LOCALAPPDATA%\WikiAligner` |
| 维基页面缓存 | `~/Library/Caches/WikiAligner` | `%LOCALAPPDATA%\WikiAligner\Cache` |
| 下载的模型 | `~/.cache/huggingface` | `%USERPROFILE%\.cache\huggingface` |
| 导出文件 | `下载/WikiAligner`（可在“设置”中更改） | 同左 |
| 日志（已安装的应用） | `~/Library/Application Support/WikiAligner/wikialigner.log` | `%LOCALAPPDATA%\WikiAligner\wikialigner.log` |

### 项目结构

```
wikialigner/
  wiki.py       维基接口：搜索、语言链接、修订列表、按修订号取 HTML（带缓存）
  extract.py    HTML 转为有序文本块
  segment.py    多语言分句与分句粒度
  models.py     模型列表、加载、向量缓存
  model_benchmark.json  本机评测结果
  align.py      margin 打分（Artetxe & Schwenk 2019）与三种匹配策略
  pipeline.py   从两个来源得到一份对齐结果
  history.py    追溯首次出现（二分查找修订历史）
  export.py     Excel、CSV、JSON 导出
  jobs.py       后台任务与结果保存
  server.py     本地 HTTP 接口
  desktop.py    启动本地服务并打开窗口
  web/          界面（纯 HTML、CSS、JS，无需构建）
tests/          单元测试与接口测试（不联网）
scripts/        双击启动脚本、模型评测
packaging/      安装包、安装脚本、冒烟测试
```

### 已知限制

- 句对只是候选结果，需要人工判断。相似度高说明两句话意思相同，不能说明其中一句译自另一句。
- 推荐阈值来自上面的新闻语料测试，没有用维基百科金标准校准。自定义模型没有评测数据，初始阈值为余弦 ≥ 0.70。
- “追溯首次出现”假设句子加入后一直保留；如果曾被删除又加回，结果是其中一次出现的时间。每次查找要读取 10–15 个历史版本，通常需要 30–60 秒。
- 旧版本由维基百科用现在的模板重新渲染，可能与当时读者看到的页面略有差异。
- 泰语和老挝语没有句末标点，只能按空格近似切分。
- 每个版本都会在 GitHub 的 Mac 和 Windows 机器上自动安装并测试。Windows 上的原生窗口还没有在实体电脑上确认；如果打不开，应用会改用浏览器。

### 许可

代码：Apache-2.0。对齐打分改写自 sentence-transformers 的 bitext mining 示例（Apache-2.0）。维基百科文本：CC BY-SA 4.0，再利用时请注明条目链接。安装包附带微软的 Harrier OSS v1 270M 模型（MIT）以及 PyTorch（BSD）、Transformers（Apache-2.0）等开源组件，它们各自遵循原有许可。
