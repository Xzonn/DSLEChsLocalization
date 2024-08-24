# 《数码宝贝物语 遗失的进化》汉化

## 构建方式
### 前提条件
- [Python 3.10+](https://www.python.org/downloads/)（`pip install -r requirements.txt`）
- [PowerShell 5.0+](https://learn.microsoft.com/powershell/)
- [.NET 8.0 SDK](https://dotnet.microsoft.com/download/dotnet/8.0)、[dotnet-script](https://github.com/dotnet-script/dotnet-script)
- [devkitPro、devkitARM](https://devkitpro.org/wiki/Getting_Started)（`dkp-pacman -Sl nds-dev`）
- 字体文件（默认读取以下文件：`files/fonts/Zfull-GB.ttf`、`C:/Windows/Fonts/simsun.ttc`、`files/fonts/SmileySans-Oblique.otf`、`files/fonts/HYZongYiTiJF.ttf`）

### 构建
在 PowerShell 中运行：

```shell
. scripts\build_patch.ps1
```
