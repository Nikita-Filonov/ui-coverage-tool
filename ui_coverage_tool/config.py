import importlib.metadata
import importlib.resources
import os
from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, HttpUrl
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
    YamlConfigSettingsSource,
    JsonConfigSettingsSource,
    PydanticBaseSettingsSource,
)

from ui_coverage_tool.src.tools.types import AppKey, AppName


class AppConfig(BaseModel):
    key: AppKey
    url: HttpUrl
    name: AppName
    tags: list[str] | None = None
    repository: HttpUrl | None = None


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        extra='allow',

        env_file=os.path.join(os.getcwd(), ".env"),
        env_prefix="UI_COVERAGE_",
        env_file_encoding="utf-8",
        env_nested_delimiter=".",

        yaml_file=os.path.join(os.getcwd(), "ui_coverage_config.yaml"),
        yaml_file_encoding="utf-8",

        json_file=os.path.join(os.getcwd(), "ui_coverage_config.json"),
        json_file_encoding="utf-8"
    )

    apps: list[AppConfig]

    results_dir: Path = Path(os.path.join(os.getcwd(), "coverage-results"))

    history_file: Path | None = Path(os.path.join(os.getcwd(), "coverage-history.json"))
    history_retention_limit: int = 30

    html_report_file: Path | None = Path(os.path.join(os.getcwd(), "index.html"))
    json_report_file: Path | None = Path(os.path.join(os.getcwd(), "coverage-report.json"))

    @property
    def html_report_template_file(self):
        try:
            return importlib.resources.files("ui_coverage_tool.src.reports.templates") / "index.html"
        except importlib.metadata.PackageNotFoundError:
            return Path(os.path.join(os.getcwd(), "ui_coverage_tool/src/reports/templates/index.html"))

    @classmethod
    def settings_customise_sources(
            cls,
            settings_cls: type[BaseSettings],
            init_settings: PydanticBaseSettingsSource,
            env_settings: PydanticBaseSettingsSource,
            dotenv_settings: PydanticBaseSettingsSource,
            file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            YamlConfigSettingsSource(cls),
            JsonConfigSettingsSource(cls),
            env_settings,
            dotenv_settings,
            init_settings,
        )


@lru_cache(maxsize=None)
def get_settings() -> Settings:
    return Settings()
