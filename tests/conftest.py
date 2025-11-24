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

def pytest_bdd_apply_tag(tag, function):
    """
    Custom tag parsing for Vordu BDD tags.
    Converts 'vordu:key=value' into @pytest.mark.vordu(key=value).
    """
    if tag.startswith("vordu:"):
        try:
            # Parse the tag: "vordu:row=api" -> key="row", value="api"
            parts = tag.split(":", 1)[1]
            if "=" in parts:
                key, value = parts.split("=", 1)
                # Apply marker with kwargs: @pytest.mark.vordu(row="api")
                marker = pytest.mark.vordu(**{key: value})
                marker(function)
            else:
                # Handle bare "vordu" tag if needed, or ignore
                pass
            
            return True
        except ValueError:
            pass
            
    return None
