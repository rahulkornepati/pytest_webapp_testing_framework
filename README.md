# 🛒 Selenium + PyTest Enterprise Automation Framework

> **A production-grade, dual-layer automation framework combining Selenium WebDriver UI tests with Python Requests API tests — built for maintainability, scalability, and CI/CD readiness.**

[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)](https://python.org)
[![Pytest](https://img.shields.io/badge/Pytest-8.4-0A9EDC?logo=pytest&logoColor=white)](https://pytest.org)
[![Selenium](https://img.shields.io/badge/Selenium-4.33-43B02A?logo=selenium&logoColor=white)](https://selenium.dev)
[![Requests](https://img.shields.io/badge/Requests-2.32-FF6F00?logo=python&logoColor=white)](https://requests.readthedocs.io)
[![GitHub Actions](https://img.shields.io/badge/CI-GitHub_Actions-2088FF?logo=githubactions&logoColor=white)](.github/workflows/selenium-tests.yml)
[![Jenkins](https://img.shields.io/badge/CI-Jenkins-D24939?logo=jenkins&logoColor=white)](Jenkinsfile)
[![API Tests](https://img.shields.io/badge/API-30_Tests-512BD4?logo=postman&logoColor=white)](api_tests/)
[![UI Tests](https://img.shields.io/badge/UI-12_Tests-43B02A?logo=googlechrome&logoColor=white)](tests/)
[![Page Object Model](https://img.shields.io/badge/POM-Architecture-FF6F00?logo=python&logoColor=white)](pages/)
[![Parallel Execution](https://img.shields.io/badge/xdist-Parallel-0A9EDC?logo=pytest&logoColor=white)](pytest.ini)
[![JSON Schema](https://img.shields.io/badge/Schema-Validation-8A2BE2?logo=javascript&logoColor=white)](schemas/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows_|_Linux_|_macOS-0078D6?logo=windows&logoColor=white)](.github/workflows/selenium-tests.yml)

---

## 📋 Project Overview

This framework provides **end-to-end quality assurance** for an ecommerce web application (SauceDemo) through a **dual automation strategy**:

| Layer | Technology | Scope |
|-------|-----------|-------|
| **🧪 UI Tests** | Selenium WebDriver + PyTest | Browser-based user journeys (login, inventory, cart, checkout) |
| **🔌 API Tests** | Python Requests + PyTest | Backend service validation (auth, products, cart, orders, users, schema, performance) |

### 🎯 Problem Solved

Modern web applications demand validation at **every layer of the stack**. Traditional UI-only automation is slow, brittle, and cannot cover backend logic. API-only automation misses critical browser rendering and user-experience bugs. **This framework bridges both worlds** with a shared configuration, reporting, and CI/CD foundation — giving teams comprehensive coverage without duplicated effort.

### 🏆 Framework Goals

- 🔹 **Enterprise-ready** — follows SOLID principles, PEP8, and clean code patterns
- 🔹 **Scalable** — page objects, reusable API client, data-driven tests, fixture injection
- 🔹 **Extensible** — add new pages, API endpoints, or tests without modifying existing code
- 🔹 **Observable** — rich HTML reports, structured logs, failure screenshots, environment metadata
- 🔹 **CI/CD-native** — works out-of-the-box with GitHub Actions and Jenkins

---

## 📑 Table of Contents

- [Key Highlights](#-key-highlights)
- [Project Architecture](#-project-architecture)
- [Framework Workflow](#-framework-workflow)
- [Tech Stack](#-tech-stack)
- [Design Patterns](#-design-patterns)
- [SOLID Principles](#-solid-principles)
- [Features Overview](#-features-overview)
- [UI Automation](#-ui-automation)
- [API Automation](#-api-automation)
- [Test Data Management](#-test-data-management)
- [Reporting](#-reporting)
- [Logging](#-logging)
- [Screenshots](#-screenshots)
- [Installation](#-installation)
- [Execution Commands](#-execution-commands)
- [Pytest Markers](#-pytest-markers)
- [Configuration](#-configuration)
- [CI/CD](#-cicd)
- [Supported Browsers](#-supported-browsers)
- [Current Test Coverage](#-current-test-coverage)
- [Best Practices Followed](#-best-practices-followed)
- [Scalability](#-scalability)
- [Future Enhancements](#-future-enhancements)
- [License](#-license)
- [Author](#-author)

---

## 🚀 Key Highlights

<details>
<summary><strong>🔹 Enterprise Architecture</strong></summary>

- **Page Object Model** with a reusable `BasePage` class encapsulating all WebDriver interactions
- **API Client** with automatic retry, session management, and pluggable authentication
- **Data Models** mapping API responses to typed Python dataclasses (`Product`, `User`, `Cart`, `Order`)
- **JSON Schema Validation** for every API response against 7 formal schemas
- **Timestamped reports** with HTML, JUnit XML, execution logs, environment properties, and failure screenshots
</details>

<details>
<summary><strong>🔹 SOLID Principles & Clean Code</strong></summary>

- **Single Responsibility** — each class has one purpose (page objects own locators, assertions own validation, models own data representation)
- **Open/Closed** — new page objects extend `BasePage` without modifying it; new API assertions extend without changing existing ones
- **Dependency Inversion** — `APIClient` depends on `AuthenticationHandler` abstractions, not concrete auth implementations
- **Full type hints** on every method, function, and class attribute
- **Comprehensive docstrings** following Google-style conventions
</details>

<details>
<summary><strong>🔹 Production Reporting</strong></summary>

- 📊 **pytest-html** — self-contained HTML report with failure screenshots embedded inline
- 📋 **JUnit XML** — CI tool integration (Jenkins, GitHub Actions)
- 🧾 **Execution Log** — structured `execution.log` with timestamps and levels
- 📝 **Summary JSON** — aggregate pass/fail/skip counts, duration, environment, per-test results
- 🖼️ **Failure Screenshots** — automatically captured and attached to HTML reports on test failure
- 🔄 **Report Cleanup** — automatic retention-based purging of old reports (default >30 days)
- 🔗 **Run ID** — every execution gets a unique timestamped folder (`reports/YYYYMMDD_HHMMSS/`)
</details>

<details>
<summary><strong>🔹 Cross-Browser & Parallel</strong></summary>

- **Chrome**, **Firefox**, and **Edge** support via `--selenium-browser` flag
- **Headless execution** with `--selenium-headless` for CI environments
- **Parallel execution** via `pytest-xdist` (`-n auto`)
- **xdist-aware reporting** — individual worker result files merged into one final summary
</details>

<details>
<summary><strong>🔹 API Testing Superpowers</strong></summary>

- **Reusable API client** — `get()`, `post()`, `put()`, `patch()`, `delete()` with automatic logging
- **4 authentication strategies** — Bearer Token, Basic Auth, API Key, Session-based
- **Automatic token refresh** — expired tokens are refreshed transparently
- **20+ custom assertions** — status codes, JSON keys, types, values, schema, headers, response time, business logic
- **Faker-powered test data** — random emails, names, passwords, addresses, prices, and more
- **Placeholder substitution** — `{{random}}` tags replaced with unique IDs for collision-free test data
- **Smart test skipping** — tests gracefully `pytest.skip()` when endpoints are unavailable
</details>

---

## 📁 Project Architecture

<pre>
📦 ecommerce_selenium_pytest_framework
├── 📂 <strong>pages/</strong>                    <em># 🧩 Page Object Model — UI layer</em>
│   ├── base_page.py                 <em>#   ↳ Abstract parent: find, click, type, wait, scroll</em>
│   ├── login_page.py                <em>#   ↳ Login page (SauceDemo)</em>
│   ├── inventory_page.py            <em>#   ↳ Product catalogue / sort / add-to-cart</em>
│   ├── cart_page.py                 <em>#   ↳ Shopping cart page</em>
│   ├── checkout_information_page.py <em>#   ↳ Checkout — customer info form</em>
│   ├── checkout_overview_page.py    <em>#   ↳ Checkout — order summary</em>
│   ├── checkout_complete_page.py    <em>#   ↳ Checkout — order confirmation</em>
│   ├── header_page.py               <em>#   ↳ App header: logo, cart badge, menu trigger</em>
│   ├── footer_page.py               <em>#   ↳ Footer: copyright, social links</em>
│   ├── menu_page.py                 <em>#   ↳ Sidebar menu: logout, reset, about</em>
│   ├── product_details_page.py      <em>#   ↳ Single product details view</em>
│   └── product_data.py              <em>#   ↳ Product name/price constants</em>
│
├── 📂 <strong>tests/</strong>                    <em># ✅ UI test classes</em>
│   ├── test_login_page.py       <em>#   ↳ 3 tests: valid login, invalid, locked-out</em>
│   ├── test_inventory_page.py   <em>#   ↳ 6 tests: add/remove, details, sort, footer</em>
│   └── test_checkout_page.py    <em>#   ↳ 3 tests: happy path, validation, sidebar logout</em>
│
├── 📂 <strong>api/</strong>                     <em># 🌐 API testing core framework</em>
│   ├── api_client.py            <em>#   ↳ Reusable HTTP client (GET/POST/PUT/PATCH/DELETE)</em>
│   ├── authentication.py        <em>#   ↳ Auth strategies: Bearer, Basic, API Key, Session</em>
│   ├── endpoints.py             <em>#   ↳ Centralized endpoint URL definitions</em>
│   ├── api_helpers.py           <em>#   ↳ Payload builders, Faker data, response extractors</em>
│   └── api_assertions.py        <em>#   ↳ 20+ custom assertions + JSON Schema validation</em>
│
├── 📂 <strong>api_tests/</strong>                <em># ✅ API test classes (30 test methods)</em>
│   ├── conftest.py              <em>#   ↳ API fixtures: client, auth, helpers, cleanup</em>
│   ├── test_auth_api.py         <em>#   ↳ 3 tests: valid login, invalid, missing fields</em>
│   ├── test_products_api.py     <em>#   ↳ 4 tests: all, by ID, search, pagination</em>
│   ├── test_cart_api.py         <em>#   ↳ 3 tests: add, update quantity, remove</em>
│   ├── test_orders_api.py       <em>#   ↳ 2 tests: create order, get details</em>
│   ├── test_users_api.py        <em>#   ↳ 2 tests: get profile, update profile</em>
│   ├── test_negative_api.py     <em>#   ↳ 4 tests: invalid endpoint, unauthorised, invalid ID, delete non-existent</em>
│   ├── test_schema_validation.py<em>#   ↳ 7 tests: validate all schemas</em>
│   └── test_performance_api.py  <em>#   ↳ 5 tests: response time under 2s</em>
│
├── 📂 <strong>models/</strong>                   <em># 📦 Typed data models</em>
│   ├── product.py               <em>#   ↳ Product dataclass with from_dict/to_dict</em>
│   ├── user.py                  <em>#   ↳ User dataclass</em>
│   ├── cart.py                  <em>#   ↳ Cart + CartItem dataclasses</em>
│   └── order.py                 <em>#   ↳ Order + OrderItem dataclasses</em>
│
├── 📂 <strong>schemas/</strong>                  <em># 📐 JSON Schema definitions (Draft-07)</em>
│   ├── auth_login_schema.json   <em>#   ↳ Login response (access_token, refresh_token)</em>
│   ├── product_schema.json      <em>#   ↳ Single product fields</em>
│   ├── products_list_schema.json<em>#   ↳ Array of products</em>
│   ├── user_schema.json         <em>#   ↳ User profile fields</em>
│   ├── cart_schema.json         <em>#   ↳ Cart resource fields</em>
│   ├── order_schema.json        <em>#   ↳ Order resource fields</em>
│   └── error_schema.json        <em>#   ↳ Error response structure</em>
│
├── 📂 <strong>utils/</strong>                   <em># 🛠️ Shared utilities</em>
│   ├── config_reader.py         <em>#   ↳ JSON test data loader</em>
│   └── report_manager.py        <em>#   ↳ Reporting engine: results, summary, environment, logging</em>
│
├── 📂 <strong>config/</strong>                  <em># ⚙️ Configuration</em>
│   └── api_config.py            <em>#   ↳ API settings from .env (timeout, retries, pagination)</em>
│
├── 📂 <strong>test_data/</strong>              <em># 📊 JSON test data fixtures</em>
│   ├── users.json               <em>#   ↳ UI test users (standard, locked-out, invalid)</em>
│   ├── checkout_customers.json  <em>#   ↳ Checkout customer profiles</em>
│   ├── api_payloads.json        <em>#   ↳ API request payload templates</em>
│   └── api_testdata.json        <em>#   ↳ API test configuration values</em>
│
├── 📂 <strong>reports/</strong>                  <em># 📈 Generated test artifacts (gitignored)</em>
│   └── 📂 YYYYMMDD_HHMMSS/      <em>#   ↳ Timestamped execution folder</em>
│       ├── report.html          <em>#   ↳ Self-contained HTML report</em>
│       ├── junit.xml            <em>#   ↳ CI-compatible JUnit results</em>
│       ├── execution.log        <em>#   ↳ Structured execution log</em>
│       ├── summary.json         <em>#   ↳ Aggregate results + environment metadata</em>
│       ├── environment.properties<em># ↳ Browser, OS, Python version metadata</em>
│       ├── failed_tests.txt     <em>#   ↳ List of failed test node IDs</em>
│       └── 📂 screenshots/      <em>#   ↳ Failure screenshots</em>
│
├── conftest.py                  <em># 🧩 Root pytest config: fixtures, hooks, browser setup</em>
├── pytest.ini                   <em># 📋 Pytest markers, test discovery, default addopts</em>
├── run_tests.py                 <em># 🚀 Unified test runner (UI / API / both)</em>
├── requirements.txt             <em># 📦 Python dependencies</em>
├── .env.example                 <em># 🔐 Environment variable template</em>
├── Jenkinsfile                  <em># 🔄 Jenkins declarative pipeline</em>
├── CHANGELOG.md                 <em># 📝 Project changelog</em>
└── 📂 .github/workflows/       <em># 🤖 CI automation</em>
    └── selenium-tests.yml       <em>#   ↳ GitHub Actions: UI + API test jobs</em>
</pre>

---

## 🔄 Framework Workflow

```
  User / CI Trigger
         ↓
  ┌─ run_tests.py / pytest ─┐
  │         ↓                │
  │   conftest.py Fixtures  │
  │    ↕       ↕             │
  │  UI Path   API Path      │
  │    ↓        ↓            │
  │  Page Obj  APIClient    │
  │    ↓        ↓            │
  │  Assert    Assert        │
  │    ↓        ↓            │
  │  └── ReportManager ──┘  │
  │         ↓                │
  │  HTML | JUnit | Logs    │
  │  Summary | Screenshots   │
  └─────────────────────────┘
```

**Execution pipeline:**

1. CI or User invokes `pytest` / `run_tests.py`
2. `conftest.py` loads environment (`.env`) and sets up fixtures
3. **UI path**: WebDriver initializes → Page Objects interact with the browser → assertions validate behavior
4. **API path**: `APIClient` authenticates → HTTP requests execute → `APIAssertions` validate responses
5. `ReportManager` collects results, screenshots, and timings from both paths
6. Final artifacts published (HTML, JUnit, logs, summary)
7. CI systems archive and publish reports for team visibility

---

## 🛠️ Tech Stack

| Technology | Version | Purpose |
|-----------|---------|---------|
| [Python](https://python.org) | 3.12+ | Core programming language |
| [Pytest](https://pytest.org) | 8.4 | Test runner, fixtures, markers, assertions |
| [Selenium WebDriver](https://selenium.dev) | 4.33 | Browser automation (UI tests) |
| [Requests](https://requests.readthedocs.io) | 2.32 | HTTP client (API tests) |
| [JSON Schema](https://python-jsonschema.readthedocs.io) | 4.23 | Response schema validation |
| [WebDriver Manager](https://github.com/SergeyPirogov/webdriver_manager) | 4.0 | Automatic browser driver management |
| [python-dotenv](https://github.com/theskumar/python-dotenv) | 1.1 | Environment variable loading |
| [Faker](https://faker.readthedocs.io) | 33.3 | Random test data generation |
| [pytest-html](https://github.com/pytest-dev/pytest-html) | 4.1 | Self-contained HTML report |
| [pytest-xdist](https://github.com/pytest-dev/pytest-xdist) | 3.8 | Parallel test execution |
| [allure-pytest](https://docs.qameta.io/allure-report/) | 2.14 | Allure reporting integration |
| [GitHub Actions](https://github.com/features/actions) | — | CI/CD automation |
| [Jenkins](https://jenkins.io) | — | Enterprise CI/CD pipeline |

---

## 🏗️ Design Patterns

### 🧩 Page Object Model (POM)

Every web page is represented by a dedicated class that encapsulates locators and interaction methods. The `BasePage` parent provides reusable WebDriver operations:

```python
class BasePage:
    def find(self, locator) -> WebElement   # Explicit wait for presence
    def click(self, locator) -> None         # Scroll + JavaScript click
    def type_text(self, locator, text)       # Clear + send_keys + JS events
    def visible(self, locator) -> WebElement # Explicit wait for visibility
```

### 🏭 Factory Pattern

**`AuthenticationHandler`** provides factory class methods (`with_bearer_token()`, `with_basic_auth()`, `with_api_key()`, `with_session()`, `no_auth()`) to construct the correct strategy without conditional logic in client code.

### 💉 Dependency Injection (via Fixtures)

Pytest fixtures inject dependencies into tests:

```python
def test_login(api_client: APIClient, api_helpers: APIHelpers): ...
```

### 🔧 Utility Pattern

- **`APIHelpers`** — payload building, random data generation, response extraction, pagination
- **`APIAssertions`** — 20+ static assertion methods for all response validation
- **`ReportManager`** — reporting orchestration separate from test logic

### 📐 Reusable Base Classes

- **`BasePage`** — all page objects inherit common WebDriver interactions
- **`APIClient`** — one client class handles all HTTP methods across every test
- **Data models** (`Product`, `User`, `Cart`, `Order`) — serialize/deserialize API responses to typed objects

---

## 🔬 SOLID Principles

| Principle | Implementation |
|-----------|---------------|
| **S**ingle Responsibility | Each class has exactly one reason to change: `LoginPage` owns login locators, `APIAssertions` owns validation logic, `ReportManager` owns artifact generation. |
| **O**pen / Closed | New page objects extend `BasePage` without modifying it. New API assertions add static methods without changing existing ones. |
| **L**iskov Substitution | Every page object can replace `BasePage` anywhere — they all conform to the same contract. |
| **I**nterface Segregation | Fixtures inject only what a test needs. No test receives irrelevant dependencies. |
| **D**ependency Inversion | `APIClient` depends on `AuthenticationHandler` abstraction, not concrete implementations. |

---

## ✨ Features Overview

| Feature | Status | Details |
|---------|--------|---------|
| Page Object Model | ✅ | 12 page classes, reusable `BasePage` |
| SOLID Principles | ✅ | Single Responsibility, Open/Closed, DI |
| Cross-Browser | ✅ | Chrome, Firefox, Edge |
| Headless Execution | ✅ | `--selenium-headless` flag |
| Parallel Execution | ✅ | `pytest-xdist` (`-n auto`) |
| Automatic Screenshots | ✅ | On failure, embedded in HTML report |
| HTML Reports | ✅ | Self-contained `pytest-html` |
| JUnit XML Reports | ✅ | CI tool integration |
| Allure Reports | ✅ | `allure-pytest` integration |
| Timestamped Reports | ✅ | `reports/YYYYMMDD_HHMMSS/` |
| Report Cleanup | ✅ | Retention-based cleanup (default >30 days) |
| Structured Logging | ✅ | File + console handlers |
| JSON Test Data | ✅ | 4 JSON files for UI + API |
| Environment Variables | ✅ | `.env` via `python-dotenv` |
| API Client | ✅ | GET, POST, PUT, PATCH, DELETE |
| API Authentication | ✅ | Bearer, Basic, API Key, Session |
| Token Auto-Refresh | ✅ | Expired bearer tokens refreshed transparently |
| JSON Schema Validation | ✅ | 7 schemas, `jsonschema` library |
| Custom Assertions | ✅ | 20+ reusable assertion methods |
| Retry Mechanism | ✅ | Configurable retries on 5xx/429 |
| CI/CD Integration | ✅ | GitHub Actions + Jenkins |
| Data Models | ✅ | Typed dataclasses for API resources |
| Faker Integration | ✅ | Random email, name, address, price |
| Placeholder Substitution | ✅ | `{{random}}` → unique IDs |
| Smart Test Skipping | ✅ | Graceful skip on unavailable endpoints |
| Performance Tests | ✅ | Response time < 2s validation |

---

## 🌐 UI Automation

All 12 page classes extend `BasePage`, which provides reusable WebDriver interactions:

| Method | Description |
|--------|-------------|
| `find(locator)` | Explicit wait for element presence (up to 10s) |
| `visible(locator)` | Wait for visibility |
| `clickable(locator)` | Wait for clickable + scroll into view |
| `click(locator)` | Smart click using JavaScript for robustness |
| `type_text(locator, text)` | Clear + send_keys + trigger JS input/change events |
| `is_visible(locator, timeout)` | Boolean check without exception |
| `wait_for_url_contains(text)` | URL pattern wait |

### UI Test Coverage

| Test File | Tests | Validations |
|-----------|-------|-------------|
| `test_login_page.py` | 3 | Valid login → inventory, invalid → error, locked-out blocked |
| `test_inventory_page.py` | 6 | Add/remove/clear badge, details & image, price sort, navigation, footer links |
| `test_checkout_page.py` | 3 | Happy path completion, missing name validation, sidebar logout |

### Cross-Browser Support

```bash
pytest --selenium-browser=chrome    # Default
pytest --selenium-browser=firefox
pytest --selenium-browser=edge
```

---

## 🔌 API Automation

### Client Architecture

```
APIClient
├── Session Management (requests.Session + HTTPAdapter)
├── Authentication (Bearer Token, Basic Auth, API Key, Session)
├── HTTP Methods: get, post, put, patch, delete
├── Logging: URL, method, headers (sanitized), payload, status, timing
├── Hooks: before_request, after_request
└── Retry: 3 attempts, exponential backoff, 429/5xx retryable
```

### Assertion Library

| Category | Methods |
|----------|---------|
| **Status Codes** | `assert_status_code`, `assert_status_ok`, `assert_status_created`, `assert_status_no_content`, `assert_status_unauthorized`, `assert_status_forbidden`, `assert_status_not_found` |
| **JSON Body** | `assert_json_has_key`, `assert_json_has_keys`, `assert_json_value`, `assert_json_type`, `assert_json_not_empty`, `assert_list_length`, `assert_error_message_contains` |
| **Schema** | `assert_valid_schema` (loads from `schemas/*.json`) |
| **Headers** | `assert_header_present`, `assert_content_type` |
| **Timing** | `assert_response_time_less_than` (default: 2s) |
| **Business Logic** | `assert_id_is_positive`, `assert_pagination` |

### Data Models

Typed dataclasses bridge API responses and test assertions:

```python
@dataclass
class Product:
    id: int; title: str; price: float
    description: str; category_id: int
    category_name: str; images: list[str]

    @classmethod
    def from_dict(cls, data: dict) -> Product: ...
    def to_dict(self) -> dict: ...
```

---

## 📊 Test Data Management

### JSON Files

| File | Content | Used By |
|------|---------|---------|
| `users.json` | UI credentials (standard, locked-out, invalid) | `test_login_page.py` |
| `checkout_customers.json` | Checkout form data | `test_checkout_page.py` |
| `api_payloads.json` | API request templates with `{{random}}` placeholders | All API tests |
| `api_testdata.json` | API config: IDs, limits, keywords, timeouts | All API tests |

### Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `BASE_URL` | `https://www.saucedemo.com/` | UI app URL |
| `API_BASE_URL` | `https://api.escuelajs.co/api/v1` | API base URL |
| `API_USERNAME` | `john@mail.com` | API auth username |
| `API_PASSWORD` | `changeme` | API auth password |
| `API_DEFAULT_TIMEOUT` | `30` | Request timeout (seconds) |
| `API_MAX_RETRIES` | `3` | Max retry attempts |
| `API_MAX_RESPONSE_TIME` | `2.0` | Performance SLA (seconds) |

### Dynamic Data (Faker)

```python
APIHelpers.random_email()         # → "jennifer78@example.org"
APIHelpers.random_name()          # → "Dr. Sarah Johnson"
APIHelpers.random_price()         # → 147.83
APIHelpers.random_product_title() # → "Advanced multi-state paradigm"
```

---

## 📈 Reporting

Every execution generates a complete artifact set under `reports/YYYYMMDD_HHMMSS/`:

| Artifact | File | Description |
|----------|------|-------------|
| 🖥️ **HTML Report** | `report.html` | Self-contained, with failure screenshots |
| 📋 **JUnit XML** | `junit.xml` | CI tool consumption |
| 🧾 **Execution Log** | `execution.log` | Timestamped structured logs |
| 📝 **Summary JSON** | `summary.json` | Pass/fail/skip, duration, environment, per-test results |
| 📊 **Environment** | `environment.properties` | OS, Python, browser, version, URL, headless |
| ❌ **Failed Tests** | `failed_tests.txt` | Node IDs of all failures |
| 🖼️ **Screenshots** | `screenshots/*.png` | Captured on failure, embedded in HTML report |

Reports older than 30 days (`--report-retention-days`) are auto-purged before each execution.

---

## 📝 Logging

Python's `logging` module with dual-handler setup (file + console):

| Logger | Used By |
|--------|---------|
| `ecommerce_framework` | Root framework logger |
| `ecommerce_framework.api.client` | API request/response logging |
| `ecommerce_framework.api.auth` | Authentication operations |
| `ecommerce_framework.api.assertions` | Schema validation |
| `ecommerce_framework.api.conftest` | API fixture setup |

**Logged events:** Test lifecycle (`START`/`END`/`PASSED`/`FAILED`), API requests/responses (with timing), screenshots, authentication, and errors.

---

## 🖼️ Screenshots

> *Placeholder images — replace with actual captures from a test run.*

| Execution Report | Failure Screenshot |
|:---:|:---:|
| ![HTML Report](https://via.placeholder.com/600x400/1a1a2e/e94560?text=HTML+Execution+Report) | ![Failure Screenshot](https://via.placeholder.com/400x300/533483/ffffff?text=Failure+Screenshot) |

| CI Pipeline | Folder Structure |
|:---:|:---:|
| ![CI Pipeline](https://via.placeholder.com/600x300/0f3460/e0e0e0?text=CI+Pipeline+Overview) | ![Folder Structure](https://via.placeholder.com/400x500/16213e/00ff88?text=Project+Structure) |

---

## 💻 Installation

```bash
git clone https://github.com/your-org/ecommerce_selenium_pytest_framework.git
cd ecommerce_selenium_pytest_framework
python -m venv .venv
source .venv/bin/activate       # Linux/macOS
.venv\Scripts\activate          # Windows
pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env            # Edit with your credentials
```

**Prerequisites:** Python 3.12+, Git, Chrome/Firefox/Edge (for UI tests). Browser drivers are managed automatically by `webdriver-manager`.

---

## 🚀 Execution Commands

| Command | Description |
|---------|-------------|
| `pytest` | Run all tests (UI + API) |
| `pytest tests/` | UI tests only |
| `pytest api_tests/ -m api` | API tests only |
| `python run_tests.py --suite=all` | Both suites via runner |
| `python run_tests.py --suite=api` | API only via runner |
| `pytest -m smoke` | Smoke tests |
| `pytest -m "api and auth"` | API auth tests |
| `pytest -m "api and performance"` | API performance tests |
| `pytest -m login` | UI login tests |
| `pytest -m checkout` | UI checkout tests |
| `pytest -m regression` | Full regression suite |
| `pytest --selenium-headless` | Headless mode |
| `pytest -n auto` | Parallel execution |
| `pytest --selenium-browser=firefox` | Firefox |
| `pytest --alluredir=allure-results` | Allure report |

---

## 🏷️ Pytest Markers

| Marker | Type | Scope | Test Count |
|--------|------|-------|-----------|
| `smoke` | 🟢 Critical | Core functionality sanity checks | 7 |
| `regression` | 🔵 Full | Comprehensive functional coverage | 20 |
| `api` | 🌐 Layer | All API/integration tests | 22* |
| `login` | 🔐 Feature | Login & authentication (UI) | 3 |
| `cart` | 🛒 Feature | Shopping cart (UI + API) | 6 |
| `checkout` | 💳 Feature | Checkout workflow (UI + API) | 5 |
| `inventory` | 📦 Feature | Product catalogue (UI + API) | 10 |
| `auth` | 🔑 Feature | API authentication tests | 3 |
| `products` | 📋 Feature | API product catalogue tests | 4 |
| `orders` | 📄 Feature | API order management tests | 2 |
| `users` | 👤 Feature | API user profile tests | 2 |
| `negative` | ❌ Quality | API error-path tests | 4 |
| `schema` | 📐 Quality | API JSON Schema validation | 7 |
| `performance` | ⏱️ Quality | API response time validation | 5 |

*\*8 of 30 API tests gracefully skip when endpoints are unavailable on the target API.*

---

## ⚙️ Configuration

```
┌───────────────────────────────────┐
│  1. .env File (environment vars)  │ ← API keys, URLs, credentials
├───────────────────────────────────┤
│  2. pytest.ini (pytest config)    │ ← Test discovery, markers, defaults
├───────────────────────────────────┤
│  3. CLI Arguments (runtime)       │ ← Overrides at execution time
└───────────────────────────────────┘
```

| Argument | Default | Description |
|----------|---------|-------------|
| `--selenium-browser` | `chrome` | Browser: `chrome`, `firefox`, `edge` |
| `--selenium-headless` | `False` | Headless mode flag |
| `--app-base-url` | `https://www.saucedemo.com/` | UI application URL |
| `--report-run-id` | Auto-timestamp | Custom report folder name |
| `--report-retention-days` | `30` | Report cleanup threshold |
| `--suite` | `ui` | Test suite: `ui`, `api`, `all` |
| `--api-base-url` | `https://api.escuelajs.co/api/v1` | API base URL |
| `--workers` | `1` | xdist worker count |

---

## 🤖 CI/CD

### GitHub Actions Workflow

Defined in [`.github/workflows/selenium-tests.yml`](.github/workflows/selenium-tests.yml) — runs **two parallel jobs** on every push/PR to `main`:

```yaml
jobs:
  selenium-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: pip install -r requirements.txt
      - run: python run_tests.py --browser chrome --markers smoke --headless
      - uses: actions/upload-artifact@v4
        with:
          name: ui-reports
          path: reports/**

  api-tests:
    runs-on: ubuntu-latest
    env:
      API_BASE_URL: https://api.escuelajs.co/api/v1
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: pip install -r requirements.txt
      - run: python -m pytest api_tests/ -m "api" -n auto
      - uses: actions/upload-artifact@v4
        with:
          name: api-reports
          path: reports/**
```

**Manual workflow dispatch** allows choosing browser, marker expression, and test suite.

### Jenkins Pipeline

The [`Jenkinsfile`](Jenkinsfile) provides a declarative pipeline:

- **Parameterized builds** — browser, markers, headless, URLs, auth method, test suite
- **Parallel UI + API stages** — both suites run concurrently
- **Post-build** — HTML report publishing, artifact archiving, JUnit collection

```groovy
stage('Run Tests') {
    parallel {
        stage('UI — Selenium Tests') { ... }
        stage('API — Integration Tests') { ... }
    }
}
post {
    always {
        publishHTML(target: [...])
        archiveArtifacts(artifacts: 'reports/**/*')
        junit(testResults: 'reports/**/junit.xml')
    }
}
```

---

## 🌐 Supported Browsers

| Browser | Headless | WebDriver Management |
|---------|----------|---------------------|
| ![Chrome](https://img.shields.io/badge/Chrome-4285F4?logo=googlechrome&logoColor=white) | ✅ `--headless=new` | Automatic (webdriver-manager) |
| ![Firefox](https://img.shields.io/badge/Firefox-FF7139?logo=firefoxbrowser&logoColor=white) | ✅ `--headless` | Automatic (webdriver-manager) |
| ![Edge](https://img.shields.io/badge/Edge-0078D7?logo=microsoftedge&logoColor=white) | ✅ `--headless=new` | Automatic (webdriver-manager) |

All browsers run at **1440×1000** viewport with configurable implicit wait.

---

## 📊 Current Test Coverage

### UI Tests (12 total)

| Test File | Tests | Status |
|-----------|-------|--------|
| `test_login_page.py` | 3 | ✅ All Passing |
| `test_inventory_page.py` | 6 | ✅ All Passing |
| `test_checkout_page.py` | 3 | ✅ All Passing |

### API Tests (30 total)

| Test File | Tests | Passing | Skipped* |
|-----------|-------|---------|----------|
| `test_auth_api.py` | 3 | 3 | 0 |
| `test_products_api.py` | 4 | 4 | 0 |
| `test_cart_api.py` | 3 | 0 | 3 |
| `test_orders_api.py` | 2 | 0 | 2 |
| `test_users_api.py` | 2 | 1 | 1 |
| `test_negative_api.py` | 4 | 4 | 0 |
| `test_schema_validation.py` | 7 | 4 | 3 |
| `test_performance_api.py` | 5 | 5 | 0 |
| **Total** | **30** | **22** | **8** |

*\*Skipped tests target cart/order endpoints unavailable on the default Platzi Fake Store API. They activate when pointed at a full-featured ecommerce backend.*

### Validation Matrix

| Validation Type | UI Tests | API Tests |
|-----------------|----------|-----------|
| HTTP Status Code | — | ✅ 7 assertion methods |
| JSON Response | — | ✅ Key presence, types, values |
| JSON Schema | — | ✅ 7 schemas validated |
| Response Time | — | ✅ < 2 seconds SLA |
| Page Loaded | ✅ `is_loaded()` | — |
| Element Visibility | ✅ `is_visible()` | — |
| Text Content | ✅ `get_text()` | — |
| Error Messages | ✅ Form validation | ✅ `assert_error_message_contains()` |
| Business Rules | ✅ Cart count, sort | ✅ Positive ID, pagination |

---

## ✅ Best Practices Followed

<details>
<summary><strong>Click to expand — 40+ best practices</strong></summary>

1. **PEP8 Compliance** — all code follows Python style guidelines
2. **Type Hints** — every function has complete type annotations
3. **Docstrings** — Google-style on every public class and method
4. **No Hardcoded Values** — URLs in `endpoints.py`, data in JSON files, config in `.env`
5. **Single Responsibility** — each class has one clear purpose
6. **Open/Closed Principle** — extend without modifying existing code
7. **Dependency Injection** — fixtures inject dependencies into tests
8. **Page Object Model** — UI interactions abstracted behind page classes
9. **Reusable Base Classes** — `BasePage`, `APIClient`, `ReportManager`
10. **Explicit Waits** — `WebDriverWait` instead of `time.sleep()`
11. **JS-Centric Clicking** — robust element interaction via JavaScript
12. **Automatic Screenshots** — capture on every test failure
13. **Embedded Screenshots** — images attached to HTML report via extras API
14. **Structured Logging** — named loggers with file + console handlers
15. **Request/Response Logging** — every API call logged with timing
16. **Sensitive Data Masking** — authorization headers sanitized in logs
17. **JSON Schema Validation** — formal validation for all API responses
18. **Typed Data Models** — API responses mapped to dataclasses
19. **Centralized Endpoints** — all API paths in one maintainable class
20. **Factory Methods** — authentication strategies via factory constructors
21. **Automatic Token Refresh** — expired tokens refreshed transparently
22. **Retry Strategy** — exponential backoff for transient failures
23. **Session Reuse** — connection pooling via `requests.Session`
24. **Placeholder Substitution** — `{{random}}` for unique test data
25. **Smart Skipping** — `pytest.skip()` for unavailable endpoints
26. **Parallel Execution** — `pytest-xdist` for faster runs
27. **xdist-Aware Reporting** — worker results merged into unified summary
28. **Timestamped Reports** — every run in its own folder
29. **Report Cleanup** — automatic retention-based purging
30. **Environment Properties** — OS, browser, version captured in reports
31. **Summary JSON** — machine-readable aggregate results
32. **Failed Test Tracking** — dedicated `failed_tests.txt`
33. **CI/CD Artifacts** — reports uploaded in GitHub Actions and Jenkins
34. **Marker-Based Filtering** — granular test selection via 15 markers
35. **Unified Test Runner** — `run_tests.py` supports UI, API, or both
36. **Environment Variables** — `.env` for local, CI env vars for pipelines
37. **Faker Integration** — realistic randomized test data
38. **No Duplicate Code** — shared utilities across UI and API layers
39. **Changelog** — `CHANGELOG.md` documents every change
</details>

---

## 📈 Scalability

### Adding New UI Tests

```python
class NewPage(BasePage):
    SOME_ELEMENT = (By.ID, "new-element-id")
    def do_something(self) -> None:
        self.click(self.SOME_ELEMENT)

class TestNewFeature:
    def test_feature(self, logged_in_driver):
        NewPage(logged_in_driver).do_something()
```

### Adding New API Tests

```python
# Add endpoint → Add payload template → Add schema → Write test
class TestNewResourceAPI:
    def test_create(self, api_client, api_helpers):
        payload = api_helpers.load_payload("new_resource")
        response = api_client.post(APIEndpoints.new_resource(), json=payload)
        APIAssertions.assert_status_created(response)
```

**To extend utilities:** Add static methods to `APIAssertions` / `APIHelpers`, create dataclasses in `models/`, add JSON schemas to `schemas/`.

---

## 🔮 Future Enhancements

| Enhancement | Priority | Description |
|-------------|----------|-------------|
| **Docker Containerization** | High | Dockerfile + docker-compose for reproducible execution |
| **Visual Regression** | Medium | Pixel-level screenshot diffing (Percy, Applitools) |
| **API Contract Testing** | High | OpenAPI/Swagger contract validation |
| **Environment Health Check** | High | Pre-test validation of all dependencies |
| **Test Data Factories** | Medium | Programmatic data generation with factory_boy |
| **Slack/Teams Notifications** | Low | Pipeline notifications with report links |
| **Performance Benchmarking** | Low | Track response times across builds |
| **Database Validation** | Medium | Direct DB assertions for data integrity |
| **Load Testing Integration** | Low | k6 or Locust scripts for endpoint load validation |

---

## 📄 License

```
MIT License
Copyright (c) 2026 Rahul QA

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED.
```

---

## 👤 Author

**Rahul QA** — *Senior SDET*

[![GitHub](https://img.shields.io/badge/GitHub-181717?logo=github&logoColor=white)](https://github.com/rahul-qa)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0A66C2?logo=linkedin&logoColor=white)](https://linkedin.com/in/rahul-qa)
[![Email](https://img.shields.io/badge/Email-EA4335?logo=gmail&logoColor=white)](mailto:rahul@example.com)

---

<div align="center">

**Built with ❤️ using Python, Selenium, PyTest, and Requests**

*If you find this framework useful, please ⭐ star the repository!*

[![Back to Top](https://img.shields.io/badge/⬆_Back_to_Top-8A2BE2)](#-selenium--pytest-enterprise-automation-framework)

</div>
