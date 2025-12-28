@vordu:project=vordu @vordu:row=vordu-web
Feature: Vörðu Frontend
    As a user
    I want to view the project matrix and details
    So that I can understand the status of the ecosystem

    @vordu:phase=0
    Scenario: User views the Project Matrix
        Given the Vörðu UI is running
        When I visit the home page
        Then I should see the "VÖRÐU" header
        And I should see the "Vordu" project row

    @vordu:phase=1
    Scenario: User opens BDD Overlay
        Given the Vörðu UI is running
        When I click on a status cell
        Then the BDD Overlay should appear
        And I should see "Vörðu Frontend"

    @vordu:phase=1
    Scenario: User expands a scenario row
        Given the Vörðu UI is running
        And the BDD Overlay is open
        When I click the expand button on a scenario row
        Then the row should expand highlighting the test steps

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