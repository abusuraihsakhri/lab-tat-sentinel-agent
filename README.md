# Lab Tat Sentinel Agent

> **Domain:** Clinical Decision Support & Biomedical Computing  
> **Reference Guidelines & Standards:** `Standard Clinical Formulations & ISO/IEC Quality Frameworks`

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## 📖 What It Does

**Lab Tat Sentinel Agent** is an advanced analytical and computational platform implementing LIS Specimen Turnaround Time & Bottleneck Forecaster.

---

## ⚙️ Key Capabilities & Algorithmic Modules

### 🔬 Core Algorithmic & Evaluation Engines

- **`Severity`** — dedicated module for severity evaluation and state verification.
- **`DomainKnowledgeRegistry`**: Enterprise domain rules, guideline matrices, and evidence benchmarks.
- **`AgentAlert`** — dedicated module for agent alert evaluation and state verification.
- **`QueueBottleneckForecasterAgent`**: Specialized Sub-Agent 1 for lab-tat-sentinel-agent
- **`SLABreachPredictorAgent`**: Specialized Sub-Agent 2 for lab-tat-sentinel-agent
- **`AnalyzerWorkloadBalancerAgent`**: Specialized Sub-Agent 3 for lab-tat-sentinel-agent

---

## 💻 CLI Quickstart & Usage

### 1. Single Task Evaluation (Audit)
```bash
python cli.py audit --task-id TASK-001 --target SPECIMEN-01 --primary 28.5 --secondary 14.2 --critical --status DISCORDANT
```

### 2. Batch Process CSV Records
```bash
python cli.py batch -i sample.csv -o results.csv
```

### 3. Supervisor Chat Query
```bash
python cli.py chat "What is the current system status?"
```

### 4. Verify Audit Trail Integrity
```bash
python cli.py verify-audit
```

### 5. Launch FastAPI REST Server
```bash
python cli.py serve --host 127.0.0.1 --port 8000
```

### Audit Command Parameters

| Parameter | Type | Default | Description |
|:----------|:-----|:--------|:------------|
| `--task-id` | str | `TASK-2026-001` | Unique task / case identifier |
| `--target` | str | `KEY-TARGET-01` | Target specimen or entity identifier |
| `--primary` | float | `28.5` | Primary metric measurement |
| `--secondary` | float | `14.2` | Secondary metric measurement |
| `--critical` | flag | `False` | Trigger emergency escalation |
| `--status` | str | `DISCORDANT` | Status descriptor (e.g., NOMINAL, DISCORDANT, SUSPICIOUS) |

### Batch CSV Input Schema

| Field | Description | Requirement |
|:------|:------------|:------------|
| `task_id` | Unique task identifier | Optional (defaults to row index) |
| `target_identifier` | Target specimen/entity | Optional |
| `primary_metric` | Primary measurement value | Optional (default: 15.0) |
| `secondary_metric` | Secondary measurement value | Optional (default: 5.0) |
| `is_critical_flag` | Emergency escalation flag | Optional (default: false) |
| `status_descriptor` | Status code or phenotype | Optional (default: NOMINAL) |

---

## 🛡️ Security & Enterprise Architecture

* **Zero-PHI Outbound Interceptor:** Active AST and regex inspection blocking SSNs, MRNs, phone numbers, and patient identifiers.
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation and state transition.
* **Air-Gapped LLM Reasoning Adapter:** Agnostic integration for local Ollama instances (`llama3`, `mistral`), Claude 3.5 Sonnet, GPT-4o, and deterministic test mocks.
* **Active Learning Bayesian Calibration:** Dynamic tracker updating worker reliability weights and monitoring Brier calibration drift.
* **FastAPI & Prometheus Telemetry:** Exposes OpenAPI 3.1 REST endpoints and operational Prometheus metrics (`/metrics`).

---

## 🧪 Testing & Verification

Run the automated test suite:

```bash
pytest -v
```

Execute high-throughput batch simulation benchmarks:

```bash
python simulator.py --tasks 100 --concurrency 1
```

The simulator generates random task payloads across all urgency tiers, injects adversarial PHI test cases, and reports HMAC-SHA256 audit integrity verification.

---

## 🐳 Container Deployment

```bash
docker build -t lab-tat-sentinel-agent .
docker run -p 8000:8000 lab-tat-sentinel-agent
```
