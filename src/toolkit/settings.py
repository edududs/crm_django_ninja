from pathlib import Path
from typing import Any

import dj_database_url
from pydantic import SecretStr, computed_field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DjangoSettings(BaseSettings):
    """Base class for env-backed Django config. Inherit or use as-is and call export_django()."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    base_dir: Path
    secret_key: SecretStr = SecretStr(
        "django-insecure-$d=t@he-wf66fltli2ufm)o(pgb78f-n-bwwgd+ppj@2!vk$ro"
    )
    debug: bool = True
    database_url: str = "sqlite:///db.sqlite3"
    allowed_hosts: list[str] = ["*"]

    language_code: str = "pt-br"
    time_zone: str = "UTC"

    static_url: str = "static/"
    static_root: str = "staticfiles"
    media_url: str = "media/"
    media_root: str = "media"

    # When debug=True, only these loggers get level DEBUG (use getLogger(__name__) in views/services).
    # Env: DEBUG_LOGGERS=catalog,customer,sales or pass when instantiating.
    debug_loggers: list[str] = []

    @field_validator("allowed_hosts", mode="before")
    @classmethod
    def parse_allowed_hosts(cls, v: str | list[str]) -> list[str]:
        """Split comma-separated ALLOWED_HOSTS from env into a list."""
        if isinstance(v, list):
            return v
        s = v if isinstance(v, str) else "*"
        return [x.strip() for x in s.split(",") if x.strip()]

    @field_validator("debug_loggers", mode="before")
    @classmethod
    def parse_debug_loggers(cls, v: str | list[str]) -> list[str]:
        """Split comma-separated DEBUG_LOGGERS from env into a list."""
        if isinstance(v, list):
            return v
        if not v or not isinstance(v, str):
            return []
        return [x.strip() for x in v.split(",") if x.strip()]

    @computed_field
    @property
    def _databases(self) -> dict[str, Any]:
        """Django DATABASES from DATABASE_URL (Twelve-Factor). SQLite NAME resolved to base_dir."""
        parsed: dict[str, Any] = dict(
            dj_database_url.parse(
                self.database_url,
                conn_max_age=600,
                conn_health_checks=True,
            )
        )
        engine = str(parsed.get("ENGINE", ""))
        if "sqlite" in engine:
            name = parsed.get("NAME")
            if name and name != ":memory:":
                parsed["NAME"] = self.base_dir.resolve() / str(name).lstrip("/")
        return {"default": parsed}

    def get_logging_config(self, log_level: str | None = None) -> dict[str, Any]:
        """Build LOGGING dict. Uses RichHandler when debug (with short rich tracebacks), StreamHandler otherwise.

        Default level is INFO even when DEBUG=True to avoid Django flooding the console
        (autoreload "file first seen", template "variable resolution" at DEBUG).
        Pass log_level="DEBUG" only for the loggers you need. Tracebacks show only the
        last 3 frames (the actual error site), not the full chain.
        """
        level = log_level or "INFO"
        handlers = ["console"]

        formatters: dict[str, Any] = {
            "rich": {"format": "%(message)s", "datefmt": "[%X]"},
        }
        if not self.debug:
            formatters["simple"] = {"format": "%(levelname)s %(message)s", "style": "%"}

        console_class = "rich.logging.RichHandler" if self.debug else "logging.StreamHandler"
        console_handler: dict[str, Any] = {
            "class": console_class,
            "formatter": "rich" if self.debug else "simple",
        }
        if self.debug and console_class == "rich.logging.RichHandler":
            console_handler["rich_tracebacks"] = True
            console_handler["tracebacks_max_frames"] = 1
            console_handler["tracebacks_extra_lines"] = 1
            console_handler["tracebacks_show_locals"] = False

        loggers: dict[str, Any] = {
            "django": {"handlers": handlers, "level": level, "propagate": False},
            "django.utils.autoreload": {"level": "WARNING", "propagate": False},
            "django.template": {"level": "WARNING", "propagate": False},
        }
        if self.debug and self.debug_loggers:
            for name in self.debug_loggers:
                loggers[name] = {"handlers": handlers, "level": "DEBUG", "propagate": False}

        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": formatters,
            "handlers": {"console": console_handler},
            "root": {"level": level, "handlers": handlers},
            "loggers": loggers,
        }

    def export_django(self) -> dict[str, Any]:
        """Dict ready for globals().update() in the project's settings module."""
        base = self.base_dir.resolve()
        is_relative_static = not self.static_root.startswith("/")
        static_root_path = base / self.static_root if is_relative_static else Path(self.static_root)
        is_relative_media = not self.media_root.startswith("/")
        media_root_path = base / self.media_root if is_relative_media else Path(self.media_root)

        return {
            "BASE_DIR": base,
            "SECRET_KEY": self.secret_key.get_secret_value(),
            "DEBUG": self.debug,
            "ALLOWED_HOSTS": self.allowed_hosts,
            "DATABASES": self._databases,
            "LANGUAGE_CODE": self.language_code,
            "TIME_ZONE": self.time_zone,
            "USE_I18N": True,
            "USE_TZ": True,
            "STATIC_URL": self.static_url,
            "STATIC_ROOT": static_root_path,
            "STATICFILES_DIRS": [base / "static"],
            "STATICFILES_STORAGE": "django.contrib.staticfiles.storage.StaticFilesStorage",
            "MEDIA_URL": self.media_url,
            "MEDIA_ROOT": media_root_path,
            "LOGGING": self.get_logging_config(),
        }


def build_django_settings(base_dir: Path) -> dict[str, Any]:
    """Convenience: build settings dict from BASE_DIR (uses DjangoSettings.export_django())."""
    return DjangoSettings(base_dir=base_dir).export_django()
