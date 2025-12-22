Feature: Vörðu Frontend
    As a user
    I want to view the project matrix and details
    So that I can understand the status of the ecosystem

    @vordu:phase=0
    Scenario: User views the Project Matrix
        Given the Vörðu UI is running
        When I visit the home page
        Then I should see the "VÖRÐU" header
        And I should see the "Demicracy" project row

    @vordu:phase=1
    Scenario: User opens BDD Overlay
        Given the Vörðu UI is running
        When I click on a status cell
        Then the BDD Overlay should appear
        And I should see "Verified Features"

    @vordu:phase=2 @wip
    Scenario: User clicks item on the BDD Overlay
        Given the Vörðu UI is running
        And the BDD Overlay is open
        When I click an item on the BDD Overlay
        Then the BDD Overlay should expand to show the Scenario Steps

    @vordu:phase=3 @wip
    Scenario: User clicks "create issue" on an item on the BDD Overlay
        Given the Vörðu UI is running
        And the BDD Overlay is open
        When I click a "create issue" button on an item on the BDD Overlay
        Then an issue creation request on GitHub should open and prepopulate with the item details

    @vordu:phase=0
    Scenario: User clicks an empty cell
        Given the Vörðu UI is running
        When I click on an empty status cell
        Then the BDD Overlay should not appear

    @vordu:phase=2 @wip
    Scenario: User views planned feature details
        Given the Vörðu UI is running
        And the BDD Overlay is open for a "Planned" item
        Then I should see the scenario name
        But I should not see "Steps:" count