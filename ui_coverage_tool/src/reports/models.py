from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

from ui_coverage_tool.config import Settings, AppConfig
from ui_coverage_tool.src.coverage.models import AppCoverage
from ui_coverage_tool.src.tools.types import AppKey


class CoverageReportConfig(BaseModel):
    apps: list[AppConfig]


class CoverageReportState(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    config: CoverageReportConfig
    created_at: datetime = Field(alias="createdAt", default_factory=datetime.now)
    apps_coverage: dict[AppKey, AppCoverage] = Field(alias="appsCoverage", default_factory=dict)

    @classmethod
    def init(cls, settings: Settings):
        return CoverageReportState(
            config=CoverageReportConfig(apps=settings.apps)
        )
