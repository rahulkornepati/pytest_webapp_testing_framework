from __future__ import annotations

import json
import logging
import platform
import shutil
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any


LOGGER_NAME = "ecommerce_framework"


@dataclass
class TestResult:
    nodeid: str
    outcome: str
    duration_seconds: float
    start_time: str | None = None
    end_time: str | None = None
    screenshot: str | None = None
    error: str | None = None


@dataclass
class ReportManager:
    root_dir: Path
    run_id: str
    retention_days: int = 30
    environment: dict[str, str] = field(default_factory=dict)
    results: list[TestResult] = field(default_factory=list)
    suite_start_epoch: float = field(default_factory=time.perf_counter)
    suite_start_timestamp: str = field(default_factory=lambda: datetime.now().astimezone().isoformat(timespec="seconds"))

    def __post_init__(self) -> None:
        self.reports_root = self.root_dir / "reports"
        self.report_dir = self.reports_root / self.run_id
        self.screenshot_dir = self.report_dir / "screenshots"
        self.html_report = self.report_dir / "report.html"
        self.execution_log = self.report_dir / "execution.log"
        self.summary_file = self.report_dir / "summary.json"
        self.environment_file = self.report_dir / "environment.properties"
        self.failed_tests_file = self.report_dir / "failed_tests.txt"
        self.junit_report = self.report_dir / "junit.xml"
        self.report_dir.mkdir(parents=True, exist_ok=True)
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
        self.environment.update(self._default_environment())

    @staticmethod
    def timestamped_run_id() -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def cleanup_old_reports(self) -> None:
        if not self.reports_root.exists():
            return

        cutoff = datetime.now() - timedelta(days=self.retention_days)
        for path in self.reports_root.iterdir():
            if not path.is_dir() or path == self.report_dir:
                continue
            modified_at = datetime.fromtimestamp(path.stat().st_mtime)
            if modified_at < cutoff:
                shutil.rmtree(path, ignore_errors=True)

    def configure_logging(self) -> logging.Logger:
        logger = logging.getLogger(LOGGER_NAME)
        logger.setLevel(logging.INFO)
        logger.propagate = False

        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        logger.handlers.clear()

        file_handler = logging.FileHandler(self.execution_log, encoding="utf-8")
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        return logger

    def update_environment(self, **values: str | None) -> None:
        for key, value in values.items():
            if value is not None:
                self.environment[key] = str(value)

    def write_environment_properties(self) -> None:
        with self.environment_file.open("w", encoding="utf-8") as properties:
            for key in sorted(self.environment):
                properties.write(f"{key}={self.environment[key]}\n")

    def add_result(self, result: TestResult) -> None:
        self.results.append(result)

    def append_result_record(self, result: TestResult, worker_id: str) -> None:
        record_file = self.report_dir / f".results_{worker_id}.jsonl"
        with record_file.open("a", encoding="utf-8") as records:
            records.write(
                json.dumps(
                    {
                        "nodeid": result.nodeid,
                        "outcome": result.outcome,
                        "duration_seconds": result.duration_seconds,
                        "start_time": result.start_time,
                        "end_time": result.end_time,
                        "screenshot": result.screenshot,
                        "error": result.error,
                    }
                )
            )
            records.write("\n")

    def load_result_records(self) -> None:
        loaded_results: list[TestResult] = []
        for record_file in sorted(self.report_dir.glob(".results_*.jsonl")):
            with record_file.open(encoding="utf-8") as records:
                for line in records:
                    if line.strip():
                        loaded_results.append(TestResult(**json.loads(line)))
        if loaded_results:
            self.results = loaded_results

    def write_summary(self) -> None:
        total_duration = time.perf_counter() - self.suite_start_epoch
        counts = {
            "passed": sum(1 for result in self.results if result.outcome == "passed"),
            "failed": sum(1 for result in self.results if result.outcome == "failed"),
            "skipped": sum(1 for result in self.results if result.outcome == "skipped"),
        }
        summary: dict[str, Any] = {
            "run_id": self.run_id,
            "started_at": self.suite_start_timestamp,
            "finished_at": datetime.now().astimezone().isoformat(timespec="seconds"),
            "total_duration_seconds": round(total_duration, 3),
            "total_tests": len(self.results),
            "counts": counts,
            "environment": self.environment,
            "artifacts": {
                "report_html": str(self.html_report),
                "execution_log": str(self.execution_log),
                "screenshots": str(self.screenshot_dir),
                "environment_properties": str(self.environment_file),
                "failed_tests": str(self.failed_tests_file),
                "junit_xml": str(self.junit_report),
            },
            "tests": [
                {
                    "nodeid": result.nodeid,
                    "outcome": result.outcome,
                    "duration_seconds": round(result.duration_seconds, 3),
                    "start_time": result.start_time,
                    "end_time": result.end_time,
                    "screenshot": result.screenshot,
                    "error": result.error,
                }
                for result in self.results
            ],
        }
        with self.summary_file.open("w", encoding="utf-8") as summary_file:
            json.dump(summary, summary_file, indent=2)

    def write_failed_tests(self) -> None:
        failed_tests = [result.nodeid for result in self.results if result.outcome == "failed"]
        with self.failed_tests_file.open("w", encoding="utf-8") as failed_file:
            failed_file.write("\n".join(failed_tests))
            if failed_tests:
                failed_file.write("\n")

    def _default_environment(self) -> dict[str, str]:
        return {
            "execution_timestamp": self.suite_start_timestamp,
            "os": platform.platform(),
            "python_version": sys.version.replace("\n", " "),
            "run_id": self.run_id,
        }
