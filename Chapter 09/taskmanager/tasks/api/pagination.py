from typing import Any

from ninja import Schema
from ninja.pagination import PaginationBase


class TaskManagerPagination(PaginationBase):
    # only `skip` param, defaults to 5 per page
    class Input(Schema):
        skip_records: int

    class Output(Schema):
        items: list[Any]
        count: int
        page_size: int

    def paginate_queryset(self, queryset, pagination: Input, **params):
        skip_records = pagination.skip_records
        return {
            "data": queryset[skip_records : skip_records + 5],
            "count": queryset.count(),
            "page_size": 5,
        }
