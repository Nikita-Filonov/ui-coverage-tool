import click

from ui_coverage_tool.cli.commands.save_report import save_report_command


@click.command(
    name="save-report",
    help="Generate a coverage report based on collected result files."
)
def save_report():
    save_report_command()


@click.group()
def cli():
    pass


cli.add_command(save_report)

if __name__ == '__main__':
    cli()
