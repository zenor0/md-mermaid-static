import pymupdf


def pdf_to_svg(pdf_path, svg_dir=None):
    """将PDF文件转换为SVG文件"""
    # 打开PDF文件
    doc = pymupdf.open(pdf_path)
    svg_dir = svg_dir or "."

    # 遍历所有页面
    for page_num, page in enumerate(doc):
        svg_data = page.get_svg_image()

        # 保存SVG文件
        svg_path = f"{svg_dir}/page_{page_num + 1}.svg"
        with open(svg_path, "w", encoding="utf-8") as f:
            f.write(svg_data)


# 使用方法
import os

os.makedirs("output_folder", exist_ok=True)
pdf_to_svg("test.pdf", "output_folder")
