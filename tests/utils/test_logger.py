from __future__ import annotations

import logging

from src.utils.logger import configure_logging, get_logger


def test_configure_logging_and_get_logger(capsys):
    configure_logging("DEBUG")
    log = get_logger("test-logger")

    log.debug("debug message")
    log.info("info message")

    # Ensure something was written to stdout/stderr by logging.
    captured = capsys.readouterr()
    combined = captured.out + captured.err
    assert "debug message" in combined or "info message" in combined

