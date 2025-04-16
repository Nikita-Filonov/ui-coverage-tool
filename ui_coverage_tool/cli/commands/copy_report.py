import pathlib
import shutil

from ui_coverage_tool.src.tools.logger import get_logger

logger = get_logger("COPY_REPORT")


def copy_report_command():
    source_file = pathlib.Path("./submodules/ui-coverage-report/build/index.html")
    destination_file = pathlib.Path("./ui_coverage_tool/src/reports/templates/index.html")

    logger.info(f"Starting to copy report from {source_file} to {destination_file}")

    if not source_file.exists():
        logger.error(f"Source file does not exist: {source_file}")
        return

    try:
        shutil.copy(src=source_file, dst=destination_file)
        logger.info(f"Successfully copied the report to {destination_file}")
    except Exception as error:
        logger.error(f"Error copying the report: {error}")
