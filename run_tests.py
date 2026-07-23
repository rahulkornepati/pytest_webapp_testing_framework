from __future__ import annotations

import argparse
import os
from datetime import datetime
import sys

import pytest


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Pytest runner for the ecommerce framework (UI + API + DB)."
    )
    # ── UI / Selenium options ────────────────────────────────────────────────
    parser.add_argument("--browser", default="chrome", choices=["chrome", "firefox", "edge"])
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--base-url", default="https://www.saucedemo.com/")

    # ── API options ──────────────────────────────────────────────────────────
    parser.add_argument(
        "--suite",
        choices=["ui", "api", "db", "all"],
        default="ui",
        help="Which test suite to run (default: ui)",
    )
    parser.add_argument(
        "--api-base-url",
        default=os.getenv("API_BASE_URL", "https://api.escuelajs.co/api/v1"),
        help="Base URL for API tests",
    )

    # ── Database options ─────────────────────────────────────────────────────
    parser.add_argument(
        "--db-reset",
        action="store_true",
        default=False,
        help="Reset the database before running database tests",
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


def build_db_args(args: argparse.Namespace) -> list[str]:
    """Build pytest arguments for database tests."""
    pytest_args = [
        "database/",
        f"--report-run-id={args.report_run_id}",
    ]
    if args.markers:
        marker_expr = args.markers
        if "database" not in marker_expr:
            marker_expr = f"database and ({marker_expr})"
        pytest_args.extend(["-m", marker_expr])
    else:
        pytest_args.extend(["-m", "database"])
    if args.workers != "1":
        pytest_args.extend(["-n", args.workers])
    return pytest_args


def main() -> int:
    args = _parse_args()

    # Reset database if requested
    if args.db_reset or args.suite == "db":
        try:
            from database.db_setup import create_database
            from database.db_config import DBConfig

            db_path = DBConfig.DATABASE_PATH
            if not db_path.exists() or args.db_reset:
                print(f"[DB] Setting up database at: {db_path}")
                create_database()
        except ImportError:
            print("[DB] Warning: database module not available, skipping setup")
        except Exception as exc:
            print(f"[DB] Warning: database setup failed: {exc}")

    suite = args.suite

    if suite == "ui":
        return pytest.main(build_ui_args(args))
    if suite == "api":
        return pytest.main(build_api_args(args))
    if suite == "db":
        return pytest.main(build_db_args(args))

    # suite == "all" — run UI, API, then DB
    ui_exit = pytest.main(build_ui_args(args))
    api_exit = pytest.main(build_api_args(args))
    db_exit = pytest.main(build_db_args(args))
    return max(ui_exit, api_exit, db_exit)


if __name__ == "__main__":
    sys.exit(main())
