import pytest
import requests
from pytest_bdd import scenario, given, when, then, parsers

@scenario('../features/api.feature', 'Ingest Cucumber JSON')
def test_ingest_cucumber_json():
    pass

@given('the API is running')
def api_running(api_base_url):
    try:
        response = requests.get(f"{api_base_url}/docs")
        assert response.status_code == 200
    except requests.exceptions.ConnectionError:
        pytest.fail("API is not running")

@when('I POST a Cucumber JSON report to "/ingest"')
def post_cucumber_report(api_base_url):
    # Mock Cucumber JSON payload
    payload = [
        {
            "project_name": "vordu-test",
            "row_id": "api-test",
            "phase_id": 0,
            "status": "pass",
            "completion": 100
        }
    ]
    try:
        response = requests.post(f"{api_base_url}/ingest", json=payload)
        pytest.response = response
    except requests.exceptions.ConnectionError:
        pytest.fail("Failed to connect to API")

@then('the response status should be 200')
def response_status_200():
    assert hasattr(pytest, 'response'), "No response captured"
    assert pytest.response.status_code == 200

@then('the database should contain the new test results')
def database_contains_results(api_base_url):
    # Query the API to verify persistence
    response = requests.get(f"{api_base_url}/matrix")
    assert response.status_code == 200
    data = response.json()
    
    # Find our test item
    found = any(
        item['project'] == 'vordu-test' and 
        item['row'] == 'api-test' and 
        item['completion'] == 100 
        for item in data
    )
    assert found, "Ingested item not found in matrix"
