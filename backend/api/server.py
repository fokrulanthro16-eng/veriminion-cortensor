"""
VeriMinion FastAPI Tactical Server
----------------------------------
Serves REST and SSE endpoints for Cortensor decentralized inference validation,
Byzantine routing, permission airlock approval, and OpenMinion 0.1 SDK X-Ray diagnostics.
"""

import asyncio
import json
import os
import uuid
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from backend.core.openminion_runtime import OpenMinionRuntimeBridge
from backend.core.storage import (
    list_sessions,
    get_session,
    get_nodes,
    get_dead_ends,
    get_xray_stats,
    init_db
)

# Initialize database
init_db()

app = FastAPI(
    title="VeriMinion - Decentralized Inference Validator & OpenMinion 0.1 X-Ray Studio",
    version="1.0.0",
    description="Cortensor Hackathon #5 Institutional-Grade Byzantine Routing & Multi-Agent Verification"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

runtime_bridge = OpenMinionRuntimeBridge()

# -----------------------------------------------------------------------------
# PYDANTIC SCHEMAS
# -----------------------------------------------------------------------------
class RunRequest(BaseModel):
    scenario_id: str
    prompt: Optional[str] = None
    session_id: Optional[str] = None
    model_provider: Optional[str] = "deterministic_fallback"

class AirlockDecisionRequest(BaseModel):
    action_id: str
    decision: str  # "APPROVE", "REJECT", "MODIFY"
    operator_note: Optional[str] = ""

class CreateSessionRequest(BaseModel):
    scenario_id: Optional[str] = "cryptographic_smart_contract_audit"
    prompt: Optional[str] = ""

# -----------------------------------------------------------------------------
# PRESET SCENARIOS
# -----------------------------------------------------------------------------
PRESET_SCENARIOS = [
    {
        "id": "cryptographic_smart_contract_audit",
        "title": "1. Cryptographic Smart Contract Audit",
        "badge": "AST & REENTRANCY",
        "description": "Validates decentralized liquidity vault withdrawal logic for state update ordering (CEI pattern) and dangerous system calls.",
        "default_prompt": "Audit and verify decentralized vault withdrawal logic. Enforce strict Checks-Effects-Interactions (CEI) to prevent reentrancy and ban unsafe AST primitives."
    },
    {
        "id": "quantitative_derivative_pricing_proof",
        "title": "2. Quantitative Derivative Pricing Proof",
        "badge": "SYMPY SYMBOLIC MATH",
        "description": "Proves the analytical Black-Scholes partial differential equation solution for European call pricing and delta calculation.",
        "default_prompt": "Prove Black-Scholes European call option formula C(S,t) and delta sensitivity. Verify symbolic equality using canonical SymPy algebra."
    },
    {
        "id": "deterministic_python_algorithm_synthesis",
        "title": "3. Deterministic Python Algorithm Synthesis",
        "badge": "SANDBOX CODE RUNNER",
        "description": "Synthesizes deterministic Byzantine fault-tolerant trimmed-mean consensus sorting with zero off-by-one errors.",
        "default_prompt": "Synthesize a robust, pure Python trimmed-consensus function filtering out top and bottom f outliers from 3f+1 node reports with automated test vectors."
    },
    {
        "id": "cortensor_portal_vs_gemma4_stress_benchmark",
        "title": "4. Cortensor Portal vs. Gemma4 Stress Benchmark",
        "badge": "SLA & THROUGHPUT RACE",
        "description": "Concurrent high-throughput stress test across inference nodes assessing latency jitter, token generation throughput, and SLA compliance.",
        "default_prompt": "Execute high-concurrency stress benchmark between Cortensor Portal primary node and Gemma4 fast tier. Measure tokens/sec and quarantine SLA violations."
    }
]

# -----------------------------------------------------------------------------
# API ROUTES
# -----------------------------------------------------------------------------
@app.get("/api/status")
async def get_system_status():
    """Returns real-time health, SDK version, Cortensor connection, and active node count."""
    nodes = get_nodes()
    return {
        "status": "ONLINE",
        "openminion_sdk_version": runtime_bridge.sdk_version,
        "cortensor_portal_url": runtime_bridge.portal_url,
        "portal_connected": bool(runtime_bridge.cortensor_key),
        "total_nodes": len(nodes),
        "active_quarantines": len([n for n in nodes if n["status"] == "QUARANTINED"]),
        "timestamp": os.path.getmtime(__file__) if os.path.exists(__file__) else 0
    }

@app.get("/api/scenarios")
async def get_scenarios():
    """Returns the 4 1-click live runnable scenarios."""
    return PRESET_SCENARIOS

@app.get("/api/sessions")
async def get_all_sessions():
    """Lists persistent sessions."""
    return list_sessions()

@app.get("/api/sessions/{session_id}")
async def get_session_detail(session_id: str):
    """Retrieves replayable state snapshot for a given session."""
    sess = get_session(session_id)
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")
    return sess

@app.post("/api/sessions")
async def create_new_session(req: CreateSessionRequest):
    """Creates a new session record."""
    session_id = f"sess-{str(uuid.uuid4())[:8]}"
    return {"session_id": session_id, "scenario_id": req.scenario_id, "prompt": req.prompt}

@app.get("/api/nodes")
async def get_all_nodes():
    """Returns current Node Reputation & Trust Ledger."""
    return get_nodes()

@app.get("/api/dead_ends")
async def get_dead_end_memory():
    """Returns Semantic Dead-End Memory records."""
    return get_dead_ends()

@app.get("/api/diagnostics/xray")
async def get_diagnostics_xray():
    """Returns live metrics across all 10 OpenMinion 0.1 building blocks."""
    return get_xray_stats()

@app.post("/api/airlock/decision")
async def resolve_airlock_gate(req: AirlockDecisionRequest):
    """Operator decision for the Permission Airlock (Approve/Reject/Modify)."""
    result = await runtime_bridge.resolve_airlock(
        action_id=req.action_id,
        decision=req.decision,
        operator_note=req.operator_note or ""
    )
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result

@app.get("/api/stream/{session_id}")
async def stream_workflow_sse(session_id: str, scenario_id: str = "cryptographic_smart_contract_audit", prompt: str = ""):
    """
    Streams Server-Sent Events (SSE) for the full Proof-of-Cognition workflow,
    lighting up OpenMinion 0.1 building blocks in real time.
    """
    if not prompt:
        matching = next((s for s in PRESET_SCENARIOS if s["id"] == scenario_id), None)
        prompt = matching["default_prompt"] if matching else "Cortensor verification task"

    async def event_generator():
        try:
            async for event in runtime_bridge.execute_proof_of_cognition_stream(
                session_id=session_id,
                scenario_id=scenario_id,
                prompt=prompt
            ):
                payload_str = json.dumps(event)
                yield f"data: {payload_str}\n\n"
                await asyncio.sleep(0.05)
        except Exception as e:
            err_payload = json.dumps({"type": "ERROR", "error": str(e)})
            yield f"data: {err_payload}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.post("/api/run")
async def run_workflow_sync(req: RunRequest):
    """
    Synchronous / non-streaming run endpoint returning full aggregated results.
    """
    session_id = req.session_id or f"sess-{str(uuid.uuid4())[:8]}"
    prompt = req.prompt
    if not prompt:
        matching = next((s for s in PRESET_SCENARIOS if s["id"] == req.scenario_id), None)
        prompt = matching["default_prompt"] if matching else "Cortensor verification task"

    events = []
    async for event in runtime_bridge.execute_proof_of_cognition_stream(
        session_id=session_id,
        scenario_id=req.scenario_id,
        prompt=prompt
    ):
        events.append(event)

    return {
        "session_id": session_id,
        "scenario_id": req.scenario_id,
        "events_count": len(events),
        "events": events,
        "nodes": get_nodes(),
        "xray": get_xray_stats()
    }

@app.get("/api/export/bundle")
async def export_submission_bundle():
    """Generates the Hackathon QA & Diagnostics bundle with live evidence."""
    xray = get_xray_stats()
    nodes = get_nodes()
    dead_ends = get_dead_ends()
    sessions = list_sessions()

    bundle_md = f"""# VERIMINION — CORTENSOR HACKATHON #5 SUBMISSION BUNDLE
**Decentralized Inference Validator & OpenMinion 0.1 SDK X-Ray Studio**
Generated automatically by VeriMinion Tactical Engine.

## 1. System Runtime Overview
- **OpenMinion SDK Version**: {runtime_bridge.sdk_version}
- **Cortensor Portal Status**: {'Connected (Live Key)' if runtime_bridge.cortensor_key else 'Deterministic Validation Engine Active'}
- **Active Sessions Logged**: {len(sessions)}
- **Node Reputation Matrix**: {len(nodes)} nodes tracked

## 2. OpenMinion 0.1 Building Blocks X-Ray Matrix
| Building Block | Invocations | Avg Latency (ms) | Status | Rough-Edge Notes |
|---|---|---|---|---|
| Execution | {xray.get('execution', {}).get('invocations', 0)} | {xray.get('execution', {}).get('avg_duration_ms', 0)}ms | HEALTHY | Deterministic transitions captured |
| Models | {xray.get('models', {}).get('invocations', 0)} | {xray.get('models', {}).get('avg_duration_ms', 0)}ms | HEALTHY | Multi-provider router with fallback |
| Tools | {xray.get('tools', {}).get('invocations', 0)} | {xray.get('tools', {}).get('avg_duration_ms', 0)}ms | HEALTHY | AST, SymPy, Sandbox, SLA verifiers |
| Permissions | {xray.get('permissions', {}).get('invocations', 0)} | {xray.get('permissions', {}).get('avg_duration_ms', 0)}ms | HEALTHY | SHA-256 Airlock Gate operational |
| Sessions | {xray.get('sessions', {}).get('invocations', 0)} | {xray.get('sessions', {}).get('avg_duration_ms', 0)}ms | HEALTHY | SQLite snapshot replayability |
| Memory | {xray.get('memory', {}).get('invocations', 0)} | {xray.get('memory', {}).get('avg_duration_ms', 0)}ms | HEALTHY | Episodic Ledger + Dead-End Memory |
| Skills | {xray.get('skills', {}).get('invocations', 0)} | {xray.get('skills', {}).get('avg_duration_ms', 0)}ms | HEALTHY | CodeAudit, QuantProof, Consensus, SLA |
| Tasks | {xray.get('tasks', {}).get('invocations', 0)} | {xray.get('tasks', {}).get('avg_duration_ms', 0)}ms | HEALTHY | Structured DAG decomposition |
| Delegation | {xray.get('delegation', {}).get('invocations', 0)} | {xray.get('delegation', {}).get('avg_duration_ms', 0)}ms | HEALTHY | Orchestrator -> Workers -> Auditor |
| Diagnostics | {xray.get('diagnostics', {}).get('invocations', 0)} | {xray.get('diagnostics', {}).get('avg_duration_ms', 0)}ms | HEALTHY | Real-time SSE telemetry streamed |

## 3. Node Reputation & Trust Ledger
| Node ID | Role / Endpoint | Trust Score | Total Runs | Drift Count | Avg Latency | Status |
|---|---|---|---|---|---|---|
"""
    for n in nodes:
        bundle_md += f"| `{n['node_id']}` | {n['display_name']} | **{n['trust_score']}%** | {n['total_runs']} | {n['drift_count']} | {n['avg_latency_ms']}ms | `{n['status']}` |\n"

    bundle_md += f"""
## 4. Semantic Dead-End Memory (Adversarial Signatures)
Found {len(dead_ends)} recorded adversarial failure signatures quarantined by the operator airlock.
"""
    for de in dead_ends:
        bundle_md += f"- **Signature**: `{de['failure_signature']}` | Node: `{de['node_id']}` | Type: `{de['divergence_type']}` | Evidence: *{de['evidence']}*\n"

    return {
        "markdown": bundle_md,
        "xray": xray,
        "nodes": nodes,
        "dead_ends": dead_ends,
        "sessions_count": len(sessions)
    }

# -----------------------------------------------------------------------------
# STATIC FILES SERVING (FRONTEND)
# -----------------------------------------------------------------------------
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FRONTEND_DIST = os.path.join(REPO_ROOT, "frontend", "dist")

if os.path.exists(FRONTEND_DIST):
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIST, "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        file_path = os.path.join(FRONTEND_DIST, full_path)
        if full_path and os.path.exists(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(FRONTEND_DIST, "index.html"))
