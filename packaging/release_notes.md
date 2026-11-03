WikiAligner finds corresponding sentences across Wikipedia language editions and across revisions of one article. It runs on your own computer; no server is needed. The sentence model is included, so it works right after installing. Wikipedia access is still needed.

WikiAligner 在维基百科的不同语言版本之间、或同一条目的不同历史版本之间，找出彼此对应的句子。它在你自己的电脑上运行，不需要服务器。安装包已附带句向量模型，装好即可使用（仍需能访问维基百科）。

## Install / 安装

**macOS (Apple silicon, M1 or later)**. Paste this into Terminal / 把下面这行粘贴到“终端”：

```bash
curl -fsSL https://github.com/LukeTu/WikiAligner/releases/latest/download/install_mac.sh | bash
```

Or download `WikiAligner-macOS-arm64.dmg` and drag the app to Applications. The first time macOS blocks it, open System Settings → Privacy & Security and click **Open Anyway**.
也可以下载 `.dmg`，把应用拖到“应用程序”。第一次打开被系统拦下时，到“系统设置 → 隐私与安全性”，点“仍要打开”。

**Windows 10/11 (64-bit)**. Download and run `WikiAligner-Windows-x64-Setup.exe`. No administrator rights needed. If SmartScreen appears, click **More info → Run anyway**.
下载并运行 `.exe`，不需要管理员权限。如果出现 SmartScreen 提示，点“更多信息 → 仍要运行”。

Or paste this into PowerShell / 或者把下面这行粘贴到 PowerShell：

```powershell
irm https://github.com/LukeTu/WikiAligner/releases/latest/download/install_windows.ps1 | iex
```

The warnings appear because the app is not signed with a paid Apple or Microsoft certificate.
出现这些提示是因为应用没有购买 Apple 或微软的代码签名证书。

## Hand it to an AI assistant / 交给 AI 部署

If the installer does not work on your computer, give `WikiAligner-handoff.zip` to an AI coding agent such as Claude Code and say: "Unzip this and follow HANDOFF.md to install WikiAligner on this computer."

如果安装包在你的电脑上用不了，把 `WikiAligner-handoff.zip` 交给 Claude Code 这类 AI 编程助手，并告诉它：“解压后按 HANDOFF.md 把 WikiAligner 装到这台电脑上。”
