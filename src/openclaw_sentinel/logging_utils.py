from __future__ import annotations

import logging


def configure_logging(debug: bool = False, log_file: str | None = None) -> None:
    level = logging.DEBUG if debug else logging.INFO
    handlers: list[logging.Handler] = [logging.StreamHandler()]
    if log_file:
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        handlers=handlers,
        force=True,
    )
