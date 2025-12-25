import os
import pytest
from playwright.sync_api import sync_playwright
import sys

# Ensure resources scripts are in path
scripts_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "resources", "scripts"))
if scripts_path not in sys.path:
    sys.path.append(scripts_path)

import vordu_ingest

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
    # Set default timeout to 10 seconds for robustness
    page.set_default_timeout(10000)
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
    """Seeds the Vordu project configuration using real ingestion."""
    catalog_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "catalog-info.yaml"))
    
    # 1. Parse Catalog
    entities = vordu_ingest.parse_catalog(catalog_path)
    vordu_data = vordu_ingest.extract_vordu_metadata(entities)
    
    # 2. Ingest Config
    config_payload = vordu_ingest.build_config_payload(vordu_data)
    requests.post(f"{api_base_url}/config/ingest", json=config_payload, headers={"X-API-Key": "dev-key"})
    
    # 3. Scan Features (Real "Planned" Data)
    root_dir = os.path.dirname(catalog_path)
    scanned_features = vordu_ingest.scan_feature_files(root_dir, vordu_data['system'])
    
    # 4. Ingest Status (Planned items only, no execution results yet)
    status_payload = vordu_ingest.build_status_payload(vordu_data, scanned_features)
    requests.post(f"{api_base_url}/ingest", json=status_payload, headers={"X-API-Key": "dev-key"})
