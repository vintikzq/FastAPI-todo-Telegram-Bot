from datetime import datetime

from pydantic import BaseModel

from src.schemas.enums import TodoPriority, TodoStatus


class TaskResponse(BaseModel):
    id: int
    name: str
    status: TodoStatus
    priority: TodoPriority
    description: str | None
    due_date: datetime | None
    created_at: datetime

    @property
    def friendly_date(self) -> str:
        if not self.due_date:
            return ""
        return self.due_date.strftime("%d.%m %H:%M")

    @property
    def emoji_status(self) -> str:
        if self.status == TodoStatus.PENDING:
            return '🔜'
        if self.status == TodoStatus.IN_PROGRESS:
            return '⏳'
        return '✅'

    @property
    def emoji_priority(self) -> str:
        if self.priority == TodoPriority.LOW:
            return '⬇️'
        if self.priority == TodoPriority.MEDIUM:
            return '⬆️'
        return '⏫'

    @property
    def not_none_description(self) -> str:
        return self.description if self.description else ""

    def format_to_html(self) -> str:
        date = self.friendly_date
        priority = self.emoji_priority
        status = self.emoji_status
        description = self.not_none_description
        return f"{priority} <b>{self.name}</b> {date} {status}\n<i>{description}</i>"
