import re

from ui_coverage_tool.config import Settings
from ui_coverage_tool.src.reports.models import CoverageReportState
from ui_coverage_tool.src.tools.logger import get_logger

logger = get_logger("UI_REPORTS_STORAGE")


class UIReportsStorage:
    def __init__(self, settings: Settings):
        self.settings = settings

    def inject_state_into_html(self, state: CoverageReportState) -> str:
        state_json = state.model_dump_json(by_alias=True)
        html_report_template_file = self.settings.html_report_template_file

        script_regex = re.compile(
            r'<script id="state" type="application/json">[\s\S]*?</script>',
            re.IGNORECASE
        )
        script_tag = f'<script id="state" type="application/json">{state_json}</script>'

        return script_regex.sub(script_tag, html_report_template_file.read_text(encoding='utf-8'))

    def save_json_report(self, state: CoverageReportState):
        json_report_file = self.settings.json_report_file

        if not json_report_file:
            logger.info("JSON report file is not configured — skipping JSON report generation.")
            return

        try:
            json_report_file.touch(exist_ok=True)
            json_report_file.write_text(state.model_dump_json(by_alias=True))
            logger.info(f'JSON report saved to {json_report_file}')
        except Exception as error:
            logger.error(f'Failed to write JSON report: {error}')

    def save_html_report(self, state: CoverageReportState):
        html_report_file = self.settings.html_report_file

        if not html_report_file:
            logger.info("HTML report file is not configured — skipping HTML report generation.")
            return

        try:
            html_report_file.touch(exist_ok=True)
            html_report_file.write_text(self.inject_state_into_html(state), encoding='utf-8')
            logger.info(f'HTML report saved to {html_report_file}')
        except Exception as error:
            logger.error(f'Failed to write HTML report: {error}')
