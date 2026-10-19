import { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import "./App.css";

const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL || "{API_BASE_URL}"
).replace(/\/$/, "");

function App() {
  const [task, setTask] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [agentStatuses, setAgentStatuses] = useState({});
  const [workflowMessage, setWorkflowMessage] = useState("");
  const abortControllerRef = useRef(null);
  const [taskHistory, setTaskHistory] = useState(() => {
    try {
      return JSON.parse(
        localStorage.getItem("agentflow_task_history") || "[]"
      );
    } catch {
      return [];
    }
  });
  useEffect(() => {
    localStorage.setItem(
      "agentflow_task_history",
      JSON.stringify(taskHistory)
    );
  }, [taskHistory]);
  
async function handleSubmit(event) {
  event.preventDefault();

  if (!task.trim()) return;

  setLoading(true);
  setResult(null);
  setError("");
  setWorkflowMessage("Starting your AI workflow...");

  const allAgents = ["research", "planning", "analysis", "verification"];

  setAgentStatuses(
    Object.fromEntries(allAgents.map((agent) => [agent, "waiting"]))
  );

  try {
    
    const taskId = crypto.randomUUID();
    const controller = new AbortController();

    abortControllerRef.current = { controller, taskId };

    const response = await fetch(
      `${API_BASE_URL}/api/tasks/stream`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Task-ID": taskId,
        },
        body: JSON.stringify({ task: task.trim() }),
        signal: controller.signal,
      }
    );
    
    if (!response.ok) {
      let message = `Request failed (${response.status}).`;

      try {
        const data = await response.json();
        message = data.detail || data.message || message;
      } catch {
        // Keep the default message if the response isn't JSON.
      }

      throw new Error(message);
    }

    if (!response.body) {
      throw new Error("The server did not provide a response stream.");
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    let completed = false;

    while (true) {
      const { value, done } = await reader.read();

      if (done) break;

      buffer += decoder.decode(value, { stream: true });

      const events = buffer.split(/\r?\n\r?\n/);
      buffer = events.pop() || "";

      for (const eventText of events) {
        const dataLine = eventText
          .split(/\r?\n/)
          .find((line) => line.startsWith("data:"));

        if (!dataLine) continue;

        const jsonText = dataLine.slice(5).trim();
        if (!jsonText) continue;

        let event;

        try {
          event = JSON.parse(jsonText);
        } catch {
          console.error("Could not parse streaming event:", jsonText);
          continue;
        }

        if (event.type === "workflow") {
          setWorkflowMessage(event.message || "Workflow started.");
        }

        if (event.type === "agents_selected") {
          setAgentStatuses(
            Object.fromEntries(
              allAgents.map((agent) => [
                agent,
                event.agents.includes(agent) ? "waiting" : "skipped",
              ])
            )
          );
          setWorkflowMessage("Your AI team has been selected.");
        }

        if (event.type === "agent_status") {
          setAgentStatuses((previous) => ({
            ...previous,
            [event.agent]: event.status,
          }));

          setWorkflowMessage(
            `${event.agent} agent: ${event.status}`
          );
        }

        if (event.type === "report") {
          setWorkflowMessage(event.message || "Preparing final report...");
        }

        
        if (event.type === "cancelled") {
          setWorkflowMessage(event.message || "Task cancelled.");
          setError("");
          completed = true;
        }


        if (event.type === "completed") {
          const completedResult = event.result;

          setResult(completedResult);
          setWorkflowMessage("Workflow completed successfully.");

          setTaskHistory((previous) => [
            {
              id: `${Date.now()}-${Math.random()}`,
              task: completedResult.task,
              result: completedResult,
              createdAt: new Date().toISOString(),
            },
            ...previous,
          ].slice(0, 20));

          completed = true;
        }

        if (event.type === "error") {
          throw new Error(event.message || "The workflow failed.");
        }
      }

      if (completed) break;
    }

    if (!completed) {
      throw new Error("The stream ended before the final report arrived.");
    }
  }catch (err) {
    if (err.name === "AbortError") {
      setWorkflowMessage("Task cancelled.");
      setError("");
    } else if (err instanceof TypeError) {
      setError(
        `Could not connect to the backend. Check that the server is running at ${API_BASE_URL}.`
      );
    } else {
      setError(
        err.message || "Something went wrong while executing the task."
      );
    }
  } finally {
    abortControllerRef.current = null;
    setLoading(false);
  }

}
function openHistoryItem(item) {
  setTask(item.task);
  setResult(item.result);
  setError("");
  setWorkflowMessage("Viewing a previous task.");
  setAgentStatuses({});
}


  const agents = [
    { name: "Research Agent", icon: "⌕", description: "Collects relevant information" },
    { name: "Planning Agent", icon: "◇", description: "Organizes the task workflow" },
    { name: "Analysis Agent", icon: "⌘", description: "Analyzes findings and results" },
    { name: "Verification Agent", icon: "✓", description: "Reviews the final output" },
  ];

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">M</div>
          <div>
            <h2>AgentFlow</h2>
            <span>Multi-Agent AI Platform</span>
          </div>
        </div>


        <button
          className="nav-item"
          onClick={() => {
            setTask("");
            setResult(null);
            setError("");
            setWorkflowMessage("");
            setAgentStatuses({});
          }}
        >
          ◷ &nbsp; New task
        </button>

        
        <div className="history-section">
          <div className="history-heading">
            <p className="nav-label">RECENT TASKS</p>

            {taskHistory.length > 0 && (
              <button
                className="clear-history-button"
                onClick={() => {
                  const confirmed = window.confirm(
                    "Are you sure you want to delete all task history?"
                  );

                  if (confirmed) {
                    setTaskHistory([]);
                  }
                }}
              >
                Clear
              </button>
            )}
          </div>
          {taskHistory.length === 0 ? (
            <p className="history-empty">Your completed tasks will appear here.</p>
          ) : (
            <div className="history-list">              
              {taskHistory.map((item) => (
                <div key={item.id} className="history-item">
                  <button
                    className="history-item-open"
                    title={item.task}
                    onClick={() => openHistoryItem(item)}
                  >
                    <span className="history-item-icon">◷</span>
                    <span className="history-item-text">{item.task}</span>
                  </button>

                  <button
                    className="history-item-delete"
                    title="Delete task"
                    aria-label={`Delete task: ${item.task}`}
                    onClick={() => {
                      setTaskHistory((previous) =>
                        previous.filter((historyItem) => historyItem.id !== item.id)
                      );
                    }}
                  >
                    ×
                  </button>
                </div>
              ))}

            </div>
          )}
        </div>


        <div className="sidebar-bottom">
          <div className="status-dot" />
          <div>
            <strong>Backend API</strong>
            <span>localhost:8000</span>
          </div>
          <span className="online">Online*</span>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div>
            <p className="eyebrow">AI WORKSPACE / OVERVIEW</p>
            <h1>Task Automation Dashboard</h1>
          </div>
          <div className="profile">
            <div className="profile-avatar">AI</div>
            <div>
              <strong>AI Workspace</strong>
              <span>Personal environment</span>
            </div>
          </div>
        </header>

        <section className="welcome">
          <div>
            <span className="pill">✦ MULTI-AGENT SYSTEM</span>
            <h2>Turn complex tasks into <span>finished work.</span></h2>
            <p>Describe your objective. Let your AI workflow research, reason, and deliver a structured report.</p>
          </div>
          <div className="hero-orbit">
            <div className="orbit orbit-one" />
            <div className="orbit orbit-two" />
            <div className="orbit-core">✦</div>
          </div>
        </section>

        <section className="stats-grid">
          <div className="stat-card">
            <span>Workflow engine</span>
            <strong>LangGraph</strong>
            <small>Stateful agent orchestration</small>
          </div>
          <div className="stat-card">
            <span>Language model</span>
            <strong>Groq LLM</strong>
            <small>AI-powered task processing</small>
          </div>
          <div className="stat-card">
            <span>Research layer</span>
            <strong>Tavily Search</strong>
            <small>Web research integration</small>
          </div>
        </section>

        <section className="workspace-grid">
          <div className="panel task-panel">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">GET STARTED</p>
                <h3>Create a new task</h3>
              </div>
              <span className="step-badge">01</span>
            </div>

            <form onSubmit={handleSubmit}>
              <label htmlFor="task">What would you like your agents to do?</label>
              <textarea
                id="task"
                value={task}
                onChange={(event) => setTask(event.target.value)}
                placeholder="Example: Research the latest trends in AI agents and prepare a report with reliable sources..."
                maxLength={2000}
                rows={5}
                disabled={loading}
              />
              <div className="input-footer">
                <span>{task.length}/2000 characters</span>

                <div className="task-actions">
                  {loading && (
                    <button
                      type="button"
                      className="cancel-task-button"                      
                      onClick={async () => {
                        const activeTask = abortControllerRef.current;
                        if (!activeTask) return;

                        try {
                          const response = await fetch(
                            `${API_BASE_URL}/api/tasks/${activeTask.taskId}/cancel`,
                            {
                              method: "POST",
                            }
                          );

                          if (!response.ok) {
                            console.error(
                              "Cancellation request failed:",
                              response.status,
                              await response.text()
                            );
                          } else {
                            setWorkflowMessage("Cancellation requested...");
                          }
                        } catch (err) {
                          console.error("Could not request task cancellation:", err);
                          setError("Could not contact the backend to cancel the task.");
                        }

                        activeTask.controller.abort();
                      }}
                    >
                      Cancel task
                    </button>
                  )}

                  <button
                    type="submit"
                    className="run-button"
                    disabled={loading || !task.trim()}
                  >
                    {loading ? "Running workflow..." : "Run AI workflow →"}
                  </button>
                </div>
              </div>
            </form>

            <div className="suggestions">
              <span>TRY AN EXAMPLE</span>
              <button onClick={() => setTask("Research the top AI agent frameworks in 2026 and compare their features, use cases, and limitations.")}>
                AI framework comparison
              </button>
              <button onClick={() => setTask("Create a 30-day learning roadmap for a computer science student preparing for software engineering internships.")}>
                Internship roadmap
              </button>
            </div>

            {loading && (
              <div className="loading-box">
                <div className="spinner" />
                <div>
                  <strong>Your agents are working</strong>
                  <p>The workflow is processing your task. This can take a little time.</p>
                </div>
              </div>
            )}

            {error && <div className="error-box">{error}</div>}
          </div>

          <div className="panel agents-panel">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">YOUR AI TEAM</p>
                <h3>Agent capabilities</h3>
              </div>
              <span className="team-count">04 AGENTS</span>
            </div>

            <div className="agent-list">
              {agents.map((agent, index) => (
                <div className="agent-row" key={agent.name}>
                  <div className={`agent-icon agent-${index}`}>{agent.icon}</div>
                  <div className="agent-info">
                    <strong>{agent.name}</strong>
                    <span>{agent.description}</span>
                  </div>
                  <span className="agent-indicator">●</span>
                </div>
              ))}
            </div>

            <div className="workflow-note">
              <span>✦</span>
              <div>
                <strong>Coordinated intelligence</strong>
                <p>The backend determines which agents and tools are used for each task.</p>
              </div>
            </div>
          </div>
        </section>

        {result && (
          <section className="panel results-panel">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">WORKFLOW COMPLETED</p>
                <h3>Task results</h3>
              </div>
              <button className="secondary-button" onClick={() => {
                navigator.clipboard?.writeText(result.final_report || "");
              }}>
                Copy final report
              </button>
            </div>

            <div className="result-task">
              <strong>Original task</strong>
              <p>{result.task}</p>
            </div>

            <div className="selected-agents">
              <strong>Selected agents</strong>
              <div className="agent-chips">
                {(result.selected_agents || []).map((agent, index) => (
                  <span key={`${agent}-${index}`}>{agent}</span>
                ))}
              </div>
            </div>

            <div className="final-report">
              <h4>Final report</h4>
              <pre>{result.final_report || "No final report was returned."}</pre>
            </div>

            <div className="result-details">
              <h4>Agent outputs</h4>
              {(result.results || []).map((item, index) => (
                <div className="output-card" key={`${item.agent || "agent"}-${index}`}>
                  <strong>{item.agent || `Agent ${index + 1}`}</strong>
                  <pre>{typeof item.output === "string" ? item.output : JSON.stringify(item.output, null, 2)}</pre>
                </div>
              ))}
            </div>

            {result.research_sources?.length > 0 && (
              <div className="sources-section">
                <h4>Research sources</h4>
                {result.research_sources.map((source, index) => {
                  const url = typeof source === "string" ? source : source.url;
                  const title = typeof source === "string" ? source : source.title || source.url;
                  return (
                    <div key={`${url || title}-${index}`}>
                      {url ? (
                        <a href={url} target="_blank" rel="noreferrer">{title || url}</a>
                      ) : (
                        <span>{JSON.stringify(source)}</span>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </section>
        )}

        <footer>
          <span>AgentFlow · Multi-Agent Task Automation</span>
          <span>React · FastAPI · LangGraph</span>
        </footer>
      </main>
    </div>
  );
}

export default App;

