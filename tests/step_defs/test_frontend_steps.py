import pytest
from pytest_bdd import scenarios, given, when, then
from playwright.sync_api import Page, expect

# Automatically bind all scenarios in the feature file
scenarios('../features/frontend.feature')

@given('the Vörðu UI is running')
def vordu_ui_running(page: Page, ui_base_url, seed_demicracy_data):
    page.goto(ui_base_url)

@given('the BDD Overlay is open')
def open_bdd_overlay(page: Page):
    # Ensure we are on the page
    # page.goto(ui_base_url) # handled by previous given
    # Click status cell to open overlay
    cell = page.get_by_text("1/1").first
    expect(cell).to_be_visible()
    cell.click()
    expect(page.locator(".fixed.inset-0.bg-black\\/80")).to_be_visible()

@when('I visit the home page')
def visit_home_page(page: Page, ui_base_url):
    page.goto(ui_base_url)

@then('I should see the "VÖRÐU" header')
def see_vordu_header(page: Page):
    # Use exact=True or specify level to distinguish from project headers
    expect(page.get_by_role("heading", name="VÖRÐU", level=1)).to_be_visible()

@then('I should see the "Demicracy" project row')
def see_demicracy_row(page: Page):
    expect(page.get_by_text("Demicracy")).to_be_visible()

@when('I click on a status cell')
def click_status_cell(page: Page):
    # Find a cell with "1/1" (Scenario count) text and click it
    # We prefer counts over percentages now.
    cell = page.get_by_text("1/1").first
    expect(cell).to_be_visible()
    cell.click()

@then('the BDD Overlay should appear')
def bdd_overlay_appears(page: Page):
    # Check for the overlay container or a specific element inside it
    expect(page.locator(".fixed.inset-0.bg-black\\/80")).to_be_visible()

@then('I should see "Verified Features"')
def see_verified_features(page: Page):
    expect(page.get_by_text("Verified Features")).to_be_visible()

@when('I click an item on the BDD Overlay')
def click_item_bdd_overlay(page: Page):
    pytest.skip("WIP: UI implementation pending")

@then('the BDD Overlay should expand to show the Scenario Steps')
def bdd_overlay_expands(page: Page):
    pytest.skip("WIP: UI implementation pending")

@when('I click a "create issue" button on an item on the BDD Overlay')
def click_create_issue(page: Page):
    pytest.skip("WIP: UI implementation pending")

@then('an issue creation request on GitHub should open and prepopulate with the item details')
def issue_creation_opens(page: Page):
    pytest.skip("WIP: UI implementation pending")
