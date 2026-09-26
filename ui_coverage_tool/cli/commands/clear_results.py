import click

from ui_coverage_tool.config import get_settings
from ui_coverage_tool.src.tracker.storage import UICoverageTrackerStorage


def clear_results_command():
    settings = get_settings()
    try:
        UICoverageTrackerStorage(settings).clear()
    except OSError as error:
        raise click.ClickException(str(error)) from error
