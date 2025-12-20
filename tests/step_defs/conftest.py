import pytest
import os
import requests
from pytest_bdd import given, when, then, parsers

# -----------------------------------------------------------------------------
# Fixtures
# -----------------------------------------------------------------------------

@pytest.fixture
def api_base_url():
    """Returns the base URL for the API."""
    return os.getenv("API_BASE_URL", "http://localhost:8000")

@pytest.fixture
def ui_base_url():
    """Returns the base URL for the UI."""
    # Default to Vite dev server locally, or API static serve in CI
    return os.getenv("UI_BASE_URL", "http://localhost:5173")

@pytest.fixture
def seed_demicracy_data(api_base_url):
    """Fixture to ensure Demicracy data exists for UI tests."""
    
    # 1. Seed Configuration (Required for UI to render the row)
    config_payload = {
        "system": {
            "name": "Demicracy",
            "label": "Demicracy",
            "description": "Digital Democracy",
            "domain": "SiliconSaga"
        },
        "components": [
            {
                "name": "identity",
                "label": "Identity",
                "system": "Demicracy"
            }
        ]
    }
    
    # 2. Seed Status
    status_payload = [
        {
            "project_name": "Demicracy",
            "row_id": "identity",
            "phase_id": 1, 
            "status": "pass",
            "completion": 100,
            "scenarios_total": 1,
            "scenarios_passed": 1,
            "steps_total": 5,
            "steps_passed": 5
        }
    ]
    
    try:
        # Seed Config
        requests.post(f"{api_base_url}/config/ingest", json=config_payload, headers={"X-API-Key": "dev-key"})
        # Seed Status
        requests.post(f"{api_base_url}/ingest", json=status_payload, headers={"X-API-Key": "dev-key"})
    except Exception as e:
        print(f"Warning: Failed to seed data: {e}")

# -----------------------------------------------------------------------------
# Generic WIP Steps
# -----------------------------------------------------------------------------

@given(parsers.parse('the Kafka broker is reachable'))
@given(parsers.parse('the system is configured for Event Sourcing'))
@given(parsers.parse('a corrupted Read-Database'))
@given(parsers.parse('the Vörðu ingestion pipeline is configured for "Insert-Only" mode'))
@given(parsers.parse('multiple ingestion runs have occurred over time'))
@given(parsers.parse('I am viewing the Vörðu Dashboard'))
def wip_given_steps():
    pytest.skip("WIP: Feature Not Implemented Yet")

@when(parsers.parse('the Vörðu API initializes'))
@when(parsers.parse('I post a new Roadmap Ingestion Event'))
@when(parsers.parse('I trigger a "Replay History" maintenance action'))
@when(parsers.parse('a new build triggers an ingestion event'))
@when(parsers.parse('I query the "/matrix/history" endpoint'))
@when(parsers.parse('I select the "History" tab'))
def wip_when_steps():
    pytest.skip("WIP: Feature Not Implemented Yet")

@then(parsers.parse('it should successfully connect to the "vordu-events" topic'))
@then(parsers.parse('create the topic if it does not exist'))
@then(parsers.parse('the event should be published to Kafka'))
@then(parsers.parse('the Read-Database should be updated by consuming the event'))
@then(parsers.parse('the system should consume all events from Offset 0'))
@then(parsers.parse('the Vörðu Matrix should match the expected state'))
@then(parsers.parse('the event should be appended to the "vordu-history" Kafka topic'))
@then(parsers.parse('the database should not update existing rows in place'))
@then(parsers.parse('insert new rows with a unique "run_id"'))
@then(parsers.parse('I should receive a time-series dataset defined by "run_id"'))
@then(parsers.parse('the dataset should accurately reflect the granularity active at each point in time'))
@then(parsers.parse('I should see a graph plotting Total vs Passed scenarios over time'))
@then(parsers.parse('I should be able to filter by System or Component'))
def wip_then_steps():
    pytest.skip("WIP: Feature Not Implemented Yet")
