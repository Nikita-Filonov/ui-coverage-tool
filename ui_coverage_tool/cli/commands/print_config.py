from ui_coverage_tool.config import get_settings
from ui_coverage_tool.src.tools.logger import get_logger

logger = get_logger("PRINT_CONFIG")


def print_config_command():
    settings = get_settings()
    logger.info(settings.model_dump_json(indent=2))
