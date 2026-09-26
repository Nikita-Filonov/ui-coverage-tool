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

    def clear(self) -> None:
        results_dir = self.settings.results_dir

        if not results_dir.exists():
            logger.info(f"Results directory does not exist: {results_dir}")
            return

        if not results_dir.is_dir():
            raise NotADirectoryError(f"Results path is not a directory: {results_dir}")

        protected_files = {
            path.resolve()
            for path in (self.settings.history_file, self.settings.json_report_file)
            if path is not None
        }

        removed = 0
        for file in results_dir.glob("*.json"):
            if not file.is_file() or file.resolve() in protected_files:
                continue

            try:
                file.unlink()
            except OSError as error:
                raise OSError(f"Failed to remove coverage file {file}: {error}") from error
            removed += 1

        logger.info(f"Removed {removed} coverage files from directory: {results_dir}")

    def save(self, coverage: CoverageResult):
        results_dir = self.settings.results_dir

        if not results_dir.exists():
            logger.info(f"Results directory does not exist, creating: {results_dir}")
            results_dir.mkdir(parents=True, exist_ok=True)

        result_file = results_dir.joinpath(f'{uuid.uuid4()}.json')

        try:
            result_file.write_text(coverage.model_dump_json())
        except Exception as error:
            logger.error(f"Error saving coverage data to file {result_file}: {error}")
