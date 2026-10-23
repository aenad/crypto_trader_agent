"""Allowlisted structured logging: never serialize settings or arbitrary payloads."""

import json
import logging

from .models import DecisionRecord


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        return json.dumps(
            {
                "level": record.levelname,
                "event": "decision_recorded",
                "decision_id": getattr(record, "decision_id", None),
                "config_id": getattr(record, "config_id", None),
            }
        )


def log_decision(logger: logging.Logger, record: DecisionRecord) -> None:
    logger.info(
        "decision_recorded",
        extra={"decision_id": record.decision_id, "config_id": record.config_id},
    )
