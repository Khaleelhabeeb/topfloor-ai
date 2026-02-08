from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session as DBSession
from typing import List

from app.api.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.task import TaskStatus as TaskStatusEnum
from app.services.task_service import TaskService
from app.agents import AgentRegistry
from app.agents.registry import AgentType


router = APIRouter(prefix="/tools", tags=["Tools"])


class PromptBuilderRequest(BaseModel):
	agent_type: str = Field(..., description="Agent role/type")


class PromptBuilderResponse(BaseModel):
	text: str


@router.post("/prompt-builder", response_model=PromptBuilderResponse)
async def build_prompt(
	payload: PromptBuilderRequest,
	db: DBSession = Depends(get_db),
	current_user: User = Depends(get_current_user)
):
	"""
	Return a prompt containing the agent system prompt and current tasks.
	"""
	if not AgentRegistry.validate_agent_type(payload.agent_type):
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail=f"Invalid agent type: {payload.agent_type}"
		)

	agent_def = AgentRegistry.get_agent(AgentType(payload.agent_type))

	task_service = TaskService(db)
	tasks, _ = task_service.get_agent_tasks(
		user_id=current_user.id,
		agent_type=payload.agent_type,
		sort_by="updated_at",
		sort_order="desc",
		limit=20
	)

	active_statuses = {
		TaskStatusEnum.PENDING,
		TaskStatusEnum.QUEUED,
		TaskStatusEnum.IN_PROGRESS
	}
	current_tasks = [task for task in tasks if task.status in active_statuses]

	task_lines: List[str] = []
	for task in current_tasks:
		task_lines.append(
			f"- {task.title} ({task.status.value}, priority {task.priority.value})"
		)

	tasks_section = "None" if not task_lines else "\n".join(task_lines)

	voice_prefix = (
		"VOICE MODE:\n"
		"- Speak naturally and concisely; keep responses to 1-3 sentences.\n"
		"- Avoid markdown, code blocks, and long lists unless asked.\n"
		"- If something is ambiguous, ask one short clarifying question.\n"
		"- Read numbers naturally; avoid symbols or abbreviations without context.\n"
		"- If you plan to create a task, say so clearly before you proceed.\n\n"
	)

	text = (
		voice_prefix
		+ "SYSTEM PROMPT:\n"
		f"{agent_def.system_prompt}\n\n"
		"CURRENT TASKS:\n"
		f"{tasks_section}"
	)

	return PromptBuilderResponse(text=text)
