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

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "viewport": {"width": 1280, "height": 720},
    }

@pytest.fixture(scope="function", autouse=True)
def configure_timeout(page):
    # Set default timeout to 2 seconds for faster fail-fast
    page.set_default_timeout(2000)
    return page

import requests

@pytest.fixture(scope="function", autouse=True)
def clean_db(api_base_url):
    """Ensures a clean database state before every test."""
    try:
        # Pass dev-key for admin access
        requests.delete(f"{api_base_url}/admin/db", headers={"X-API-Key": "dev-key"})
    except requests.ConnectionError:
        pass # API might not be running if unit tests only

@pytest.fixture
def seed_demicracy_data(api_base_url):
    """Seeds the Demicracy project configuration."""
    payload = {
        "system": {
            "name": "demicracy",
            "label": "Demicracy",
            "description": "Core Project",
            "domain": "Governance"
        },
        "components": [
            {"name": "frontend", "label": "Frontend", "system": "demicracy"},
            {"name": "api", "label": "API", "system": "demicracy"}
        ]
    }
    requests.post(f"{api_base_url}/config/ingest", json=payload, headers={"X-API-Key": "dev-key"})
    
    # Also seed a mock status to make it visible/clickable (100% completion)
    status_payload = [
        # Phase 0: 50%
        {
            "project_name": "demicracy",
            "row_id": "frontend",
            "phase_id": 0,
            "status": "pending",
            "completion": 50,
            "scenarios_total": 2,
            "scenarios_passed": 1,
            "steps_total": 10,
            "steps_passed": 5
        },
        # Phase 1: 100% (The target for our test)
        {
            "project_name": "demicracy",
            "row_id": "frontend",
            "phase_id": 1,
            "status": "pass",
            "completion": 100,
            "scenarios_total": 1,
            "scenarios_passed": 1,
            "steps_total": 5,
            "steps_passed": 5
        },
        # Phase 2: 0%
        {
            "project_name": "demicracy",
            "row_id": "frontend",
            "phase_id": 2,
            "status": "empty",
            "completion": 0,
            "scenarios_total": 0,
            "scenarios_passed": 0,
            "steps_total": 0,
            "steps_passed": 0
        },
        # Phase 3: 0%
        {
            "project_name": "demicracy",
            "row_id": "frontend",
            "phase_id": 3,
            "status": "empty",
            "completion": 0,
            "scenarios_total": 0,
            "scenarios_passed": 0,
            "steps_total": 0,
            "steps_passed": 0
        }
    ]
    requests.post(f"{api_base_url}/ingest", json=status_payload, headers={"X-API-Key": "dev-key"})

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
    
    elif tag == "wip":
        marker = pytest.mark.xfail(reason="Work in Progress (Roadmap Item)")
        marker(function)
        return True
            
    return None

@pytest.fixture
def seed_vordu_data(api_base_url):
    """Seeds the Vordu project configuration."""
    payload = {
        "system": {
            "name": "vordu",
            "label": "Vordu",
            "description": "Living Roadmap",
            "domain": "Meta"
        },
        "components": [
            {"name": "vordu-web", "label": "Web", "system": "vordu"},
            {"name": "vordu-api", "label": "API", "system": "vordu"}
        ]
    }
    requests.post(f"{api_base_url}/config/ingest", json=payload, headers={"X-API-Key": "dev-key"})
    
    # Seed mock status
    status_payload = [
        # Phase 0: 100%
        {
            "project_name": "vordu",
            "row_id": "vordu-web",
            "phase_id": 0,
            "status": "pass",
            "completion": 100,
            "scenarios_total": 2,
            "scenarios_passed": 2,
            "steps_total": 4,
            "steps_passed": 4
        },
        # Phase 1: 50% (Target)
        {
            "project_name": "vordu",
            "row_id": "vordu-web",
            "phase_id": 1,
            "status": "pending",
            "completion": 50,
            "scenarios_total": 2,
            "scenarios_passed": 1,
            "steps_total": 10,
            "steps_passed": 5
        }
    ]
    requests.post(f"{api_base_url}/ingest", json=status_payload, headers={"X-API-Key": "dev-key"})
