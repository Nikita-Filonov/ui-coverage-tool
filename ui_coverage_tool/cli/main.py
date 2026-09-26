import click

from ui_coverage_tool.cli.commands.copy_report import copy_report_command
from ui_coverage_tool.cli.commands.print_config import print_config_command
from ui_coverage_tool.cli.commands.save_report import save_report_command
from ui_coverage_tool.cli.commands.clear_results import clear_results_command


@click.command(
    name="save-report",
    help="Generate a coverage report based on collected result files."
)
def save_report():
    save_report_command()


@click.command(name="copy-report", help="Internal command to update report template.")
def copy_report():
    copy_report_command()


@click.command(
    name="print-config",
    help="Print the resolved configuration to the console."
)
def show_config():
    print_config_command()


@click.command(
    name="clear-results",
    help="Remove collected coverage result files before a new test run."
)
def clear_results():
    clear_results_command()


@click.group()
def cli():
    pass


cli.add_command(save_report)
cli.add_command(copy_report)
cli.add_command(show_config)
cli.add_command(clear_results)

if __name__ == '__main__':
    cli()
