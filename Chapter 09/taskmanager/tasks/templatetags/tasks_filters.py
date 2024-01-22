from django import template
from django.db.models import Case, Count, When

register = template.Library()


@register.filter
def percent_complete(tasks):
    if tasks.exists():
        # Aggregate count of all tasks and count of completed tasks
        aggregation = tasks.aggregate(
            total=Count("id"), done=Count(Case(When(status="DONE", then=1)))
        )

        # Calculate the percentage
        percent_done = (aggregation["done"] / aggregation["total"]) * 100
        return percent_done
    else:
        return 0
