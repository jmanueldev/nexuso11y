import time
import json
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, Request, Response
from pydantic import BaseModel, Field

app = FastAPI(title="NexusTelemetry Universal MELT Engine", version="4.0.0")

# --- 1. MELT Pydantic Schemas ---

class MetricPayload(BaseModel):
    metric_name: str
    value: float
    unit: str
    labels: Dict[str, str] = Field(default_factory=dict)

class EventPayload(BaseModel):
    event_id: str
    severity: str  # INFO, WARN, CRITICAL
    message: str
    source_component: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class LogPayload(BaseModel):
    level: str     # DEBUG, INFO, ERROR
    message: str
    service_name: str
    stack_trace: Optional[str] = None

class TracePayload(BaseModel):
    trace_id: str
    span_id: str
    parent_span_id: Optional[str] = None
    operation_name: str
    duration_ms: float
    attributes: Dict[str, Any] = Field(default_factory=dict)

class UnifiedMELTEnvelope(BaseModel):
    infrastructure_type: str  # kubernetes, virtualized, bare_metal
    timestamp: float = Field(default_factory=time.time)
    correlation_id: str
    metrics: List[MetricPayload] = Field(default_factory=list)
    events: List[EventPayload] = Field(default_factory=list)
    logs: List[LogPayload] = Field(default_factory=list)
    traces: List[TracePayload] = Field(default_factory=list)


# --- 2. Ingestion & Correlation Endpoint ---

@app.post("/v1/melt/ingest")
async def ingest_melt_stream(envelope: UnifiedMELTEnvelope) -> Response:
    start_time = time.time()
    
    # Track counts for each pillar processed in this batch
    metrics_count = len(envelope.metrics)
    events_count = len(envelope.events)
    logs_count = len(envelope.logs)
    traces_count = len(envelope.traces)
    
    # Cross-Domain Correlation Logic:
    # If an Event is critical AND a Trace contains an error status, flag a unified incident.
    incident_triggered = False
    for event in envelope.events:
        if event.severity == "CRITICAL":
            for trace in envelope.traces:
                if trace.attributes.get("http.status_code", 200) >= 500:
                    incident_triggered = True
                    break

    processing_latency_ms = (time.time() - start_time) * 1000

    return Response(
        content=json.dumps({
            "status": "indexed_melt_stream",
            "correlation_id": envelope.correlation_id,
            "infrastructure": envelope.infrastructure_type,
            "pillars_processed": {
                "metrics": metrics_count,
                "events": events_count,
                "logs": logs_count,
                "traces": traces_count
            },
            "unified_incident_flag": incident_triggered,
            "processing_latency_ms": round(processing_latency_ms, 4)
        }),
        media_type="application/json"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=4318)