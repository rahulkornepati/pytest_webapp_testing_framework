from __future__ import annotations

import argparse
import os
from datetime import datetime
import sys

import pytest


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Pytest runner for the ecommerce framework (UI + API)."
    )
    # ── UI / Selenium options ────────────────────────────────────────────────
    parser.add_argument("--browser", default="chrome", choices=["chrome", "firefox", "edge"])
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--base-url", default="https://www.saucedemo.com/")

    # ── API options ──────────────────────────────────────────────────────────
    parser.add_argument(
        "--suite",
        choices=["ui", "api", "all"],
        default="ui",
        help="Which test suite to run (default: ui)",
    )
    parser.add_argument(
        "--api-base-url",
        default=os.getenv("API_BASE_URL", "https://api.escuelajs.co/api/v1"),
        help="Base URL for API tests",
    )

    # ── Common options ───────────────────────────────────────────────────────
    parser.add_argument("--markers", default="", help="Pytest marker expression")
    parser.add_argument(
        "--workers",
        default="1",
        help="Number of xdist workers. Use 'auto' for local parallel runs.",
    )
    parser.add_argument(
        "--report-run-id",
        default=os.getenv("PYTEST_REPORT_RUN_ID") or datetime.now().strftime("%Y%m%d_%H%M%S"),
    )
    return parser.parse_args()


def build_ui_args(args: argparse.Namespace) -> list[str]:
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


def build_api_args(args: argparse.Namespace) -> list[str]:
    env = os.environ.copy()
    env["API_BASE_URL"] = args.api_base_url
    os.environ.update(env)

    pytest_args = [
        "api_tests/",
        f"--report-run-id={args.report_run_id}",
    ]
    if args.markers:
        marker_expr = args.markers
        # Prefix api marker if not already present
        if "api" not in marker_expr:
            marker_expr = f"api and ({marker_expr})"
        pytest_args.extend(["-m", marker_expr])
    else:
        pytest_args.extend(["-m", "api"])
    if args.workers != "1":
        pytest_args.extend(["-n", args.workers])
    return pytest_args


def main() -> int:
    args = _parse_args()
    suite = args.suite

    if suite == "ui":
        return pytest.main(build_ui_args(args))
    if suite == "api":
        return pytest.main(build_api_args(args))

    # suite == "all" — run UI first, then API
    ui_exit = pytest.main(build_ui_args(args))
    api_exit = pytest.main(build_api_args(args))
    return max(ui_exit, api_exit)


if __name__ == "__main__":
    sys.exit(main())
