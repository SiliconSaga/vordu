Feature: External Integrations
    As a Vörðu user
    I want to access related external resources directly from the dashboard
    So that I can quickly navigate to source code and test results

    Background:
        Given the Vörðu UI is running

    @component:vordu-web @phase:1
    Scenario: Integration icons validation
        Given the BDD Overlay is open
        When I click the expand button on a scenario row
        Then the row should expand highlighting the test steps
        And I should see the "GitHub" icon in the icon bar
        And I should see the "Jenkins" icon in the icon bar
        And I should see the "GitHub Create Issue" icon in the icon bar

    @component:vordu-web @phase:2
    Scenario: Navigate to GitHub source
        Given I have a valid GitHub token configured
        And the "vordu-web" component has a valid GitHub slug
        And the BDD Overlay is open
        And the scenario exists on the main branch
        When I click the "GitHub" icon in the icon bar
        Then the icon should show a loading spinner
        And the system should identify the source file and line number
        And a new tab should open to the correct GitHub URL

    @component:vordu-web @phase:2
    Scenario: GitHub source not found
        Given I have a valid GitHub token configured
        And the "vordu-web" component has a valid GitHub slug
        And the BDD Overlay is open
        But the scenario text cannot be found in the main branch
        When I click the "GitHub" icon in the icon bar
        Then the icon should show a loading spinner
        And I should see an error message "Scenario not found in current main branch"

    @component:vordu-web @phase:2
    Scenario: Navigate to Jenkins test report
        Given the "vordu-web" component has a valid Jenkins job
        And the BDD Overlay is open
        When I click the "Jenkins" icon in the icon bar
        Then a new tab should open to the Jenkins test report for the latest build
