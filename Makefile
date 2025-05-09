# Mermaid主题预览生成Makefile

# 查找所有主题目录
THEME_DIRS := $(wildcard themes/*)
# 过滤掉非目录项
THEME_DIRS := $(filter-out themes/gallery.html themes/README.md, $(THEME_DIRS))

# 为每个主题生成三种预览SVG文件路径
FLOWCHART_PREVIEWS := $(patsubst themes/%,themes/%/flowchart_preview.svg,$(THEME_DIRS))
SEQUENCE_PREVIEWS := $(patsubst themes/%,themes/%/sequence_preview.svg,$(THEME_DIRS))
CLASS_PREVIEWS := $(patsubst themes/%,themes/%/class_preview.svg,$(THEME_DIRS))

# 所有预览文件
ALL_PREVIEWS := $(FLOWCHART_PREVIEWS) $(SEQUENCE_PREVIEWS) $(CLASS_PREVIEWS)
# HTML预览文件
HTML_PREVIEWS := $(patsubst themes/%,themes/%/preview.html,$(THEME_DIRS))
# 图库HTML文件
GALLERY_HTML := themes/gallery.html

# 默认目标：生成所有预览和图库
all: previews gallery

# 生成所有预览
previews: $(ALL_PREVIEWS) $(HTML_PREVIEWS)

# 生成图库HTML
gallery: $(GALLERY_HTML)

# 规则：生成流程图预览
themes/%/flowchart_preview.svg: themes/%/theme.json themes/%/style.css
	@echo "生成 $@ 预览..."
	@python3 scripts/generate_single_preview.py --theme-dir $(dir $@) --type flowchart

# 规则：生成序列图预览
themes/%/sequence_preview.svg: themes/%/theme.json themes/%/style.css
	@echo "生成 $@ 预览..."
	@python3 scripts/generate_single_preview.py --theme-dir $(dir $@) --type sequence

# 规则：生成类图预览
themes/%/class_preview.svg: themes/%/theme.json themes/%/style.css
	@echo "生成 $@ 预览..."
	@python3 scripts/generate_single_preview.py --theme-dir $(dir $@) --type class

# 规则：生成HTML预览
themes/%/preview.html: themes/%/flowchart_preview.svg themes/%/sequence_preview.svg themes/%/class_preview.svg
	@echo "生成 $@ 预览HTML..."
	@python3 scripts/generate_html_preview.py --theme-dir $(dir $@)

# 规则：生成图库HTML
$(GALLERY_HTML): $(HTML_PREVIEWS)
	@echo "生成主题图库..."
	@python3 scripts/generate_theme_gallery.py --themes-dir themes --output $(GALLERY_HTML)

# 强制重新生成所有预览
force-previews:
	@echo "强制重新生成所有预览..."
	@rm -f $(ALL_PREVIEWS) $(HTML_PREVIEWS)
	@$(MAKE) previews

# 强制重新生成图库
force-gallery:
	@echo "强制重新生成图库..."
	@rm -f $(GALLERY_HTML)
	@$(MAKE) gallery

# 强制重新生成所有
force-all:
	@echo "强制重新生成所有文件..."
	@rm -f $(ALL_PREVIEWS) $(HTML_PREVIEWS) $(GALLERY_HTML)
	@$(MAKE) all

# 清理所有生成文件
clean:
	@echo "清理所有生成的预览文件..."
	@rm -f $(ALL_PREVIEWS) $(HTML_PREVIEWS) $(GALLERY_HTML)

.PHONY: all previews gallery force-previews force-gallery force-all clean 