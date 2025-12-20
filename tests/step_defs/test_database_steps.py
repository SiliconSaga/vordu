from pytest_bdd import scenarios, given, when, then

scenarios('../features/database.feature')

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
