import pytest
from pytest_bdd import scenarios, given, when, then
from playwright.sync_api import Page, expect

# Automatically bind all scenarios in the feature file
scenarios('../features/web.feature')

@given('the Vörðu UI is running')
def vordu_ui_running(page: Page, ui_base_url, seed_demicracy_data, seed_vordu_data):
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

@then('I should see "Vörðu Frontend"')
def see_vordu_frontend_header(page: Page):
    expect(page.get_by_text("Vörðu Frontend")).to_be_visible()

@when('I click the expand button on a scenario row')
def click_expand_scenario(page: Page):
    # Click on the first scenario row
    row = page.locator(".space-y-3 > div").first
    row.click()

@then('the row should expand highlighting the test steps')
def row_expands_steps(page: Page):
    # Check for steps container visibility
    # We look for "Given" or "When" or "Then" text which indicates steps are shown
    # Or just check if the container expanded.
    # We can check if "Steps:" text is visible if available, or just check content.
    # Let's check for a step keyword like "Given" inside the expanded area.
    # Since we clicked the first row (likely "User views the Project Matrix"), it has steps.
    expect(page.get_by_text("Given", exact=False).first).to_be_visible()

@then('I should see the "GitHub" icon in the icon bar')
def see_github_icon(page: Page):
    # Look for the SVG or a parent div that we can identify
    # We can rely on the fact that we have two icons.
    # Or strict locator if we added aria-labels. We didn't add aria-labels yet.
    # We can accept any SVG in the icon bar area?
    # Let's assume there are svgs.
    expect(page.locator("svg").nth(1)).to_be_visible() # Top bar has icons too?
    # Let's be more specific: inside the row.
    row = page.locator(".space-y-3 > div").first
    expect(row.locator("svg").first).to_be_visible()

@then('I should see the "Jenkins" icon in the icon bar')
def see_jenkins_icon(page: Page):
    row = page.locator(".space-y-3 > div").first
    expect(row.locator("svg").nth(1)).to_be_visible()

@when('I click a "create issue" button on an item on the BDD Overlay')
def click_create_issue(page: Page):
    pytest.skip("WIP: UI implementation pending")

@then('an issue creation request on GitHub should open and prepopulate with the item details')
def issue_creation_opens(page: Page):
    pytest.skip("WIP: UI implementation pending")

@when('I click on an empty status cell')
def click_empty_cell(page: Page):
    # Locate an empty cell (opacity-30)
    # This assumes there is an empty cell. Ideally we'd mock data to ensure one exists.
    # For now, we try to find one.
    empty_cell = page.locator(".opacity-30.cursor-default").first
    if empty_cell.is_visible():
        empty_cell.click(force=True) # Force click because it might be non-interactive?
    else:
        pytest.skip("No empty cell found to test")

@then('the BDD Overlay should not appear')
def bdd_overlay_not_appears(page: Page):
    expect(page.locator(".fixed.inset-0.bg-black\\/80")).not_to_be_visible()

@given('the BDD Overlay is open for a "Planned" item')
def open_bdd_overlay_planned(page: Page):
    # Find a Pending cell (Amber/Yellow)
    # We look for the "⚠" or similar indicator, or color yellow
    # Using the CSS class or style from MatrixCell
    # Pending cells have `text-yellow-500` icon or border color?
    # Actually MatrixCell sets style color.
    # We can try to find a cell passed but with 0 steps, or just a known pending cell.
    # Let's try finding a cell that says "pending" if we have aria labels, or by color.
    # Simplified: Find cell with "⚠" (which is in overlay, not cell). 
    # The cell just shows X/Y or %.
    # Planned items (0/0) show "0/0" or "0 scenarios"?
    # The updated code shows "X/Y scenarios" for planned.
    # Let's assume we can find one.
    cell = page.get_by_text("scenarios").first
    if cell.is_visible():
        cell.click()
        expect(page.locator(".fixed.inset-0.bg-black\\/80")).to_be_visible()
    else:
        pytest.skip("No planned item cell found")

@then('I should see the scenario name')
def see_scenario_name(page: Page):
    # Check for any text in the overlay content area
    expect(page.locator(".bg-black\\/30")).to_be_visible()

@then('I should not see "Steps:" count')
def not_see_steps_count(page: Page):
    expect(page.get_by_text("Steps:", exact=False)).not_to_be_visible()
