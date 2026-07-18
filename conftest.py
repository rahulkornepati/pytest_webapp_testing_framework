from __future__ import annotations

import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Generator

import pytest
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions

from utils.config_reader import read_json
from utils.report_manager import LOGGER_NAME, ReportManager, TestResult


ROOT_DIR = Path(__file__).resolve().parent
REPORT_MANAGER_KEY = "_ecommerce_report_manager"
LOGGER_KEY = "_ecommerce_logger"


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption("--selenium-browser", action="store", default="chrome", choices=["chrome", "firefox", "edge"])
    parser.addoption("--selenium-headless", action="store_true", default=False)
    parser.addoption("--app-base-url", action="store", default="https://www.saucedemo.com/")
    parser.addoption("--selenium-implicit-wait", action="store", default=0, type=int)
    parser.addoption("--report-run-id", action="store", default=None, help="Existing or new timestamped report folder name.")
    parser.addoption("--report-retention-days", action="store", default=30, type=int)


def pytest_configure(config: pytest.Config) -> None:
    run_id = config.getoption("--report-run-id") or os.getenv("PYTEST_REPORT_RUN_ID") or ReportManager.timestamped_run_id()
    os.environ["PYTEST_REPORT_RUN_ID"] = run_id

    report_manager = ReportManager(
        root_dir=ROOT_DIR,
        run_id=run_id,
        retention_days=config.getoption("--report-retention-days"),
    )
    report_manager.cleanup_old_reports()
    logger = report_manager.configure_logging()

    config.option.htmlpath = str(report_manager.html_report)
    config.option.self_contained_html = True
    if hasattr(config.option, "xmlpath"):
        config.option.xmlpath = str(report_manager.junit_report)

    setattr(config, REPORT_MANAGER_KEY, report_manager)
    setattr(config, LOGGER_KEY, logger)
    logger.info("Report directory initialized: %s", report_manager.report_dir)


def pytest_sessionstart(session: pytest.Session) -> None:
    report_manager = _report_manager(session.config)
    report_manager.update_environment(
        browser=session.config.getoption("--selenium-browser"),
        base_url=os.getenv("BASE_URL", session.config.getoption("--app-base-url")),
        headless=str(session.config.getoption("--selenium-headless")),
        implicit_wait=str(session.config.getoption("--selenium-implicit-wait")),
    )
    report_manager.write_environment_properties()


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    report_manager = _report_manager(session.config)
    logger = _logger(session.config)
    if _is_xdist_worker(session.config):
        logger.info("Worker session finished with exit status %s", exitstatus)
        return

    report_manager.load_result_records()
    report_manager.update_environment(pytest_exit_status=str(exitstatus))
    report_manager.write_environment_properties()
    report_manager.write_failed_tests()
    report_manager.write_summary()
    logger.info("Suite finished with exit status %s", exitstatus)
    logger.info("Summary written to %s", report_manager.summary_file)


def pytest_runtest_logstart(nodeid: str, location: tuple[str, int | None, str]) -> None:
    logging_logger = __import__("logging").getLogger(LOGGER_NAME)
    logging_logger.info("START | %s", nodeid)


def pytest_runtest_logfinish(nodeid: str, location: tuple[str, int | None, str]) -> None:
    logging_logger = __import__("logging").getLogger(LOGGER_NAME)
    logging_logger.info("END   | %s", nodeid)


@pytest.fixture(scope="session", autouse=True)
def load_environment() -> None:
    load_dotenv(ROOT_DIR / ".env")


@pytest.fixture(scope="session")
def base_url(request: pytest.FixtureRequest) -> str:
    return os.getenv("BASE_URL", request.config.getoption("--app-base-url"))


@pytest.fixture(scope="session")
def users() -> dict:
    return read_json("users.json")


@pytest.fixture(scope="session")
def checkout_customers() -> dict:
    return read_json("checkout_customers.json")


@pytest.fixture()
def driver(request: pytest.FixtureRequest):
    browser = request.config.getoption("--selenium-browser")
    headless = request.config.getoption("--selenium-headless")
    implicit_wait = request.config.getoption("--selenium-implicit-wait")
    logger = _logger(request.config)

    if browser == "chrome":
        options = ChromeOptions()
        options.add_argument("--window-size=1440,1000")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        if headless:
            options.add_argument("--headless=new")
        web_driver = webdriver.Chrome(options=options)
    elif browser == "firefox":
        options = FirefoxOptions()
        if headless:
            options.add_argument("--headless")
        web_driver = webdriver.Firefox(options=options)
        web_driver.set_window_size(1440, 1000)
    else:
        options = EdgeOptions()
        options.add_argument("--window-size=1440,1000")
        if headless:
            options.add_argument("--headless=new")
        web_driver = webdriver.Edge(options=options)

    web_driver.implicitly_wait(implicit_wait)
    _record_browser_environment(request.config, web_driver)
    logger.info("WebDriver started | browser=%s | headless=%s", browser, headless)
    yield web_driver
    try:
        web_driver.quit()
        logger.info("WebDriver closed | browser=%s", browser)
    except Exception:
        logger.exception("Unable to close WebDriver cleanly")


@pytest.fixture()
def logged_in_driver(driver, base_url: str, users: dict):
    from pages.login_page import LoginPage

    LoginPage(driver).load(base_url)
    LoginPage(driver).login(users["standard_user"]["username"], users["standard_user"]["password"])
    return driver


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    outcome = yield
    report = outcome.get_result()
    setattr(item, "rep_" + report.when, report)
    should_record = report.when == "call" or (report.when == "setup" and report.skipped)
    if not should_record:
        return

    report_manager = _report_manager(item.config)
    logger = _logger(item.config)
    screenshot_path = None

    if report.when == "call" and report.failed:
        screenshot_path = _capture_failure_screenshot(item, report_manager, logger)
        if screenshot_path is not None:
            _attach_screenshot_to_html_report(item, report, screenshot_path)

    result = TestResult(
        nodeid=item.nodeid,
        outcome=report.outcome,
        duration_seconds=report.duration,
        start_time=datetime.fromtimestamp(call.start).astimezone().isoformat(timespec="seconds"),
        end_time=datetime.fromtimestamp(call.stop).astimezone().isoformat(timespec="seconds"),
        screenshot=str(screenshot_path) if screenshot_path else None,
        error=report.longreprtext if report.failed else None,
    )
    report_manager.add_result(result)
    report_manager.append_result_record(result, _worker_id(item.config))

    log_status = report.outcome.upper()
    logger.info("%s | %s | duration=%.3fs", log_status, item.nodeid, report.duration)


def _report_manager(config: pytest.Config) -> ReportManager:
    return getattr(config, REPORT_MANAGER_KEY)


def _logger(config: pytest.Config):
    return getattr(config, LOGGER_KEY)


def _record_browser_environment(config: pytest.Config, web_driver) -> None:
    capabilities = getattr(web_driver, "capabilities", {}) or {}
    browser_name = capabilities.get("browserName") or config.getoption("--selenium-browser")
    browser_version = capabilities.get("browserVersion") or capabilities.get("version")
    platform_name = capabilities.get("platformName")
    _report_manager(config).update_environment(
        browser=browser_name,
        browser_version=browser_version,
        browser_platform=platform_name,
    )
    _report_manager(config).write_environment_properties()


def _capture_failure_screenshot(item: pytest.Item, report_manager: ReportManager, logger) -> Path | None:
    driver_instance = item.funcargs.get("driver") or item.funcargs.get("logged_in_driver")
    if driver_instance is None:
        logger.warning("No WebDriver fixture found for failed test: %s", item.nodeid)
        return None

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    safe_name = re.sub(r"[^A-Za-z0-9_.-]+", "_", item.nodeid).strip("_")
    screenshot_path = report_manager.screenshot_dir / f"{safe_name}_{timestamp}.png"
    try:
        driver_instance.save_screenshot(str(screenshot_path))
        logger.info("Failure screenshot captured: %s", screenshot_path)
        return screenshot_path
    except Exception:
        logger.exception("Unable to capture failure screenshot for %s", item.nodeid)
        return None


def _attach_screenshot_to_html_report(item: pytest.Item, report: pytest.TestReport, screenshot_path: Path) -> None:
    html_plugin = item.config.pluginmanager.getplugin("html")
    if html_plugin is None:
        return

    extras = getattr(report, "extras", [])
    extras.append(html_plugin.extras.image(str(screenshot_path), name="Failure screenshot"))
    report.extras = extras


def _worker_id(config: pytest.Config) -> str:
    worker_input = getattr(config, "workerinput", None)
    if worker_input:
        return worker_input.get("workerid", "worker")
    return "master"


def _is_xdist_worker(config: pytest.Config) -> bool:
    return hasattr(config, "workerinput")
