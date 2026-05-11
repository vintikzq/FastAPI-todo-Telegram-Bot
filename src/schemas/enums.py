from enum import IntEnum, StrEnum, auto


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
    STATS = '📊 Statistics'


class ActionsNav(IntEnum):
    LIST = 1
    VIEW = 2
    PAGE_UP = 3
    PAGE_DOWN = 4
    SKIP = 5


class ActionsView(IntEnum):
    DELETE = 1
    UPDATE = 2


class ActionsUpdate(IntEnum):
    NAME = 1
    DESCRIPTION = 2
    PRIORITY = 3
    DEADLINE = 4
