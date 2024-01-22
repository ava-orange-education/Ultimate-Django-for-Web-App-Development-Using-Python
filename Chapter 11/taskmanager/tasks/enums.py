from enum import Enum


class TaskStatus(str, Enum):
    UNASSIGNED = "UNASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"
    ARCHIVED = "ARCHIVED"
