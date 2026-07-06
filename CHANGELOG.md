# Changelog

## Production reporting and CI upgrade

### Added

- `utils/report_manager.py`
  - Added a dedicated reporting utility responsible for timestamped report directories, artifact paths, environment metadata, report retention cleanup, structured summary generation, failed test tracking, and logging configuration.
  - Keeps reporting concerns separate from tests and page objects to preserve the existing Page Object Model structure.

- `.github/workflows/selenium-tests.yml`
  - Added a GitHub Actions workflow that installs dependencies, runs headless Selenium tests, and uploads the full timestamped `reports/` artifact.
  - Uses `PYTEST_REPORT_RUN_ID` so CI executions produce stable, traceable report folder names.

- `CHANGELOG.md`
  - Documents every modified file and the reason for each change.

### Changed

- `conftest.py`
  - Creates a unique timestamped folder under `reports/` for every execution.
  - Routes `pytest-html` output to `report.html` inside the current run folder.
  - Routes JUnit XML to `junit.xml` inside the current run folder.
  - Creates `execution.log`, `screenshots/`, `summary.json`, `environment.properties`, and `failed_tests.txt` in the current run folder.
  - Embeds failure screenshots in the HTML report through the pytest-html extras API.
  - Captures per-test start time, end time, duration, outcome, error text, and screenshot path.
  - Writes total suite duration and aggregate pass/fail/skip counts to `summary.json`.
  - Logs every test start, end, pass, fail, and skip using Python logging with file and console handlers.
  - Stores OS, Python version, browser, browser version, base URL, headless mode, implicit wait, execution timestamp, run ID, and pytest exit status in `environment.properties`.
  - Cleans report folders older than 30 days before execution.
  - Supports xdist by appending worker result records and producing one final summary from the controller process.
  - Replaced the previous top-level `screenshots/` failure fixture so screenshots live with the correct execution report and are available during pytest-html report generation.

- `run_tests.py`
  - Added `--report-run-id` support.
  - Honors `PYTEST_REPORT_RUN_ID` when set by CI.
  - Removed hard-coded flat report paths from runner arguments so `conftest.py` owns artifact routing consistently.

- `Jenkinsfile`
  - Exports `PYTEST_REPORT_RUN_ID` for stable Jenkins report folder names.
  - Archives `reports/**/*` so all run artifacts are retained.
  - Updates JUnit collection to `reports/**/junit.xml`.
  - Updates HTML publication to discover timestamped `report.html` files.

- `README.md`
  - Rewritten with ASCII-safe project structure.
  - Updated report documentation to describe timestamped execution folders and generated artifacts.
  - Added CI notes for Jenkins and GitHub Actions.
  - Removed stale flat report and screenshot paths.

### Unchanged

- Existing tests, test data, and page object classes were not functionally changed.
- Existing pytest markers and command-line options remain available.
