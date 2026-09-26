import json
from pathlib import Path

import pytest

from ui_coverage_tool.config import Settings, get_settings


@pytest.fixture
def config_files(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> dict[str, Path]:
    files = {
        "yaml_file": tmp_path / "ui_coverage_config.yaml",
        "json_file": tmp_path / "ui_coverage_config.json",
        "env_file": tmp_path / ".env",
    }
    for source, path in files.items():
        monkeypatch.setitem(Settings.model_config, source, str(path))
    return files


def test_settings_loads_yaml_before_json_and_init_values(config_files: dict[str, Path]) -> None:
    config_files["yaml_file"].write_text(
        "apps:\n"
        "  - key: yaml-app\n"
        "    name: YAML App\n"
        "    url: https://yaml.example.com\n"
        "results_dir: ./yaml-results\n",
        encoding="utf-8",
    )
    config_files["json_file"].write_text(
        json.dumps({
            "apps": [{"key": "json-app", "name": "JSON App", "url": "https://json.example.com"}],
            "history_retention_limit": 12,
        }),
        encoding="utf-8",
    )

    settings = Settings(
        apps=[{"key": "init-app", "name": "Init App", "url": "https://init.example.com"}],
        history_retention_limit=3,
    )

    assert [app.key for app in settings.apps] == ["yaml-app"]
    assert settings.results_dir == Path("yaml-results")
    assert settings.history_retention_limit == 12


def test_settings_loads_json_when_yaml_is_missing(config_files: dict[str, Path]) -> None:
    config_files["json_file"].write_text(
        json.dumps({
            "apps": [{"key": "json-app", "name": "JSON App", "url": "https://json.example.com"}],
            "history_file": None,
        }),
        encoding="utf-8",
    )

    settings = Settings()

    assert settings.apps[0].key == "json-app"
    assert settings.history_file is None


def test_settings_env_overrides_dotenv_and_init_values(
        config_files: dict[str, Path],
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    config_files["env_file"].write_text(
        'UI_COVERAGE_APPS=[{"key":"dotenv-app","name":"Dotenv App","url":"https://dotenv.example.com"}]\n'
        "UI_COVERAGE_HISTORY_RETENTION_LIMIT=7\n",
        encoding="utf-8",
    )
    monkeypatch.setenv(
        "UI_COVERAGE_APPS",
        json.dumps([{"key": "env-app", "name": "Env App", "url": "https://env.example.com"}]),
    )

    settings = Settings(
        apps=[{"key": "init-app", "name": "Init App", "url": "https://init.example.com"}],
        history_retention_limit=3,
    )

    assert [app.key for app in settings.apps] == ["env-app"]
    assert settings.history_retention_limit == 7


def test_settings_finds_packaged_html_template(config_files: dict[str, Path]) -> None:
    settings = Settings(apps=[])

    assert settings.html_report_template_file.is_file()
    assert '<script id="state" type="application/json">' in settings.html_report_template_file.read_text(
        encoding="utf-8"
    )


def test_get_settings_reloads_config_after_cache_is_cleared(config_files: dict[str, Path]) -> None:
    def write_config(key: str) -> None:
        config_files["json_file"].write_text(
            json.dumps({"apps": [{"key": key, "name": key, "url": "https://example.com"}]}),
            encoding="utf-8",
        )

    write_config("first-app")
    get_settings.cache_clear()
    try:
        first = get_settings()
        write_config("second-app")

        assert get_settings() is first
        assert first.apps[0].key == "first-app"

        get_settings.cache_clear()
        assert get_settings().apps[0].key == "second-app"
    finally:
        get_settings.cache_clear()
