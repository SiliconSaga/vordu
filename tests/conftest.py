import os
import pytest
from playwright.sync_api import sync_playwright

@pytest.fixture(scope="session")
def browser_context():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        yield context
        browser.close()

@pytest.fixture(scope="function")
def page(browser_context):
    page = browser_context.new_page()
    yield page
    page.close()

@pytest.fixture
def api_base_url():
    return os.getenv("API_BASE_URL", "http://127.0.0.1:8000") # Avoid IPv6 issues

@pytest.fixture
def ui_base_url():
    return os.getenv("UI_BASE_URL", "http://localhost:5173") # Better for local dev

def pytest_configure(config):
    """Register dynamic markers from feature files to avoid warnings."""
    # Common BDD tags used in Vordu
    markers = [
        "vordu",
        "vordu:phase=0",
        "vordu:project=vordu",
        "vordu:row=api",
        "vordu:row=database",
        "vordu:row=frontend",
    ]
    for marker in markers:
        config.addinivalue_line("markers", marker)
