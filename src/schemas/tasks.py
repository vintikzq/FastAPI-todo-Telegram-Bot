from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

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
        return self.due_date.strftime("%d.%m")

    @property
    def emoji_status(self) -> str:
        if self.status == TodoStatus.PENDING:
            return "🔜"
        if self.status == TodoStatus.IN_PROGRESS:
            return "⏳"
        return "✅"

    @property
    def emoji_priority(self) -> str:
        if self.priority == TodoPriority.LOW:
            return "⬇️"
        if self.priority == TodoPriority.MEDIUM:
            return "⬆️"
        return "⏫"

    @property
    def not_none_description(self) -> str:
        return self.description if self.description else ""

    def format_to_html(self) -> str:
        date = self.friendly_date
        priority = self.emoji_priority
        status = self.emoji_status
        description = self.not_none_description
        return f"{priority} <b>{self.name}</b> {date} {status}\n<i>{description}</i>"

    def friendly_format_for_buttons(self) -> str:
        status = self.emoji_status
        return f"{status} {self.name}"


class TaskRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    name: str
    priority: TodoPriority
    description: str | None
    due_date: str | None


class TaskUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=127)
    status: TodoStatus | None = None
    priority: TodoPriority | None = None
    due_date: str | None = None
    description: str | None = Field(default=None, max_length=1024)


class TaskStatsResponse(BaseModel):
    completed_count: int
    total_tasks: int

    @property
    def emoji_completed_count(self) -> str:
        return f"{self.completed_count} ✅"

    @property
    def emoji_total_tasks_count(self) -> str:
        return f"{self.total_tasks} 📋"

    @property
    def emoji_tasks_at_work(self) -> str:
        return f"{self.total_tasks - self.completed_count} 💻"

    def format_to_pretty_stats(self) -> str:
        done = self.emoji_completed_count
        total = self.emoji_total_tasks_count
        at_work = self.emoji_tasks_at_work

        return f"<b>Your statistics:</b>\n\nTotal tasks: {total}\nDone tasks: {done}\nTasks at work: {at_work}"
