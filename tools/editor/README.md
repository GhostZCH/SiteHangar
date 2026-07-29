# Markdown 编辑器

本地 Markdown 编辑器，用于编辑和编译站点的 Markdown 源文件。

## 功能

- 三栏布局：左侧文件树、中间编辑器、右侧实时预览
- 支持单 MD 模式（`page.md`）和多 MD 模式（`meta.md` + 章节文件）
- 多 MD 模式下支持新建/删除章节
- 剪贴板图片粘贴自动保存为文件并插入 Markdown 语法
- 编辑时自动编译（停止输入 3 秒后触发，每 1 秒检查一次）
- Ctrl+S 保存快捷键
- 可自定义数据根目录（点击工具栏文件夹图标设置）

## 启动

```powershell
cd e:\code\sitesanddata\my_sites
python tools\editor\main.py
```

## 访问

浏览器打开：http://127.0.0.1:5001

## 设置数据根目录

首次打开时默认加载 `E:\code\sitesanddata\my_sites_data\data`，可点击工具栏的文件夹图标修改。

也可通过环境变量指定：

```powershell
$env:DATA_ROOT = "E:\\your\\custom\\data\\path"
python tools\editor\main.py
```

## 依赖

```powershell
pip install -r tools\editor\requirements.txt
```
