Feature: Demicracy Core
    As a Citizen
    I want to participate in digital democracy
    So that my voice is heard

    @vordu:project=demicracy @vordu:row=identity @vordu:phase=0 @wip
    Scenario: Core Identity Module
        Given the identity service is running
        When I register a new user
        Then I should receive a unique DID

    @vordu:project=demicracy @vordu:row=identity @vordu:phase=1 @wip
    Scenario: OAuth Integration
        Given I have a Google account
        When I sign in with OAuth
        Then my identity should be linked

    @vordu:project=demicracy @vordu:row=governance @vordu:phase=1 @wip
    Scenario: Voting Mechanism
        Given a proposal is open
        When I cast a vote
        Then the vote count should increment
