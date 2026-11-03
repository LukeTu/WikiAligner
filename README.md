# WikiAligner 0.2

在维基百科的不同语言版本之间、或同一条目的不同历史版本之间，找出彼此对应的句子。
它是一个桌面应用，在 Windows 和 macOS 上本地运行，不需要部署服务器。

*WikiAligner finds corresponding sentences across Wikipedia language editions, or across two revisions of one article. It runs locally on Windows and macOS; no server needed.*

## 能做什么

- **跨语言对齐**：同一条目的两个语言版本，逐句找出可能的译文对，按分数着色；悬停高亮，点击查看详情。
- **历史版本**：每一侧都可以取“最新”“某日期当时的版本”或“指定修订号”。两侧取同一日期，就是那个时间点的跨语言对齐。
- **修订对比**：两侧选同一条目的两个版本，结果标出未改动、有改动（附字面相似度）、删除和新增的句子。
- **修订历史浏览**：列出修订（时间、编辑者、大小增减、摘要、标签），用内容翻译工具（Content Translation）完成的编辑会单独标出。勾选两个版本即可直接比较。
- **追溯首次出现**：对一个句对，按修订历史二分查找，找出两句各自首次出现的修订，并比较先后。这是判断翻译方向的线索，可选允许措辞的小改动。
- **本地文本**：任一侧都可以粘贴文本或打开 .txt / .md / .docx 文件。
- **导出**：Excel（句对、两侧未对齐句、元数据四个工作表）、CSV、JSON。元数据含修订号、链接、模型、参数和 CC BY-SA 许可说明。
- **自动保存**：每次结果都保存在本机，“记录”页可直接打开，无需重算。
- **双语界面**：右上角可切换“中”“EN”“中/EN”（中英对照，默认）。对照模式下按钮和标签同时显示两种语言，较长的说明分两行显示。
- **模型选择**：内置 8 个模型，按“推荐、高精度、经典、轻量、大模型”分组。设置页有对比表，列出本机实测 F1、速度、下载大小、语言数、许可和公开评测来源；打开结果时自动套用该模型的推荐阈值。

## 和第一版相比

论文（TC44, 2022）讨论部分计划的改进，这一版已经做到的：

| 论文中的计划 | 0.2 的做法 |
|---|---|
| 用 MediaWiki PARSE 接口取 HTML，避免丢文本，并能对齐历史版本 | 按修订号取渲染后的 HTML，保留章节、列表和图片说明，表格和信息框可选；支持任意历史版本，中文可选简繁转换 |
| 同语言的修订对比（intralingual alignment） | 两侧同语言时自动切换为修订对比模式 |
| 更细的切分，找出长句中的翻译单位 | 句子、分句、段落三种粒度；可选“一对多”匹配，处理拆句、合句 |
| 接入其他句向量模型 | 内置 LaBSE、多语言 MiniLM、MPNet、BGE-M3，也可填写任意 Hugging Face 模型名 |
| 支持上传文件 | 支持粘贴文本，或打开 txt / md / docx |

评审报告指出的问题也一并修正：

- 删除了写在前端的百度翻译密钥，右键翻译改为在 Bing、DeepL 或 Google 的网页版中打开。**旧密钥仍需在百度翻译开放平台重置。**
- 句子只生成一次，编号全程一致，不再出现网页与 Excel 编号错位。
- 近邻数 k 随文章长度自动缩小，短条目也能对齐；不再写死 768 维，任意模型都能用。
- 中文不再丢失最后一句；日语、泰语、缅甸语、高棉语可以正确分句；pysbd 对 “Sr.”“Dr.” 等称谓的误切已修正。
- 不再从文件名反推参数，语言代码和带下划线的路径都不会出错；用户输入不进入文件路径。
- 不再要求条目有英文版，任何语言都可以作为起点。
- 去掉了 JSON 文件队列，改为带状态的后台任务；失败时界面显示具体原因。
- 只在 127.0.0.1 上监听，并拒绝其他主机名的请求。
- 统一使用 pathlib，Windows 和 macOS 用同一套代码。

## 模型怎么选

公开评测里没有专门针对“在一篇条目里找译文”的排行榜，MTEB / MMTEB 的 bitext mining 分数是多种任务的平均。所以除了列出公开结果，这一版还用 WikiAligner 自己的对齐流程做了本机测试（`scripts/benchmark_models.py`）：

- 语料：NTREX-128 新闻平行语料，10 种语言（中、俄、德、日、阿、韩、泰、斯瓦希里、泰米尔、阿姆哈拉）。
- 设置：每种语言 3 组，每组 300 句英文，其中一半有译文；目标语言一侧另加 150 句无关句子；用一对一匹配，按 margin 阈值计算 F1。
- 环境：Apple 芯片 Mac（MPS），2026-10-31。表中速度是 MPS 上的结果；Windows 版只用 CPU，会慢一些。

| 模型 | 分组 | 本机 F1 | 速度（句/秒） | 下载 | 公开评测 | 说明 |
|---|---|---|---|---|---|---|
| LaBSE | 推荐 | 0.991 | 385 | 1.9 GB | BUCC 98.8 | 与 Harrier 270M 并列最好，Apple 芯片上最快；泰语略弱，输入上限 256 token |
| Harrier OSS v1 270M | 推荐（默认，随安装包附带） | 0.991 | 136 | 0.5 GB | MMTEB v2 66.5 | 2026 年 4 月发布；十种语言都稳定；纯 CPU 上每秒约 50 句，比 LaBSE（约 41 句）略快 |
| Harrier OSS v1 0.6B | 备选 | 0.990 | 26 | 1.2 GB | MMTEB v2 69.0 | 和 270M 版相当，但慢得多 |
| Multilingual E5 large instruct | 备选 | 0.989 | 92 | 2.2 GB | MTEB bitext 80.1 | 召回率最高 |
| BGE-M3 | 备选 | 0.983 | 95 | 2.3 GB | MTEB bitext 79.1；2026 稳健性研究第一梯队 | 能处理较长输入，适合按段落对齐；阿姆哈拉语稍弱 |
| Multilingual E5 small | 轻量 | 0.965 | 860 | 0.5 GB | | 小而快 |
| Multilingual MiniLM | 轻量 | 0.790 | 926 | 0.5 GB | | 斯瓦希里语、泰米尔语、阿姆哈拉语上基本失效 |
| Qwen3-Embedding 0.6B | 通用检索 | 0.941 | 25 | 1.2 GB | MTEB bitext 72.2 | 找译文较弱，不建议 |
| Qwen3-Embedding 4B | 大模型 | 未测 | | 8 GB | MTEB bitext 79.4 | 需要 16 GB 以上内存 |

几点说明：

- 新闻译文比维基百科上的译文规整得多，这个测试里前五名的差距只有约 1 个百分点。用涅姆佐夫条目（2015-03-10 英文版对俄文版）实测时，LaBSE、Harrier 270M、E5-large、BGE-M3 按各自推荐阈值分别找出 19–26 对，其中 15 对四个模型都找到了。拿不准时，可以用两个模型各跑一次，再对照结果。
- 每个模型的分数分布不同（例如 E5 的余弦普遍在 0.8 以上），不能共用一个阈值。应用会按本机测试为每个模型设定推荐的 margin 阈值：精确率达到 97% 的最低阈值。
- 指令模型（E5、Harrier、Qwen3）需要的提示词已自动添加。
- 测试可以重跑，也可以加入新模型：`uv run python scripts/benchmark_models.py [模型键…]`，结果写入 `wikialigner/model_benchmark.json`，应用会直接读取。

来源：[MMTEB 稳健性研究（arXiv 2605.31142）](https://arxiv.org/abs/2605.31142)、[Qwen3-Embedding 报告中的 MTEB 多语言表](https://github.com/QwenLM/Qwen3-Embedding)、[Multilingual E5 技术报告](https://arxiv.org/abs/2402.05672)、[Harrier OSS v1 模型卡](https://huggingface.co/microsoft/harrier-oss-v1-270m)、[LaBSE](https://arxiv.org/abs/2007.01852)。

## 安装

支持 Apple 芯片的 Mac（M1 及以后）和 64 位 Windows 10/11。安装包已附带默认模型（Harrier 270M），装好即可使用；使用时需要能访问维基百科。其他模型在第一次使用时下载。

从 [Releases 页面](https://github.com/LukeTu/WikiAligner/releases/latest) 安装：

**macOS**：把下面这行粘贴到“终端”，会自动下载、安装并打开：

```bash
curl -fsSL https://github.com/LukeTu/WikiAligner/releases/latest/download/install_mac.sh | bash
```

也可以下载 `WikiAligner-macOS-arm64.dmg`，把应用拖到“应用程序”。第一次打开时系统会拦下，到“系统设置 → 隐私与安全性”点“仍要打开”。

**Windows**：下载并运行 `WikiAligner-Windows-x64-Setup.exe`，不需要管理员权限。如果出现 SmartScreen 提示，点“更多信息 → 仍要运行”。也可以在 PowerShell 里运行：

```powershell
irm https://github.com/LukeTu/WikiAligner/releases/latest/download/install_windows.ps1 | iex
```

出现这些提示，是因为应用没有购买 Apple（每年 99 美元）或微软的代码签名证书。

**交给 AI 部署**：如果安装包用不了，把 `WikiAligner-handoff.zip` 交给 Claude Code 这类 AI 编程助手，告诉它“解压后按 HANDOFF.md 把 WikiAligner 装到这台电脑上”。

Intel 芯片的 Mac 不受支持，因为目前的 PyTorch 已不再提供 Intel Mac 版本。

## 从源码运行

- macOS：双击 `scripts/start_mac.command`
- Windows：双击 `scripts/start_windows.bat`

第一次运行会自动安装 [uv](https://docs.astral.sh/uv/)、Python 3.12 和依赖（约 1 GB），之后几秒即可启动。也可以用命令行：

```bash
uv run -m wikialigner            # 打开应用窗口
uv run -m wikialigner --browser  # 改用默认浏览器打开
```

### 发布新版本

推送 `v*` 标签后，`.github/workflows/build.yml` 会在 GitHub Actions 上打包 Mac 和 Windows 版，把安装包实际安装一遍并跑 `packaging/smoke_test.py`，全部通过后才发布 Release。PyInstaller 不能跨平台打包，所以两个版本都要在对应系统上构建。本地打包的步骤见 `HANDOFF.md`。

### 中国大陆用户

- 访问维基百科需要代理。应用默认使用系统代理，也可以在“设置”里单独填写代理地址。
- 下载其他模型时，如果连不上 huggingface.co，应用会自动改用 hf-mirror.com 镜像，也可以在“设置”里手动指定。

## 数据存放位置

| 内容 | macOS | Windows |
|---|---|---|
| 设置、保存的结果 | `~/Library/Application Support/WikiAligner` | `%LOCALAPPDATA%\WikiAligner` |
| 维基页面缓存 | `~/Library/Caches/WikiAligner` | `%LOCALAPPDATA%\WikiAligner\Cache` |
| 模型 | `~/.cache/huggingface` | `%USERPROFILE%\.cache\huggingface` |
| 导出文件 | `下载/WikiAligner`（可在设置中更改） | 同左 |
| 运行日志（已安装的应用） | `~/Library/Application Support/WikiAligner/wikialigner.log` | `%LOCALAPPDATA%\WikiAligner\wikialigner.log` |

## 项目结构

```
wikialigner/
  wiki.py       维基接口：搜索、语言链接、修订列表、按修订号取 HTML（磁盘缓存）
  extract.py    HTML → 有序文本块（标题、段落、列表、图片说明、可选表格和信息框）
  segment.py    多语言分句与分句粒度
  models.py     模型注册表（含提示词、分组、说明）、懒加载、向量缓存
  model_benchmark.json  本机模型评测结果
  align.py      margin 打分（Artetxe & Schwenk 2019）与三种匹配策略
  pipeline.py   从两个来源到一份对齐结果
  history.py    追溯句子首次出现（二分查找修订历史）
  export.py     Excel / CSV / JSON 导出
  jobs.py       后台任务与结果保存
  server.py     本地 HTTP 接口
  desktop.py    启动本地服务并打开窗口
  web/          界面（纯 HTML/CSS/JS，无需构建）
tests/          单元测试与接口测试（不联网）
scripts/        双击启动脚本
packaging/      PyInstaller 配置
```

## 测试

```bash
uv run pytest
```

## 已知限制

- 默认按余弦相似度 ≥ 0.70 显示句对。这个阈值来自少量样例，还没有经过金标准评测校准。
- “追溯首次出现”假设句子加入后一直保留；如果曾被删除又加回，结果是其中一次出现的时间。每次查找要读取 10–15 个历史版本，通常需要半分钟到一分钟。
- 旧版本由维基百科用现在的模板重新渲染，与当年读者看到的页面可能略有差异。
- 分句对没有句末标点的语言（如泰语）只能按空格近似切分。

## 许可

代码：Apache-2.0。对齐打分改写自 sentence-transformers 的 bitext mining 示例（Apache-2.0）。
维基百科文本：CC BY-SA 4.0，再利用时请注明条目链接。
安装包附带微软的 Harrier OSS v1 270M 模型（MIT 许可）以及 PyTorch（BSD）、Transformers（Apache-2.0）等开源组件，它们各自遵循原有许可。
