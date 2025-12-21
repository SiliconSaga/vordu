Feature: Vörðu API
    As a CI/CD pipeline
    I want to ingest Cucumber JSON reports
    So that the matrix reflects the latest test results

    @vordu:project=vordu @vordu:row=vordu-api @vordu:phase=0
    Scenario: Ingest Cucumber JSON
        Given the API is running
        When I POST a Cucumber JSON report to "/ingest"
        Then the response status should be 200
        And the database should contain the new test results
