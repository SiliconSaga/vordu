from pytest_bdd import scenario, given, when, then, parsers

@scenario('../features/database.feature', 'Persist Project Structure')
def test_persist_project_structure():
    pass

@given('a clean database')
def clean_database():
    # Logic to reset DB
    pass

@when('I create a new project "Vordu-Self-Test"')
def create_new_project():
    # Logic to insert project
    pass

@then('I should be able to retrieve it by ID')
def retrieve_project_by_id():
    # Logic to query project
    pass
