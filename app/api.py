import asyncio
import json
import threading

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.graph_workflow import (
    build_graph,
    generate_final_report,
    run_task,
)

app = FastAPI(
    title="Multi-Agent Task Automation API",
    description="API for the LangGraph multi-agent workflow",
    version="1.1.0",
)

active_tasks = {}
active_tasks_lock = threading.Lock()


@app.post("/api/tasks/{task_id}/cancel")
def cancel_task(task_id: str):
    with active_tasks_lock:
        cancel_event = active_tasks.get(task_id)

    if cancel_event is None:
        return {"status": "not_running", "message": "Task is no longer running."}

    cancel_event.set()
    return {"status": "cancellation_requested"}


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)



class TaskRequest(BaseModel):
    task: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="The task to execute",
    )


def sse_event(data: dict) -> str:
    """Format one Server-Sent Event as JSON."""
    return f"data: {json.dumps(data)}\n\n"


@app.get("/")
def home():
    return {"message": "Multi-Agent Task Automation API is running"}


@app.get("/api/health")
def health():
    return {"status": "healthy"}


@app.post("/api/tasks")
def execute_task(request: TaskRequest):
    """Keep the original non-streaming endpoint working."""
    task = request.task.strip()

    if not task:
        raise HTTPException(
            status_code=400,
            detail="Task cannot be empty",
        )

    try:
        return run_task(task)
    except Exception as exc:
        print(f"Task execution failed: {exc}")
        raise HTTPException(
            status_code=500,
            detail="Task execution failed. Check the backend terminal.",
        ) from exc



@app.post("/api/tasks/stream")
def execute_task_stream(
    request: Request,
    task_request: TaskRequest,
):
    """Execute a workflow and support cancellation between steps."""
    task = task_request.task.strip()

    if not task:
        raise HTTPException(
            status_code=400,
            detail="Task cannot be empty",
        )

    task_id = request.headers.get("X-Task-ID", "").strip()

    if not task_id:
        raise HTTPException(
            status_code=400,
            detail="Missing X-Task-ID header",
        )

    cancel_event = threading.Event()

    with active_tasks_lock:
        if task_id in active_tasks:
            raise HTTPException(
                status_code=409,
                detail="This task ID is already in use",
            )
        active_tasks[task_id] = cancel_event

    def event_generator():
        try:
            workflow = build_graph()

            state = {
                "task": task,
                "selected_agents": [],
                "results": [],
                "research_sources": [],
                "final_report": "",
            }

            yield sse_event({
                "type": "workflow",
                "status": "running",
                "message": "Starting the AI workflow...",
            })

            completed = set()
            started = set()

            for update in workflow.stream(
                state,
                stream_mode="updates",
            ):
                if cancel_event.is_set():
                    yield sse_event({
                        "type": "cancelled",
                        "message": "Task cancelled.",
                    })
                    return

                for node_name, node_output in update.items():
                    state.update(node_output)

                    if node_name == "orchestrator":
                        agents = state.get("selected_agents", [])

                        yield sse_event({
                            "type": "agents_selected",
                            "agents": agents,
                            "message": "The orchestrator selected the agents.",
                        })

                        if agents:
                            first_agent = agents[0]
                            started.add(first_agent)

                            yield sse_event({
                                "type": "agent_status",
                                "agent": first_agent,
                                "status": "running",
                            })

                    elif node_name in {
                        "research",
                        "planning",
                        "analysis",
                        "verification",
                    }:
                        completed.add(node_name)

                        yield sse_event({
                            "type": "agent_status",
                            "agent": node_name,
                            "status": "completed",
                        })

                        next_agent = next(
                            (
                                agent
                                for agent in state["selected_agents"]
                                if agent not in completed
                            ),
                            None,
                        )

                        if next_agent and next_agent not in started:
                            started.add(next_agent)

                            yield sse_event({
                                "type": "agent_status",
                                "agent": next_agent,
                                "status": "running",
                            })

            if cancel_event.is_set():
                yield sse_event({
                    "type": "cancelled",
                    "message": "Task cancelled.",
                })
                return

            yield sse_event({
                "type": "report",
                "status": "running",
                "message": "Preparing your final report...",
            })

            final_report = generate_final_report(
                task=task,
                results=state["results"],
                sources=state["research_sources"],
            )

            if cancel_event.is_set():
                yield sse_event({
                    "type": "cancelled",
                    "message": "Task cancelled.",
                })
                return

            response = {
                "task": task,
                "selected_agents": state["selected_agents"],
                "results": state["results"],
                "research_sources": state["research_sources"],
                "final_report": final_report,
            }

            yield sse_event({
                "type": "completed",
                "result": response,
            })

        
        
        except Exception as exc:
            import traceback

            print(
                f"Streaming task failed: {type(exc).__name__}: {exc}",
                flush=True,
            )
            traceback.print_exc()

            yield sse_event({
                "type": "error",
                "message": (
                    "The workflow encountered an error. "
                    "Please try again. If the problem continues, "
                    "check the backend terminal."
                ),
            })



        finally:
            with active_tasks_lock:
                active_tasks.pop(task_id, None)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )

