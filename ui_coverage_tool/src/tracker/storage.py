import uuid

from ui_coverage_tool.config import Settings
from ui_coverage_tool.src.tools.logger import get_logger
from ui_coverage_tool.src.tracker.models import CoverageResult, CoverageResultList

logger = get_logger("UI_COVERAGE_TRACKER_STORAGE")


class UICoverageTrackerStorage:
    def __init__(self, settings: Settings):
        self.settings = settings

    def load(self) -> CoverageResultList:
        results_dir = self.settings.results_dir
        logger.info(f"Loading coverage results from directory: {results_dir}")

        if not results_dir.exists():
            logger.warning(f"Results directory does not exist: {results_dir}")
            return CoverageResultList(root=[])

        results = [
            CoverageResult.model_validate_json(file.read_text())
            for file in results_dir.glob("*.json") if file.is_file()
        ]

        logger.info(f"Loaded {len(results)} coverage files from directory: {results_dir}")
        return CoverageResultList(root=results)

    def save(self, coverage: CoverageResult):
        results_dir = self.settings.results_dir

        if not results_dir.exists():
            logger.info(f"Results directory does not exist, creating: {results_dir}")
            results_dir.mkdir(exist_ok=True)

        result_file = results_dir.joinpath(f'{uuid.uuid4()}.json')

        try:
            result_file.write_text(coverage.model_dump_json())
        except Exception as error:
            logger.error(f"Error saving coverage data to file {result_file}: {error}")
