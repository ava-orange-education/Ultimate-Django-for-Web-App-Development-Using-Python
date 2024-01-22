@django_db
Feature: Task Claiming
    Scenario: User creates and claims a task
	Given a user with necessary permissions
	When the user creates a task
	And the user claims the created task
	Then when the user lists tasks, the created task is shown as claimed
