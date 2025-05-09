# Mermaid主题预览生成工具

这个目录包含用于生成Mermaid主题预览的工具脚本。新的系统使用Makefile来自动化预览生成，只会重新生成需要更新的文件，避免不必要的处理。

## 系统组件

系统由以下组件组成：

1. **Makefile** - 位于项目根目录，用于自动化构建过程
2. **generate_single_preview.py** - 生成单个主题的单个类型SVG预览
3. **generate_html_preview.py** - 生成单个主题的HTML预览页面
4. **generate_theme_gallery.py** - 生成展示所有主题的图库页面

## 使用说明

### 生成所有预览

要生成所有主题的所有预览（SVG和HTML）：

```bash
make previews
```

### 生成主题图库

要生成主题图库页面（需要先生成所有预览）：

```bash
make gallery
```

### 生成所有内容

一次性生成所有预览和图库：

```bash
make all
```

### 强制重新生成

如果需要强制重新生成预览（忽略已存在的文件）：

```bash
make force-previews  # 强制重新生成所有预览
make force-gallery   # 强制重新生成图库
make force-all       # 强制重新生成所有内容
```

### 清理生成的文件

```bash
make clean
```

## 为单个主题生成预览

如果只想更新某个特定主题的预览，可以直接在themes/主题名称/目录中创建或修改主题文件（theme.json和style.css），然后运行：

```bash
make themes/主题名称/flowchart_preview.svg  # 生成流程图预览
make themes/主题名称/sequence_preview.svg   # 生成序列图预览 
make themes/主题名称/class_preview.svg      # 生成类图预览
make themes/主题名称/preview.html           # 生成HTML预览页面
```

## 添加新主题

添加新主题的步骤：

1. 在`themes/`目录下创建新的主题目录，例如`themes/新主题名称/`
2. 在主题目录中创建以下文件：
   - `theme.json` - 主题配置文件
   - `style.css` - 主题样式文件
3. 运行以下命令生成预览：
   ```bash
   make themes/新主题名称/preview.html
   ```
4. 重新生成图库以包含新主题：
   ```bash
   make gallery
   ```

## 脚本直接使用

如需直接使用脚本（不通过Makefile），可以这样：

### 生成单个预览SVG

```bash
python scripts/generate_single_preview.py --theme-dir themes/主题名称 --type flowchart
python scripts/generate_single_preview.py --theme-dir themes/主题名称 --type sequence
python scripts/generate_single_preview.py --theme-dir themes/主题名称 --type class
```

### 生成单个主题的HTML预览

```bash
python scripts/generate_html_preview.py --theme-dir themes/主题名称
```

### 生成主题图库

```bash
python scripts/generate_theme_gallery.py --themes-dir themes --output themes/gallery.html
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