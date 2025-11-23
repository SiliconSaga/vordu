Feature: Vörðu Database
    As the system
    I want to persist project data
    So that status is preserved between restarts

    @vordu:project=vordu @vordu:row=database @vordu:phase=0
    Scenario: Persist Project Structure
        Given a clean database
        When I create a new project "Vordu-Self-Test"
        Then I should be able to retrieve it by ID
