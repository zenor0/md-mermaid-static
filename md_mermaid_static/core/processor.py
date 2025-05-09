"""
Markdown processor that handles the conversion of Markdown files with Mermaid diagrams to output files.
"""

from pathlib import Path
from typing import List, Tuple

from md_mermaid_static.models import MermaidBlock, CLIConfig
from md_mermaid_static.utils import logger, display_mermaid_block, display_summary
from .parser import MarkdownParser
from .renderer import MermaidRenderer


class MarkdownProcessor:
    """Markdown Processor"""

    def __init__(self, input_file: str, cli_config: CLIConfig = CLIConfig()):
        self.input_file = Path(input_file)
        self.output_dir = Path(cli_config.output_dir)
        # Store reference to CLI config, but also rely on singleton for consistency
        self.cli_config = cli_config
        # Pass singleton instance to renderer to ensure consistency
        self.renderer = MermaidRenderer(
            cli_config.output_dir, CLIConfig.get_instance() or cli_config
        )

    def process(self) -> Path:
        """Process Markdown file"""
        logger.info(f"Processing file: {self.input_file}")

        # Read input file
        content = self.input_file.read_text(encoding="utf-8")

        # Parse Mermaid code blocks
        parser = MarkdownParser()
        blocks = parser.find_mermaid_blocks(content)

        if not blocks:
            logger.warning("No Mermaid code blocks found")
            return self._save_output(content)

        logger.info(f"Found {len(blocks)} Mermaid code blocks")

        # Display all code block details in debug mode
        for i, block in enumerate(blocks):
            display_mermaid_block(block, i)

        # Render all code blocks
        logger.info("Starting chart rendering...")

        # Process all code blocks concurrently or sequentially
        rendered_blocks = self.renderer.render_blocks(blocks)

        logger.info(f"Completed rendering {len(blocks)} charts")

        # Update Markdown content
        new_content = self._replace_blocks(content, rendered_blocks)

        # Count successful and failed renders
        success_count = sum(1 for _, path in rendered_blocks if path is not None)
        failed_count = len(rendered_blocks) - success_count

        # Save output file
        output_file = self._save_output(new_content)

        # Display processing summary
        display_summary(
            total_blocks=len(blocks),
            success_count=success_count,
            failed_count=failed_count,
            output_file=output_file,
        )

        return output_file

    def _replace_blocks(
        self, content: str, rendered_blocks: List[Tuple[MermaidBlock, Path]]
    ) -> str:
        """Replace Mermaid code blocks in Markdown"""
        lines = content.split("\n")
        offset = 0

        for block, image_path in rendered_blocks:
            # Check if image path is empty
            if image_path is None:
                logger.warning(
                    f"Chart at line {block.line_start} failed to render, keeping original code block"
                )
                continue

            # Calculate relative path
            rel_path = image_path.relative_to(self.output_dir)

            # Create new image reference
            image_ref = f"![{block.config.caption or ''}]({rel_path})"

            # Replace original code block
            start_idx = block.line_start - 1 + offset
            end_idx = block.line_end - 1 + offset
            lines[start_idx : end_idx + 1] = [image_ref]

            logger.debug(
                f"Replaced code block at lines {block.line_start}-{block.line_end} with image: {rel_path}"
            )

            # Update offset
            offset += 1 - (end_idx - start_idx + 1)

        return "\n".join(lines)

    def _save_output(self, content: str) -> Path:
        """Save output file"""
        output_file = self.output_dir / self.input_file.name
        output_file.write_text(content, encoding="utf-8")
        logger.debug(f"Saved output file: {output_file}")
        return output_file
