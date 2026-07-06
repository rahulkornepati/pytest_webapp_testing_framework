from __future__ import annotations

import argparse
import os
from datetime import datetime
import sys

import pytest


def build_args() -> list[str]:
    parser = argparse.ArgumentParser(description="Pytest runner for the ecommerce Selenium framework.")
    parser.add_argument("--browser", default="chrome", choices=["chrome", "firefox", "edge"])
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--markers", default="", help="Pytest marker expression, for example: smoke or regression")
    parser.add_argument("--workers", default="1", help="Number of xdist workers. Use auto for local parallel runs.")
    parser.add_argument("--base-url", default="https://www.saucedemo.com/")
    parser.add_argument("--report-run-id", default=os.getenv("PYTEST_REPORT_RUN_ID") or datetime.now().strftime("%Y%m%d_%H%M%S"))
    args = parser.parse_args()

    pytest_args = [
        "tests",
        f"--selenium-browser={args.browser}",
        f"--app-base-url={args.base_url}",
        f"--report-run-id={args.report_run_id}",
    ]
    if args.headless:
        pytest_args.append("--selenium-headless")
    if args.markers:
        pytest_args.extend(["-m", args.markers])
    if args.workers != "1":
        pytest_args.extend(["-n", args.workers])
    return pytest_args


if __name__ == "__main__":
    sys.exit(pytest.main(build_args()))
