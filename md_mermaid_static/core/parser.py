"""
Markdown parser for extracting Mermaid code blocks.
"""

import re
import yaml
from typing import List, Tuple, Dict, Any

from md_mermaid_static.models import MermaidBlock, MermaidConfig, Theme
from md_mermaid_static.utils import logger


class MarkdownParser:
    """Markdown Parser"""

    # Support standard ```mermaid format
    MERMAID_BLOCK_PATTERN = re.compile(r"```mermaid\n(.*?)\n```", re.DOTALL)

    # Support GitHub-style ```mermaid format with extra indentation
    GITHUB_MERMAID_PATTERN = re.compile(r"```mermaid\s*\n(.*?)\n\s*```", re.DOTALL)

    # Support Mermaid directive syntax
    MERMAID_DIRECTIVE_PATTERN = re.compile(r":::mermaid\s*\n(.*?)\n:::", re.DOTALL)

    @staticmethod
    def parse_frontmatter(content: str) -> Tuple[Dict[str, Any], str]:
        """Parse frontmatter and actual content"""
        if content.startswith("---\n"):
            parts = content.split("---\n", 2)
            if len(parts) >= 3:
                try:
                    config = yaml.safe_load(parts[1])
                    logger.debug(f"Parsed config from frontmatter: {config}")
                    return config or {}, parts[2]
                except yaml.YAMLError as e:
                    logger.warning(f"Failed to parse frontmatter: {str(e)}")
                    return {}, content
        return {}, content

    @staticmethod
    def _normalize_config_keys(config: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize config keys (convert hyphens to underscores)"""
        normalized_config = {}
        for key, value in config.items():
            # Convert hyphens to underscores (e.g., render-theme -> render_theme)
            normalized_key = key.replace("-", "_")

            # Special handling for theme field name
            if normalized_key == "theme":
                normalized_key = "render_theme"

            # Handle custom theme (render-theme with string value that's not a standard theme)
            if normalized_key == "render_theme" and isinstance(value, str):
                try:
                    # Try to convert to standard theme enum
                    value = Theme(value.lower())
                except ValueError:
                    # If not a valid theme enum, it's a custom theme
                    logger.debug(f"Using custom theme: {value}")
                    # Store the original theme name in custom_theme
                    normalized_config["custom_theme"] = value
                    # Don't set render_theme for custom themes
                    continue

            normalized_config[normalized_key] = value

        logger.debug(f"Normalized config: {normalized_config}")
        return normalized_config

    def _extract_blocks(
        self, pattern: re.Pattern, markdown_content: str
    ) -> List[MermaidBlock]:
        """Extract Mermaid code blocks from Markdown content"""
        blocks = []

        for match in pattern.finditer(markdown_content):
            content = match.group(1)
            config_dict, mermaid_content = self.parse_frontmatter(content)

            # Normalize config keys
            normalized_config = self._normalize_config_keys(config_dict)

            # Calculate line numbers
            line_start = markdown_content.count("\n", 0, match.start()) + 1
            line_end = markdown_content.count("\n", 0, match.end()) + 1

            # Create block
            block = MermaidBlock(
                content=mermaid_content.strip(),
                config=MermaidConfig(**normalized_config),
                line_start=line_start,
                line_end=line_end,
            )

            # Log found code block
            logger.debug(f"Found Mermaid block (lines {line_start}-{line_end})")
            blocks.append(block)

        return blocks

    def find_mermaid_blocks(self, markdown_content: str) -> List[MermaidBlock]:
        """Find all Mermaid code blocks in Markdown content"""
        blocks = []

        # Find standard format blocks
        logger.debug("Searching for standard Mermaid blocks")
        standard_blocks = self._extract_blocks(
            self.MERMAID_BLOCK_PATTERN, markdown_content
        )
        blocks.extend(standard_blocks)
        logger.debug(f"Found {len(standard_blocks)} standard format blocks")

        # Find GitHub-style blocks
        logger.debug("Searching for GitHub-style Mermaid blocks")
        github_blocks = self._extract_blocks(
            self.GITHUB_MERMAID_PATTERN, markdown_content
        )
        # Exclude already matched blocks (avoid duplicates)
        new_github_blocks = [b for b in github_blocks if b not in blocks]
        blocks.extend(new_github_blocks)
        logger.debug(f"Found {len(new_github_blocks)} additional GitHub-style blocks")

        # Find directive style blocks
        logger.debug("Searching for directive-style Mermaid blocks")
        directive_blocks = self._extract_blocks(
            self.MERMAID_DIRECTIVE_PATTERN, markdown_content
        )
        blocks.extend(directive_blocks)
        logger.debug(f"Found {len(directive_blocks)} directive-style blocks")

        return blocks
