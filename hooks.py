from __future__ import annotations

from typing import Any

from agents import RunHooks
from chatkit.agents import AgentContext
from chatkit.types import CustomTask, SearchTask


class ChatKitWorkflowHooks(RunHooks):
    """
    Converts OpenAI Agents SDK lifecycle events into
    user-friendly ChatKit workflow tasks.
    """

    def __init__(self) -> None:
        super().__init__()

        self._agent_tasks: dict[int, tuple[Any, int]] = {}

        self._tool_tasks: dict[str, tuple[Any, int]] = {}

    async def on_agent_start(
        self,
        context: Any,
        agent: Any,
    ) -> None:

        print(f"[HOOK] Agent started: {agent.name}")

        chatkit_context = self._get_chatkit_context(context)

        if chatkit_context is None:
            print("[HOOK] ChatKit context not found")
            return

        title = self._friendly_agent_name(agent.name)

        if title is None:
            return

        task = CustomTask(
            title=title,
            icon="agent",
            status_indicator="loading",
        )

        await chatkit_context.add_workflow_task(task)

        task_index = self._get_latest_task_index(chatkit_context)

        self._agent_tasks[id(agent)] = (
            task,
            task_index,
        )

    async def on_agent_end(
        self,
        context: Any,
        agent: Any,
        output: Any,
    ) -> None:

        print(f"[HOOK] Agent finished: {agent.name}")

        chatkit_context = self._get_chatkit_context(context)

        if chatkit_context is None:
            print("[HOOK] ChatKit context not found")
            return

        task_info = self._agent_tasks.get(id(agent))

        if task_info is None:
            return

        task, task_index = task_info

        if chatkit_context.workflow_item is None:
            return

        task.status_indicator = "complete"

        await chatkit_context.update_workflow_task(
            task,
            task_index,
        )

    async def on_tool_start(
        self,
        context: Any,
        agent: Any,
        tool: Any,
    ) -> None:

        tool_name = getattr(tool, "name", "")

        print(f"[HOOK] Tool started: {tool_name}")

        chatkit_context = self._get_chatkit_context(context)

        if chatkit_context is None:
            print("[HOOK] ChatKit context not found")
            return

        if tool_name == "web_search":

            query = self._extract_search_query(context)

            task = SearchTask(
                title="Searching the web",
                title_query=query,
                queries=[query],
                status_indicator="loading",
            )

        else:

            task = CustomTask(
                title=self._friendly_tool_name(tool_name),
                icon="search",
                status_indicator="loading",
            )

        await chatkit_context.add_workflow_task(task)

        task_index = self._get_latest_task_index(chatkit_context)

        tool_call_id = str(
            getattr(
                context,
                "tool_call_id",
                tool_name,
            )
        )

        self._tool_tasks[tool_call_id] = (
            task,
            task_index,
        )

    async def on_tool_end(
        self,
        context: Any,
        agent: Any,
        tool: Any,
        result: Any,
    ) -> None:

        tool_name = getattr(tool, "name", "")

        print(f"[HOOK] Tool finished: {tool_name}")

        chatkit_context = self._get_chatkit_context(context)

        if chatkit_context is None:
            print("[HOOK] ChatKit context not found")
            return

        tool_call_id = str(
            getattr(
                context,
                "tool_call_id",
                tool_name,
            )
        )

        task_info = self._tool_tasks.get(tool_call_id)

        if task_info is None:
            return

        task, task_index = task_info

        if chatkit_context.workflow_item is None:
            return

        task.status_indicator = "complete"

        if isinstance(task, SearchTask):

            task.sources = self._extract_sources(result)

        await chatkit_context.update_workflow_task(
            task,
            task_index,
        )

    async def on_handoff(
        self,
        context: Any,
        from_agent: Any,
        to_agent: Any,
    ) -> None:

        print(
            f"[HOOK] Handoff: "
            f"{from_agent.name} -> {to_agent.name}"
        )

        chatkit_context = self._get_chatkit_context(context)

        if chatkit_context is None:
            print("[HOOK] ChatKit context not found")
            return

        title = self._friendly_agent_name(to_agent.name)

        if title is None:
            return

        task = CustomTask(
            title=title,
            icon="agent",
            status_indicator="loading",
        )

        await chatkit_context.add_workflow_task(task)

    @staticmethod
    def _get_chatkit_context(
        context: Any,
    ) -> AgentContext | None:

        """
        Agents SDK lifecycle hooks receive a RunContextWrapper.

        The actual ChatKit AgentContext is normally available as:

            context.context
        """

        inner_context = getattr(
            context,
            "context",
            None,
        )

        if isinstance(inner_context, AgentContext):
            return inner_context

        # Fallback in case the AgentContext is passed directly.
        if isinstance(context, AgentContext):
            return context

        return None

    @staticmethod
    def _get_latest_task_index(
        context: AgentContext,
    ) -> int:

        if context.workflow_item is None:
            raise RuntimeError(
                "Workflow was not initialized after adding a task."
            )

        return (
            len(
                context.workflow_item.workflow.tasks
            )
            - 1
        )

    @staticmethod
    def _friendly_agent_name(
        agent_name: str,
    ) -> str | None:

        name = (
            agent_name
            .lower()
            .replace("_", " ")
            .strip()
        )

        if "triage" in name:
            return "Understanding your question"

        if "planner" in name:
            return "Planning research"

        if "research" in name:
            return "Researching your question"

        if "writer" in name:
            return "Preparing your answer"

        return None

    @staticmethod
    def _friendly_tool_name(
        tool_name: str,
    ) -> str:

        name = (
            tool_name
            .replace("_", " ")
            .strip()
        )

        if not name:
            return "Working on your request"

        return name.capitalize()

    @staticmethod
    def _extract_search_query(
        context: Any,
    ) -> str:

        tool_arguments = getattr(
            context,
            "tool_arguments",
            None,
        )

        if isinstance(tool_arguments, dict):

            for key in (
                "query",
                "search_query",
                "q",
            ):

                value = tool_arguments.get(key)

                if value:
                    return str(value)

        if isinstance(tool_arguments, str):
            return tool_arguments

        return "Searching for relevant information"

    @staticmethod
    def _extract_sources(
        result: Any,
    ) -> list[dict[str, str]]:

        sources: list[dict[str, str]] = []

        if isinstance(result, dict):

            raw_results = (
                result.get("results")
                or result.get("sources")
                or result.get("data")
                or []
            )

        elif isinstance(result, list):

            raw_results = result

        else:

            return sources

        for item in raw_results:

            if not isinstance(item, dict):
                continue

            url = item.get("url")

            if not url:
                continue

            title = item.get(
                "title",
                "Web source",
            )

            sources.append(
                {
                    "type": "url",
                    "title": str(title),
                    "url": str(url),
                }
            )

        return sources