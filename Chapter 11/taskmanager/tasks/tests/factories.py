import factory
from accounts.models import Organization
from django.contrib.auth import get_user_model
from tasks.models import Task, TaskStatus


class OrganizationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Organization


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()

    username = factory.Faker("user_name")
    email = factory.Faker("email")
    organization = factory.SubFactory(OrganizationFactory)


class TaskFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Task

    title = factory.Faker("sentence", nb_words=4)
    description = factory.Faker("paragraph")
    status = factory.Iterator([status.value for status in TaskStatus])

    creator = factory.SubFactory(UserFactory)

    # The owner field can either be null or an instance of the User model.
    # This creates a User instance 50% of the time, and sets owner to None 50% of the time.
    owner = factory.Maybe(
        factory.Faker("pybool"),
        yes_declaration=factory.SubFactory(UserFactory),
        no_declaration=None,
    )

    version = factory.Sequence(lambda n: n)
