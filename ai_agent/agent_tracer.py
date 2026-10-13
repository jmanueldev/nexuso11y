import time
import uuid
from typing import Dict, Any, List
from pydantic import BaseModel

class AgentSpan(BaseModel):
    trace_id: str
    span_id: str
    parent_span_id: str | None = None
    operation_name: str  # e.g., "gen_ai.agent.run", "gen_ai.tool.execute"
    model_name: str
    input_tokens: int
    output_tokens: int
    tool_name: str | None = None
    latency_ms: float
    evaluation_score: float | None = None  # Online evaluation metrics

class AgentObservabilityEngine:
    def __init__(self):
        self.active_sessions: Dict[str, List[AgentSpan]] = {}

    def track_agent_turn(self, session_id: str, operation: str, prompt: str, response: str, tool_used: str = None) -> AgentSpan:
        start_time = time.time()
        
        # Simulating execution & token calculation
        input_tokens = len(prompt.split()) * 2
        output_tokens = len(response.split()) * 2
        
        latency = (time.time() - start_time) * 1000 + 45.0 # Mocking inference time
        
        span = AgentSpan(
            trace_id=str(uuid.uuid4()),
            span_id=str(uuid.uuid4())[:8],
            operation_name=operation,
            model_name="claude-3-5-sonnet",
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            tool_name=tool_used,
            latency_ms=round(latency, 2),
            evaluation_score=0.98 if "error" not in response.lower() else 0.35 # Automated online eval score
        )
        
        if session_id not in self.active_sessions:
            self.active_sessions[session_id] = []
        self.active_sessions[session_id].append(span)
        
        return span

if __name__ == "__main__":
    engine = AgentObservabilityEngine()
    # Test multi-turn conversational trace
    span1 = engine.track_agent_turn("session_99", "gen_ai.agent.run", "Fetch Kubernetes cluster error logs", "Found OOMKilled on pod-alpha", "kubectl_logs")
    print(f"AI Agent Multi-Turn Trace Recorded: {span1.model_dump_json(indent=2)}")