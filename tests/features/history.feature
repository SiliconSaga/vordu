Feature: Roadmap History & Analytics

  As a Project Manager
  I want to track roadmap progress over time
  So that I can visualize trends and velocity

  @component:vordu-data @phase:2
  Scenario: Kafka Event Sourcing for History
    Given the Vörðu ingestion pipeline is configured for "Insert-Only" mode
    When a new build triggers an ingestion event
    Then the event should be appended to the "vordu-history" Kafka topic
    And the database should not update existing rows in place
    But insert new rows with a unique "run_id"

  @component:vordu-api @phase:2
  Scenario: Querying Historical Trends
    Given multiple ingestion runs have occurred over time
    When I query the "/matrix/history" endpoint
    Then I should receive a time-series dataset defined by "run_id"
    And the dataset should accurately reflect the granularity active at each point in time

  @component:vordu-web @phase:3
  Scenario: Visualizing Burn-down Charts
    Given I am viewing the Vörðu Dashboard
    When I select the "History" tab
    Then I should see a graph plotting Total vs Passed scenarios over time
    And I should be able to filter by System or Component
