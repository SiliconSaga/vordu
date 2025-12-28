Feature: Vörðu Data
    As the system
    I want to persist project data
    So that status is preserved between restarts

    @phase:1 @wip
    Scenario: Kafka Connectivity
        Given the Kafka broker is reachable
        When the Vörðu API initializes
        Then it should successfully connect to the "vordu-events" topic
        And create the topic if it does not exist

    @phase:2 @wip
    Scenario: Persist via Event Stream
        Given the system is configured for Event Sourcing
        When I post a new Roadmap Ingestion Event
        Then the event should be published to Kafka
        And the Read-Database should be updated by consuming the event

    @phase:3 @wip
    Scenario: Rebuild State from History
        Given a corrupted Read-Database
        When I trigger a "Replay History" maintenance action
        Then the system should consume all events from Offset 0
        And the Vörðu Matrix should match the expected state
