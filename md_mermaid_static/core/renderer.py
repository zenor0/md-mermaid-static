"""
Mermaid渲染器模块
"""

import hashlib
import logging
import platform
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import List, Optional, Tuple

import pymupdf

from ..models.cli_config import CLIConfig
from ..models.enums import OutputFormat
from ..models.mermaid_block import MermaidBlock
from ..models.mermaid_config import MermaidRenderOptions
from ..config.env import get_mermaid_cli_package

logger = logging.getLogger(__name__)


class MermaidRenderer:
    """Mermaid Chart Renderer"""

    def __init__(self, output_dir: str, cli_config: CLIConfig = CLIConfig()):
        self.output_dir = Path(output_dir)
        self.cli_config = cli_config
        self.media_dir = self.output_dir / "media"
        self.media_dir.mkdir(parents=True, exist_ok=True)

    def _get_mermaid_cli_cmd(self) -> str:
        """Get available mermaid-cli command"""
        # First check if user specified a command
        if self.cli_config.use_command != "auto":
            logger.debug(f"Using user-specified command: {self.cli_config.use_command}")
            return self.cli_config.use_command

        # Auto-detect logic
        if self._check_command_exists("pnpx"):
            logger.debug("Detected pnpx, using it for mermaid-cli")
            return "pnpx"
        logger.debug("Using npx for mermaid-cli")
        return "npx"

    def _check_command_exists(self, cmd: str) -> bool:
        """Check if command exists"""
        try:
            # First try platform-specific command check
            if platform.system() == "Windows":
                # Windows uses where command, without shell=True
                check_cmd = ["where", cmd]
                result = subprocess.run(
                    check_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
            else:
                # Linux/Mac uses which command
                check_cmd = ["which", cmd]
                result = subprocess.run(
                    check_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )

            exists = result.returncode == 0

            # If first method fails, try running command --help
            if not exists:
                try:
                    help_result = subprocess.run(
                        [cmd, "--help"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        timeout=2,  # Add timeout to avoid hang
                    )
                    exists = (
                        help_result.returncode == 0 or help_result.returncode == 1
                    )  # Some commands return 1 for --help
                    if exists:
                        logger.debug(f"Detected command {cmd} via --help")
                except Exception:
                    # Ignore this error since we've tried two methods
                    pass

            logger.debug(f"Command detection {cmd}: {exists}")
            return exists
        except Exception as e:
            logger.debug(f"Error detecting command: {cmd}, error: {str(e)}")
            return False

    def render_blocks(
        self, blocks: List[MermaidBlock]
    ) -> List[Tuple[MermaidBlock, Optional[Path]]]:
        """Render multiple Mermaid code blocks with concurrent support"""
        if not blocks:
            return []

        if self.cli_config.concurrent and len(blocks) > 1:
            logger.info(
                f"Rendering {len(blocks)} charts in concurrent mode, max workers: {self.cli_config.max_workers}"
            )
            with ThreadPoolExecutor(
                max_workers=self.cli_config.max_workers
            ) as executor:
                # Create task list
                futures = []
                for i, block in enumerate(blocks):
                    futures.append(executor.submit(self.render_block, block, i))

                # Collect results
                results = []
                for i, future in enumerate(futures):
                    try:
                        output_path = future.result()
                        results.append((blocks[i], output_path))
                        if output_path:
                            logger.info(
                                f"Chart #{i + 1} rendered successfully: {output_path}"
                            )
                        else:
                            logger.warning(f"Chart #{i + 1} rendering failed")
                    except Exception as e:
                        logger.error(
                            f"Error rendering chart #{i + 1}: {str(e)}",
                            exc_info=logger.isEnabledFor(logging.DEBUG),
                        )
                        results.append((blocks[i], None))

                return results
        else:
            # Sequential processing
            results = []
            for i, block in enumerate(blocks):
                try:
                    output_path = self.render_block(block, i)
                    results.append((block, output_path))
                    if output_path:
                        logger.info(
                            f"Chart #{i + 1} rendered successfully: {output_path}"
                        )
                    else:
                        logger.warning(f"Chart #{i + 1} rendering failed")
                except Exception as e:
                    logger.error(
                        f"Error rendering chart #{i + 1}: {str(e)}",
                        exc_info=logger.isEnabledFor(logging.DEBUG),
                    )
                    results.append((block, None))
            return results

    def render_block(self, block: MermaidBlock, index: int) -> Optional[Path]:
        """Render a single Mermaid code block"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create temporary mermaid file
            mermaid_file = Path(temp_dir) / "diagram.mmd"
            mermaid_file.write_text(block.content)

            # Generate MD5 hash as filename
            mermaid_content = block.config.model_dump_json() + "\n" + block.content
            md5_hash = hashlib.md5(mermaid_content.encode("utf-8")).hexdigest()

            # Get render options - now properly integrated with CLI config from within get_render_options
            render_options = block.get_render_options()

            # Determine output format from CLI config
            output_format = self.cli_config.output_format

            # Handle enhanced SVG mode (render to PDF first, then convert to SVG)
            actual_output_format = output_format
            if output_format == OutputFormat.ENHANCED_SVG:
                logger.info("Using enhanced SVG mode: rendering via PDF conversion")
                # Use PDF as intermediate format
                actual_output_format = OutputFormat.PDF

            # Temporary output file
            temp_output = Path(temp_dir) / f"output.{actual_output_format.value}"

            # Build render command
            cmd = self._build_render_command(mermaid_file, temp_output, render_options)

            # Display render command in debug mode
            logger.debug(f"Render command: {' '.join(cmd)}")
            # display_render_command(cmd, index)

            try:
                # Execute render command
                logger.debug(f"Executing render command: {' '.join(cmd)}")
                # Print render options
                logger.debug(
                    f"Render options: {dict(filter(lambda x: x[1], render_options.model_dump().items()))}"
                )

                result = subprocess.run(cmd, capture_output=True, text=True)

                # Always print output for debugging
                if result.stdout:
                    logger.debug(f"Command stdout: {result.stdout}")
                if result.stderr:
                    logger.debug(f"Command stderr: {result.stderr}")

                if result.returncode != 0:
                    error_msg = result.stderr
                    logger.error(
                        f"Rendering failed (code {result.returncode}): {error_msg}"
                    )
                    return None

                # Final output file
                final_output_ext = (
                    "svg"
                    if output_format == OutputFormat.ENHANCED_SVG
                    else output_format.value
                )
                final_output = self.media_dir / f"mermaid_{md5_hash}.{final_output_ext}"

                # Handle enhanced SVG mode (PDF to SVG conversion)
                if output_format == OutputFormat.ENHANCED_SVG:
                    logger.debug("Converting enhanced PDF to SVG")
                    self._convert_pdf_to_svg(temp_output, final_output)
                    return final_output

                # Handle PDF to other format conversion (if needed)
                if (
                    actual_output_format == OutputFormat.PDF
                    and output_format != OutputFormat.PDF
                ):
                    logger.debug(f"Converting PDF to {output_format.value}")
                    self._convert_pdf_to_other_format(
                        temp_output, final_output, output_format
                    )
                else:
                    # Directly copy file
                    import shutil

                    logger.debug(
                        f"Copying output file: {temp_output} to {final_output}"
                    )
                    shutil.copy2(temp_output, final_output)

                return final_output

            except Exception as e:
                error_msg = str(e)
                logger.error(
                    f"Error during rendering: {error_msg}",
                    exc_info=logger.isEnabledFor(logging.DEBUG),
                )
                return None

    def _build_render_command(
        self, input_file: Path, output_file: Path, options: MermaidRenderOptions
    ) -> List[str]:
        """Build mermaid-cli command"""
        cli_cmd = self._get_mermaid_cli_cmd()
        cmd = [
            cli_cmd,
            get_mermaid_cli_package(),
            "-i",
            str(input_file),
            "-o",
            str(output_file),
        ]

        # Add theme - only if it's a built-in theme
        # (custom themes are handled via config file and CSS)
        if options.theme and not options.custom_theme:
            cmd.extend(["-t", options.theme.value])

        # Add dimensions
        if options.width:
            cmd.extend(["-w", str(options.width)])
        if options.height:
            cmd.extend(["-H", str(options.height)])

        # Add background color - always add background color param, even if default
        if options.background_color:
            cmd.extend(["-b", options.background_color])

        # Add config file
        if options.config_file:
            config_path = Path(options.config_file)
            if config_path.exists():
                cmd.extend(["-c", str(config_path)])
                logger.debug(f"Using config file: {config_path}")
            else:
                logger.warning(f"Config file not found: {config_path}")

        # Add CSS file
        if options.css_file:
            css_path = Path(options.css_file)
            if css_path.exists():
                cmd.extend(["-C", str(css_path)])
                logger.debug(f"Using CSS file: {css_path}")
            else:
                logger.warning(f"CSS file not found: {css_path}")

        # Add scale factor
        if options.scale:
            cmd.extend(["-s", str(options.scale)])

        # Add PDF fit option
        if options.pdf_fit:
            cmd.append("-f")

        # Add SVG ID
        if options.svg_id:
            cmd.extend(["-I", options.svg_id])

        return cmd

    def _convert_pdf_to_svg(self, pdf_path: Path, svg_path: Path):
        """Convert PDF to SVG"""
        logger.debug(f"Converting PDF to SVG: {pdf_path} -> {svg_path}")
        doc = pymupdf.open(str(pdf_path))
        page = doc[0]  # Get first page
        svg_data = page.get_svg_image()
        svg_path.write_text(svg_data, encoding="utf-8")
        doc.close()

    def _convert_pdf_to_png(self, pdf_path: Path, png_path: Path, dpi: int = 300):
        """Convert PDF to PNG"""
        logger.debug(f"Converting PDF to PNG: {pdf_path} -> {png_path}, DPI: {dpi}")
        doc = pymupdf.open(str(pdf_path))
        page = doc[0]  # Get first page
        pix = page.get_pixmap(dpi=dpi)
        pix.save(str(png_path))
        doc.close()

    def _convert_pdf_to_other_format(
        self, pdf_path: Path, output_path: Path, format: OutputFormat
    ):
        """Convert PDF to other formats"""
        if format == OutputFormat.SVG or format == OutputFormat.ENHANCED_SVG:
            self._convert_pdf_to_svg(pdf_path, output_path)
        elif format == OutputFormat.PNG:
            self._convert_pdf_to_png(pdf_path, output_path)
        else:
            logger.warning(f"Conversion from PDF to {format.value} is not supported")
