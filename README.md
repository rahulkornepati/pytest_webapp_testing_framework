# Selenium Pytest Automation Framework

A scalable and maintainable UI automation framework built using **Python**, **Selenium WebDriver**, and **Pytest**.

The framework automates the SauceDemo web application while following modern automation design principles such as the **Page Object Model (POM)**, reusable utilities, modular page classes, centralized test data, detailed reporting, and Continuous Integration support.

The project has been designed to be simple enough for learning while still following practices commonly used in real-world automation projects.

---

# Application Under Test

https://www.saucedemo.com/

---

# Tech Stack

| Technology | Purpose in Framework |
|------------|---------------------|
| Python | Core programming language used to build the framework |
| Selenium WebDriver | Browser automation and UI interaction |
| Pytest | Test execution framework, fixtures, assertions and markers |
| Page Object Model (POM) | Separates page locators and business actions from test cases |
| WebDriver Manager / Selenium Manager | Automatically manages browser drivers |
| Pytest HTML | Generates HTML execution reports |
| Pytest xdist | Executes tests in parallel |
| Allure Pytest | Supports rich reporting integration |
| Jenkins | Continuous Integration pipeline |
| GitHub Actions | Cloud-based CI execution |
| HTML Reports | Stores execution summary for every run |
| JUnit XML | CI compatible execution report |
| JSON Test Data | Externalized user credentials and checkout data |
| Logging | Records execution flow for debugging |
| Git | Version control |
| GitHub | Source code repository and collaboration |

---

# Framework Architecture

```
ecommerce_selenium_pytest_framework

│
├── pages/
│   ├── Login Page
│   ├── Inventory Page
│   ├── Cart Page
│   ├── Checkout Pages
│   ├── Header
│   ├── Footer
│   └── Base Page
│
├── tests/
│   ├── Login Tests
│   ├── Inventory Tests
│   └── Checkout Tests
│
├── test_data/
│   ├── users.json
│   └── checkout_customers.json
│
├── utils/
│   ├── Config Reader
│   └── Report Manager
│
├── reports/
│
├── conftest.py
├── pytest.ini
├── Jenkinsfile
├── requirements.txt
└── run_tests.py
```

---

# Framework Design Pattern

The project follows the **Page Object Model (POM)** design pattern.

Each web page has its own class containing:

- Web element locators
- Page-specific actions
- Reusable methods

The test classes only contain validation logic and business scenarios, making them easy to read and maintain.

---

# Features

- Page Object Model architecture
- Modular page classes
- Reusable Selenium utilities
- Externalized test data
- Cross-browser execution
- Headless execution
- Parallel execution support
- HTML reports
- JUnit XML reports
- Structured execution logs
- Automatic failure screenshots
- Timestamp-based report generation
- Jenkins pipeline
- GitHub Actions workflow
- Configurable execution using command-line arguments

---

# Technologies Used

## Python

Python is used as the primary programming language for developing reusable automation code.

Used in:

- Page Objects
- Test Cases
- Utility Classes
- Configuration
- Reporting
- Framework Runner

---

## Selenium WebDriver

Responsible for browser automation.

Used for:

- Browser launch
- Element identification
- User interactions
- Validations
- Navigation

---

## Pytest

Acts as the test execution engine.

Used for:

- Fixtures
- Assertions
- Test Discovery
- Markers
- Parameterization
- Command-line execution

---

## Page Object Model

Implemented inside the **pages** package.

Each page exposes reusable methods such as:

- Login
- Add Product
- Remove Product
- Checkout
- Cart Operations

This minimizes duplicate Selenium code.

---

## JSON Test Data

Application test data is stored separately from the test scripts.

Current files include:

- users.json
- checkout_customers.json

Benefits:

- Easy maintenance
- Data-driven testing
- Cleaner test code

---

## Logging

Execution logs are automatically generated for every run.

Logs help identify:

- Execution flow
- Failed actions
- Debugging information

---

## HTML Reporting

Each execution generates an HTML report containing:

- Test summary
- Pass/Fail status
- Execution duration
- Failure details

---

## Screenshot Capture

Whenever a test fails:

- Screenshot is captured automatically
- Screenshot is stored inside the execution folder
- Screenshot is linked to the report

This significantly reduces debugging effort.

---

## Parallel Execution

The framework supports parallel execution using **pytest-xdist**.

Useful for:

- Regression Suite
- Faster execution
- CI pipelines

---

## Jenkins Integration

The project includes a ready-to-use Jenkins Pipeline.

Pipeline stages include:

- Checkout source code
- Install dependencies
- Execute tests
- Archive reports
- Publish HTML reports
- Publish JUnit reports

---

## GitHub Actions

The repository contains a GitHub Actions workflow for cloud execution.

The workflow:

- Installs Python
- Installs project dependencies
- Executes automation suite
- Uploads execution reports

---

# Test Data Management

Test data is maintained separately from automation logic.

Current datasets include:

- Login users
- Checkout customer information

This approach improves maintainability and scalability.

---

# Reporting Structure

Every execution creates a separate timestamped report folder.

Typical report contents include:

- HTML Report
- Execution Log
- JUnit XML
- Environment Details
- Failure Summary
- Screenshots
- Summary JSON

Older reports are automatically cleaned based on the configured retention period.

---

# Running the Project

## Install dependencies

```bash
pip install -r requirements.txt
```

---

## Execute all tests

```bash
pytest
```

---

## Execute smoke suite

```bash
pytest -m smoke
```

---

## Execute in headless mode

```bash
python run_tests.py --browser chrome --headless
```

---

## Execute in parallel

```bash
python run_tests.py --workers auto
```

---

# CI/CD Support

The framework is ready for Continuous Integration.

Supported platforms:

- Jenkins
- GitHub Actions

Execution artifacts generated during CI include:

- HTML Report
- JUnit XML
- Execution Logs
- Screenshots

---

# Current Test Coverage

The framework currently covers:

- Login functionality
- Product inventory validation
- Product details page
- Add to Cart
- Remove from Cart
- Checkout workflow
- Header validation
- Footer validation
- Cart functionality

---

# Why This Framework?

This framework demonstrates many of the engineering practices followed in production automation projects:

- Clean project structure
- Modular Page Object Model
- Reusable components
- Data-driven testing
- Detailed reporting
- Parallel execution
- Cross-browser support
- CI/CD integration
- Maintainable and scalable design

The project can be easily extended by adding new Page Objects and Test Classes without impacting the existing framework.
