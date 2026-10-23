"""
VeriMinion Automated Test Suite
-------------------------------
Verifies ALL 10 mandated building blocks of the OpenMinion 0.1 Python SDK:
 1. execution
 2. models
 3. tools
 4. permissions
 5. sessions
 6. memory
 7. skills
 8. tasks
 9. delegation
10. diagnostics
Plus FastAPI REST & SSE endpoints.
"""

import os
import sys
import pytest
from fastapi.testclient import TestClient

# Ensure root directory is on PYTHONPATH
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from backend.core.tools import (
    ast_syntax_and_security_verifier,
    math_symbolic_verifier,
    deterministic_code_runner,
    schema_compliance_checker,
    latency_throughput_benchmark_tool
)
from backend.core.skills import (
    AdversarialCodeAuditSkill,
    QuantitativeProofSkill,
    ByzantineConsensusSkill,
    CortensorTelemetrySkill
)
from backend.core.storage import (
    init_db,
    save_session,
    get_session,
    list_sessions,
    get_nodes,
    update_node_reputation,
    set_node_quarantine,
    record_dead_end,
    get_dead_ends,
    get_xray_stats
)
from backend.core.openminion_runtime import OpenMinionRuntimeBridge
from backend.api.server import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_test_db():
    init_db()


# -----------------------------------------------------------------------------
# 1. TOOLS BUILDING BLOCK TESTS
# -----------------------------------------------------------------------------
def test_block_tools_ast_verifier():
    clean_code = "def safe_add(a, b):\n    return a + b\n"
    res_clean = ast_syntax_and_security_verifier(clean_code)
    assert res_clean["valid"] is True
    assert len(res_clean["security_violations"]) == 0

    malicious_code = "import os\ndef exploit():\n    os.system('rm -rf /')\n    eval('2+2')\n"
    res_malicious = ast_syntax_and_security_verifier(malicious_code)
    assert res_malicious["valid"] is False
    assert len(res_malicious["security_violations"]) >= 1


def test_block_tools_math_symbolic_verifier():
    expr_a = "S * exp(-r*T) + K"
    expr_b = "K + S * exp(-r*T)"
    res_eq = math_symbolic_verifier(expr_a, expr_b)
    assert res_eq["valid"] is True
    assert res_eq["is_equivalent"] is True

    expr_drift = "K + S * exp(r*T)" # intentional sign flip
    res_drift = math_symbolic_verifier(expr_a, expr_drift)
    assert res_drift["valid"] is False


def test_block_tools_deterministic_code_runner():
    good_code = "def compute(a, b):\n    return a * 2 + b\n"
    test_cases = [{"inputs": [2, 3], "expected": 7}, {"inputs": [0, 5], "expected": 5}]
    res_good = deterministic_code_runner(good_code, test_cases)
    assert res_good["valid"] is True
    assert res_good["passed_tests"] == 2

    bad_code = "def compute(a, b):\n    return a + b\n"
    res_bad = deterministic_code_runner(bad_code, test_cases)
    assert res_bad["valid"] is False
    assert res_bad["passed_tests"] < 2


def test_block_tools_schema_and_latency():
    schema_res = schema_compliance_checker({"benchmark": "PASS", "score": 95}, ["benchmark", "score"], {"score": "int"})
    assert schema_res["valid"] is True

    sla_res = latency_throughput_benchmark_tool("node-alpha", 100, 200, 250.0)
    assert sla_res["valid"] is True
    assert sla_res["sla_breached"] is False

    sla_bad = latency_throughput_benchmark_tool("node-gamma", 100, 200, 2800.0)
    assert sla_bad["valid"] is False
    assert sla_bad["sla_breached"] is True


# -----------------------------------------------------------------------------
# 2. SKILLS BUILDING BLOCK TESTS
# -----------------------------------------------------------------------------
def test_block_skills_code_audit():
    clean_contract = "class Vault:\n    def withdraw(self, amt):\n        self.bal -= amt\n        self.transfer(amt)\n"
    audit_clean = AdversarialCodeAuditSkill.audit(clean_contract)
    assert audit_clean["passed"] is True

    vulnerable_contract = "class Vault:\n    def withdraw(self, amt):\n        self.transfer(amt)\n        self.bal -= amt\n"
    audit_vuln = AdversarialCodeAuditSkill.audit(vulnerable_contract)
    assert audit_vuln["reentrancy_risk_flagged"] is True


def test_block_skills_byzantine_consensus():
    evals = [
        {"node_id": "node-alpha", "is_valid": True},
        {"node_id": "node-beta", "is_valid": True},
        {"node_id": "node-gamma", "is_valid": False, "divergence_reason": "Ast Violation"}
    ]
    consensus = ByzantineConsensusSkill.evaluate_quorum(evals)
    assert consensus["consensus_reached"] is True
    assert consensus["honest_nodes_count"] == 2
    assert consensus["byzantine_nodes_count"] == 1
    assert consensus["byzantine_nodes"][0]["node_id"] == "node-gamma"


# -----------------------------------------------------------------------------
# 3. MEMORY & SESSIONS BUILDING BLOCK TESTS
# -----------------------------------------------------------------------------
def test_block_memory_ledger_and_dead_ends():
    nodes = get_nodes()
    assert len(nodes) >= 3

    # Update node reputation
    update_node_reputation("node-alpha", passed=True, latency_ms=190.0)
    update_node_reputation("node-gamma", passed=False, latency_ms=900.0)
    
    updated_nodes = {n["node_id"]: n for n in get_nodes()}
    assert updated_nodes["node-alpha"]["successful_runs"] >= 1
    assert updated_nodes["node-gamma"]["drift_count"] >= 1

    # Record dead-end memory
    record_dead_end("node-gamma", "sig-1234", "AST_VIOLATION", "Dangerous os.system call")
    dead_ends = get_dead_ends()
    assert any(de["node_id"] == "node-gamma" for de in dead_ends)


def test_block_sessions_persistence():
    sess_id = "test-sess-001"
    save_session(sess_id, "cryptographic_smart_contract_audit", "test prompt", "COMPLETED", {"step": 1}, "Test summary")
    
    retrieved = get_session(sess_id)
    assert retrieved is not None
    assert retrieved["session_id"] == sess_id
    assert retrieved["state_snapshot"]["step"] == 1

    all_sess = list_sessions()
    assert any(s["session_id"] == sess_id for s in all_sess)


# -----------------------------------------------------------------------------
# 4. PERMISSIONS AIRLOCK BUILDING BLOCK TESTS
# -----------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_block_permissions_airlock():
    bridge = OpenMinionRuntimeBridge()
    airlock = await bridge.create_airlock_request(
        session_id="test-airlock-sess",
        action_type="QUARANTINE_NODE",
        target_node="node-gamma",
        details="Byzantine AST drift detected"
    )
    assert airlock["action_id"].startswith("act-")
    assert len(airlock["mutation_hash"]) == 64 # SHA-256

    # Test Approve Operator Action
    res = await bridge.resolve_airlock(airlock["action_id"], "APPROVE", "Verified by operator")
    assert res["success"] is True
    assert res["decision"] == "APPROVE"

    nodes = {n["node_id"]: n for n in get_nodes()}
    assert nodes["node-gamma"]["status"] == "QUARANTINED"


# -----------------------------------------------------------------------------
# 5. MODELS, TASKS, DELEGATION & DIAGNOSTICS TESTS
# -----------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_block_models_and_execution_stream():
    bridge = OpenMinionRuntimeBridge()
    session_id = "stream-test-001"
    scenario_id = "cryptographic_smart_contract_audit"
    prompt = "Test contract audit"

    events = []
    async for ev in bridge.execute_proof_of_cognition_stream(session_id, scenario_id, prompt):
        events.append(ev)

    assert len(events) >= 5
    event_types = [e["type"] for e in events]
    assert "SESSION_INIT" in event_types
    assert "TASK_DAG_UPDATE" in event_types
    assert "NODE_OUTPUT" in event_types
    assert "VERIFICATION_RESULT" in event_types
    assert "CONSENSUS_EVALUATION" in event_types
    assert "WORKFLOW_COMPLETE" in event_types


def test_block_diagnostics_xray():
    xray = get_xray_stats()
    assert "execution" in xray
    assert "models" in xray
    assert "tools" in xray
    assert "permissions" in xray
    assert "sessions" in xray
    assert "memory" in xray
    assert "skills" in xray
    assert "tasks" in xray
    assert "delegation" in xray
    assert "diagnostics" in xray


# -----------------------------------------------------------------------------
# 6. FASTAPI ENDPOINT INTEGRATION TESTS
# -----------------------------------------------------------------------------
def test_api_status():
    res = client.get("/api/status")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ONLINE"
    assert "openminion_sdk_version" in data


def test_api_scenarios():
    res = client.get("/api/scenarios")
    assert res.status_code == 200
    scenarios = res.json()
    assert len(scenarios) == 4
    ids = [s["id"] for s in scenarios]
    assert "cryptographic_smart_contract_audit" in ids
    assert "quantitative_derivative_pricing_proof" in ids
    assert "deterministic_python_algorithm_synthesis" in ids
    assert "cortensor_portal_vs_gemma4_stress_benchmark" in ids


def test_api_nodes():
    res = client.get("/api/nodes")
    assert res.status_code == 200
    nodes = res.json()
    assert len(nodes) >= 3


def test_api_run_workflow():
    payload = {
        "scenario_id": "quantitative_derivative_pricing_proof",
        "prompt": "Test derivative formula verification"
    }
    res = client.post("/api/run", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["scenario_id"] == "quantitative_derivative_pricing_proof"
    assert data["events_count"] > 0


def test_api_export_bundle():
    res = client.get("/api/export/bundle")
    assert res.status_code == 200
    bundle = res.json()
    assert "markdown" in bundle
    assert "CORTENSOR HACKATHON #5 SUBMISSION BUNDLE" in bundle["markdown"]
    assert "xray" in bundle
