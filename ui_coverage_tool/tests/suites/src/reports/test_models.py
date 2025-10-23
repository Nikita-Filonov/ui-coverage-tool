from datetime import datetime

from ui_coverage_tool.config import Settings, AppConfig
from ui_coverage_tool.src.coverage.models import AppCoverage
from ui_coverage_tool.src.reports.models import (
    CoverageReportState,
    CoverageReportConfig,
)


# -------------------------------
# TEST: init
# -------------------------------

def test_init_creates_valid_report_state(settings: Settings) -> None:
    state = CoverageReportState.init(settings)

    assert isinstance(state, CoverageReportState)
    assert isinstance(state.config, CoverageReportConfig)
    assert isinstance(state.created_at, datetime)

    assert isinstance(state.apps_coverage, dict)
    assert state.apps_coverage == {}

    # Проверяем, что конфиг скопировал все приложения из настроек
    assert len(state.config.apps) == len(settings.apps)
    first_app = state.config.apps[0]

    assert isinstance(first_app, AppConfig)
    assert first_app.key == settings.apps[0].key
    assert str(first_app.url) == str(settings.apps[0].url)


def test_init_with_empty_settings() -> None:
    empty_settings = Settings(apps=[])
    state = CoverageReportState.init(empty_settings)

    assert isinstance(state, CoverageReportState)
    assert isinstance(state.config, CoverageReportConfig)
    assert isinstance(state.created_at, datetime)
    assert isinstance(state.apps_coverage, dict)

    assert state.config.apps == empty_settings.apps
    assert state.apps_coverage == {}


def test_init_creates_distinct_instances(settings: Settings) -> None:
    """init() создаёт независимые экземпляры состояния."""
    state1 = CoverageReportState.init(settings)
    state2 = CoverageReportState.init(settings)

    assert state1 is not state2
    assert state1.created_at != state2.created_at

    app1 = state1.config.apps[0]
    app2 = state2.config.apps[0]

    assert isinstance(app1, AppConfig)
    assert isinstance(app2, AppConfig)
    assert app1.key == app2.key
    assert str(app1.url) == str(app2.url)


# -------------------------------
# TEST: structure integrity
# -------------------------------

def test_coverage_report_state_allows_adding_apps(settings: Settings) -> None:
    state = CoverageReportState.init(settings)

    app_key = settings.apps[0].key
    app_coverage = AppCoverage(history=[], elements=[])

    state.apps_coverage[app_key] = app_coverage

    assert app_key in state.apps_coverage
    assert isinstance(state.apps_coverage[app_key], AppCoverage)
    assert state.apps_coverage[app_key].history == []
    assert state.apps_coverage[app_key].elements == []
