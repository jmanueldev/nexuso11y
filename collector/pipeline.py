import time
import json
from fastapi import FastAPI, Request, Response

app = FastAPI(title="NexusO11y Edge Node", version="1.0.0")

@app.post("/v1/traces")
async def ingest_traces(request: Request) -> Response:
    start_time = time.time()
    body = await request.json()
    
    spans = body.get("resourceSpans", [])
    processed_spans = []
    anomaly_detected = False

    for resource_span in spans:
        for scope_span in resource_span.get("scopeSpans", []):
            for span in scope_span.get("spans", []):
                attributes = {attr["key"]: attr["value"] for attr in span.get("attributes", [])}
                
                # Futuristic GenAI Agent Guard Logic (Detecting Token Saturation)
                if "gen_ai.prompt" in attributes:
                    token_count = int(attributes.get("gen_ai.usage.input_tokens", {}).get("intValue", 0))
                    if token_count > 4096:
                        anomaly_detected = True
                        span["status"] = {"code": 2, "message": "Context window saturation warning"}

                processed_spans.append(span)

    duration_ms = (time.time() - start_time) * 1000
    return Response(
        content=json.dumps({
            "status": "indexed", 
            "processed_count": len(processed_spans), 
            "latency_ms": round(duration_ms, 2), 
            "anomaly_flag": anomaly_detected
        }),
        media_type="application/json"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=4318)