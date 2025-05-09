# 主题预览生成工具

这个目录包含用于生成主题预览图像和图库的脚本。

## 生成主题预览

`generate_theme_previews.py` 脚本会为每个主题生成预览图像，并将其保存到对应的主题文件夹中。预览图像包含流程图、序列图和类图的示例。

### 使用方法

```bash
# 使用默认主题目录 (./themes)
python scripts/generate_theme_previews.py

# 指定自定义主题目录
python scripts/generate_theme_previews.py --themes-dir /path/to/themes
```

### 生成的预览文件

脚本会在每个主题文件夹中生成以下文件：

- `flowchart_preview.svg` - 流程图预览
- `sequence_preview.svg` - 序列图预览
- `class_preview.svg` - 类图预览
- `preview.html` - 包含所有预览的HTML文件

## 生成主题图库

`generate_theme_gallery.py` 脚本会生成一个HTML页面，展示所有主题的预览图像。这个页面可以作为主题选择的参考。

### 使用方法

```bash
# 使用默认主题目录 (./themes) 和输出文件 (./themes/gallery.html)
python scripts/generate_theme_gallery.py

# 指定自定义主题目录和输出文件
python scripts/generate_theme_gallery.py --themes-dir /path/to/themes --output /path/to/gallery.html
```

### 图库特点

- 展示所有主题的流程图预览
- 提供每个主题的基本信息（基础主题、深色/浅色模式）
- 链接到每个主题的完整预览页面
- 响应式布局，适应不同屏幕大小

## 完整工作流程

推荐的工作流程是先生成预览，然后生成图库：

```bash
# 生成所有主题的预览
python scripts/generate_theme_previews.py

# 生成主题图库
python scripts/generate_theme_gallery.py

# 在浏览器中打开图库
# Linux/macOS
xdg-open themes/gallery.html  # Linux
open themes/gallery.html      # macOS

# Windows
start themes/gallery.html     # Windows
```

## 要求

- Node.js 和 npm/npx 已安装
- Mermaid CLI 可通过 npx 使用：`npx @mermaid-js/mermaid-cli`
- Python 3.6 或更高版本

## 在文档中使用预览图像

生成的预览图像可以在主题文档中使用，例如：

```markdown
# 深海蓝调主题

![流程图预览](flowchart_preview.svg)

这个主题使用深蓝色调和水波纹效果，适合海洋相关或深度分析的图表。
``` 