from enum import StrEnum, auto


class TodoStatus(StrEnum):
    PENDING = auto()
    IN_PROGRESS = auto()
    DONE = auto()


class TodoPriority(StrEnum):
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()


class MenuButtons(StrEnum):
    MY_TASKS = '🗂️ My tasks'
    CREATE_TASK = '✏️ Create task'
    STATS = "📊 Statistics"

