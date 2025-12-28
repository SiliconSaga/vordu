import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from playwright.sync_api import Page, expect

# Automatically bind all scenarios in the feature file
scenarios('../features/integrations.feature')

# Import steps from test_web_steps to share "Given the Vörðu UI is running" etc.
from tests.step_defs.test_web_steps import *

@then('I should see the "GitHub" icon in the icon bar')
def see_github_icon(page: Page):
    row = page.locator(".space-y-3 > div").first
    expect(row.get_by_alt_text("See scenario definition on GitHub")).to_be_visible()

@then('I should see the "Jenkins" icon in the icon bar')
def see_jenkins_icon(page: Page):
    row = page.locator(".space-y-3 > div").first
    expect(row.get_by_alt_text("See scenario results in Jenkins")).to_be_visible()

@then('I should see the "GitHub Create Issue" icon in the icon bar')
def see_github_create_issue_icon(page: Page):
    row = page.locator(".space-y-3 > div").first
    expect(row.get_by_alt_text("Create an issue for this scenario on GitHub")).to_be_visible()

# New failing steps for integrations.feature

@given('I have a valid GitHub token configured')
def valid_github_token():
    assert False, "Not implemented yet"

@given('the "vordu-web" component has a valid GitHub slug')
def component_has_github_slug():
    assert False, "Not implemented yet"

@given('the "vordu-web" component has a valid Jenkins job')
def component_has_jenkins_job():
    assert False, "Not implemented yet"

@given('the scenario exists on the main branch')
def scenario_exists_on_main():
    assert False, "Not implemented yet"

@when('I click the "GitHub" icon in the icon bar')
def click_github_icon(page: Page):
    assert False, "Not implemented yet"

@then('the icon should show a loading spinner')
def icon_shows_spinner(page: Page):
    assert False, "Not implemented yet"

@then('the system should identify the source file and line number')
def system_identifies_source():
    assert False, "Not implemented yet"

@then('a new tab should open to the correct GitHub URL')
def new_tab_opens_github(page: Page):
    assert False, "Not implemented yet"

@given('the scenario text cannot be found in the main branch')
def scenario_not_found_on_main():
    assert False, "Not implemented yet"

@then('I should see an error message "Scenario not found in current main branch"')
def see_error_message_scenario_not_found(page: Page):
    assert False, "Not implemented yet"

@when('I click the "Jenkins" icon in the icon bar')
def click_jenkins_icon(page: Page):
    assert False, "Not implemented yet"

@then('a new tab should open to the Jenkins test report for the latest build')
def new_tab_opens_jenkins(page: Page):
    assert False, "Not implemented yet"

# @when('I click a "create issue" button on an item on the BDD Overlay')
# def click_create_issue(page: Page):
#     assert False, "WIP: UI implementation pending"

# @then('an issue creation request on GitHub should open and prepopulate with the item details')
# def issue_creation_opens(page: Page):
#     assert False, "WIP: UI implementation pending"