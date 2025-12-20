Feature: Vörðu Frontend
    As a user
    I want to view the project matrix and details
    So that I can understand the status of the ecosystem

    @vordu:project=vordu @vordu:row=frontend @vordu:phase=0
    Scenario: User views the Project Matrix
        Given the Vörðu UI is running
        When I visit the home page
        Then I should see the "VÖRÐU" header
        And I should see the "Demicracy" project row

    Scenario: User opens BDD Overlay
        Given the Vörðu UI is running
        When I click on a status cell
        Then the BDD Overlay should appear
        And I should see "Verified Features"
