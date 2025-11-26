Feature: Infrastructure & Tooling
    As a Platform Engineer
    I want to ensure the CI/CD pipeline is robust
    So that developers can ship code with confidence

    @vordu:project=vordu @vordu:row=api @vordu:phase=1 @wip
    Scenario: Jenkins Allure Integration
        Given the Jenkins pipeline is configured
        When I run a build with Allure enabled
        Then the Allure report should be generated
        And the report should contain BDD test results

    @vordu:project=vordu @vordu:row=frontend @vordu:phase=2 @wip
    Scenario: Visual Regression Testing
        Given the UI is deployed
        When I run Percy or similar tool
        Then I should see visual diffs for changed components
