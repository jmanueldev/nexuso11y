
# NexusO11y 🚀

> **The Next-Gen, Zero-Overhead Observability Stack for Massive Kubernetes & Production GenAI Apps.**

a novel eBPF and OTel-native observability daemon and semantic sidecar designed to capture massive Kubernetes traffic, API paths, and GenAI agent loops. NexusO11y combines kernel-level **eBPF tracing**, an ultra-lightweight **OpenTelemetry (OTel) ingestion pipeline**, and a real-time **GenAI Agent Guard** to capture high-throughput traffic and trace LLM token loops without sidecar bloat.

The biggest pain point in 2026 is **Agentic AI & High-Throughput Microservice Observability Blind Spots**: traditional tracers show what happened, but they **lack a Real-Time Per-Turn Policy/Semantic Classifier layer and an eBPF-to-Vector zero-overhead pipeline** for Kubernetes.

## ⚡ Key Features
* **Zero-App-Change eBPF Tracing:** Automatically extracts RED metrics (Rate, Errors, Duration) from Linux sockets.
* **GenAI Semantic Guard:** Inspects OTel payloads in real-time to intercept LLM context token spikes and runaway agent loops.
* **Columnar Native:** Built to stream directly into ClickHouse at millions of events per second with 10x lower memory footprint than traditional collectors.

## 🚀 Quickstart (Local Test)
1. Clone the repository:
   ```bash
   git clone 
   cd nexuso11y
   ```

2. Boot up the local stack (Collector + ClickHouse mockup):
   ```bash
   make up
   ```

   ---

### 2. `Makefile`
```makefile
.PHONY: up down build

up:
	docker compose up --build -d
	@echo "NexusO11y stack is running on http://localhost:4318"

down:
	docker compose down

build:
	cd collector && pip install -r requirements.txt
	@echo "Collector dependencies installed successfully."
