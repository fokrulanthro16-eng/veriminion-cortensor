"""
VeriMinion Persistent SQLite Storage
------------------------------------
Implements persistent storage for Sessions, Memory (Node Trust Ledger + Semantic Dead-End Memory),
Permissions Audit Log, and Telemetry Events.
"""

import sqlite3
import json
import os
import time
from typing import Any, Dict, List, Optional

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(REPO_ROOT, "veriminion.db")


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Sessions table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        session_id TEXT PRIMARY KEY,
        created_at REAL,
        scenario_id TEXT,
        prompt TEXT,
        status TEXT,
        state_snapshot TEXT,
        summary TEXT
    )
    """)

    # 2. Node Trust Ledger
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS node_trust_ledger (
        node_id TEXT PRIMARY KEY,
        display_name TEXT,
        endpoint_type TEXT,
        trust_score REAL,
        total_runs INTEGER,
        successful_runs INTEGER,
        drift_count INTEGER,
        avg_latency_ms REAL,
        status TEXT,
        last_updated REAL
    )
    """)

    # 3. Semantic Dead-End Memory
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dead_end_memory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        node_id TEXT,
        failure_signature TEXT,
        divergence_type TEXT,
        evidence TEXT,
        recorded_at REAL
    )
    """)

    # 4. Permission Airlock Audit Log
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS permission_audit_log (
        action_id TEXT PRIMARY KEY,
        session_id TEXT,
        action_type TEXT,
        target_node TEXT,
        mutation_hash TEXT,
        details TEXT,
        decision TEXT,
        operator_note TEXT,
        timestamp REAL
    )
    """)

    # 5. Diagnostics Telemetry Log
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS telemetry_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT,
        building_block TEXT,
        event_type TEXT,
        duration_ms REAL,
        payload TEXT,
        timestamp REAL
    )
    """)

    # Pre-seed default nodes if not present
    default_nodes = [
        ("node-alpha", "Node-Alpha [Cortensor Portal]", "cortensor_portal", 98.5, 42, 41, 1, 230.4, "HEALTHY"),
        ("node-beta", "Node-Beta [Gemma4 Fast Tier]", "gemma4_local", 94.2, 38, 36, 2, 85.2, "HEALTHY"),
        ("node-gamma", "Node-Gamma [Adversarial Drift Node]", "quantized_drift", 62.0, 35, 21, 14, 145.0, "MONITORED"),
    ]

    for nid, dname, etype, tscore, total, succ, drift, lat, stat in default_nodes:
        cursor.execute("""
        INSERT OR IGNORE INTO node_trust_ledger 
        (node_id, display_name, endpoint_type, trust_score, total_runs, successful_runs, drift_count, avg_latency_ms, status, last_updated)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (nid, dname, etype, tscore, total, succ, drift, lat, stat, time.time()))

    conn.commit()
    conn.close()


# Database helper methods
def list_sessions() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT session_id, created_at, scenario_id, prompt, status, summary FROM sessions ORDER BY created_at DESC LIMIT 50")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    d = dict(row)
    if d.get("state_snapshot"):
        try:
            d["state_snapshot"] = json.loads(d["state_snapshot"])
        except Exception:
            pass
    return d


def save_session(session_id: str, scenario_id: str, prompt: str, status: str, state_snapshot: Dict[str, Any], summary: str = ""):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO sessions (session_id, created_at, scenario_id, prompt, status, state_snapshot, summary)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(session_id) DO UPDATE SET
        status = excluded.status,
        state_snapshot = excluded.state_snapshot,
        summary = excluded.summary
    """, (session_id, time.time(), scenario_id, prompt, status, json.dumps(state_snapshot), summary))
    conn.commit()
    conn.close()


def get_nodes() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM node_trust_ledger ORDER BY trust_score DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_node_reputation(node_id: str, passed: bool, latency_ms: float):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM node_trust_ledger WHERE node_id = ?", (node_id,))
    row = cursor.fetchone()
    if row:
        total = row["total_runs"] + 1
        succ = row["successful_runs"] + (1 if passed else 0)
        drift = row["drift_count"] + (0 if passed else 1)
        # Exponential moving average for latency
        avg_lat = round(row["avg_latency_ms"] * 0.8 + latency_ms * 0.2, 1)
        # Trust score formula: weighted pass rate minus drift penalties
        pass_ratio = (succ / total) * 100.0
        drift_penalty = min(drift * 2.0, 30.0)
        trust_score = max(0.0, min(100.0, round(pass_ratio - drift_penalty * 0.2, 1)))

        status = row["status"]
        if status != "QUARANTINED":
            if trust_score < 70.0:
                status = "DEGRADED"
            else:
                status = "HEALTHY"

        cursor.execute("""
        UPDATE node_trust_ledger 
        SET trust_score = ?, total_runs = ?, successful_runs = ?, drift_count = ?, 
            avg_latency_ms = ?, status = ?, last_updated = ?
        WHERE node_id = ?
        """, (trust_score, total, succ, drift, avg_lat, status, time.time(), node_id))
    conn.commit()
    conn.close()


def set_node_quarantine(node_id: str, status: str = "QUARANTINED"):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE node_trust_ledger SET status = ?, last_updated = ? WHERE node_id = ?", (status, time.time(), node_id))
    conn.commit()
    conn.close()


def record_dead_end(node_id: str, signature: str, div_type: str, evidence: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO dead_end_memory (node_id, failure_signature, divergence_type, evidence, recorded_at)
    VALUES (?, ?, ?, ?, ?)
    """, (node_id, signature, div_type, evidence, time.time()))
    conn.commit()
    conn.close()


def get_dead_ends(limit: int = 10) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM dead_end_memory ORDER BY recorded_at DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def record_permission_action(action_id: str, session_id: str, action_type: str, target_node: str, mutation_hash: str, details: str, decision: str, note: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO permission_audit_log (action_id, session_id, action_type, target_node, mutation_hash, details, decision, operator_note, timestamp)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(action_id) DO UPDATE SET
        decision = excluded.decision,
        operator_note = excluded.operator_note
    """, (action_id, session_id, action_type, target_node, mutation_hash, details, decision, note, time.time()))
    conn.commit()
    conn.close()


def log_telemetry_event(session_id: str, building_block: str, event_type: str, duration_ms: float, payload: Dict[str, Any]):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO telemetry_events (session_id, building_block, event_type, duration_ms, payload, timestamp)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (session_id, building_block, event_type, duration_ms, json.dumps(payload), time.time()))
    conn.commit()
    conn.close()


def get_xray_stats() -> Dict[str, Any]:
    """
    Aggregates real-time invocation counts, average latency, and health per building block.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT building_block, COUNT(*) as count, AVG(duration_ms) as avg_latency
    FROM telemetry_events
    GROUP BY building_block
    """)
    rows = cursor.fetchall()
    conn.close()

    all_blocks = [
        "execution", "models", "tools", "permissions", "sessions",
        "memory", "skills", "tasks", "delegation", "diagnostics"
    ]
    
    stats = {}
    db_data = {r["building_block"]: r for r in rows}

    for b in all_blocks:
        if b in db_data:
            stats[b] = {
                "invocations": db_data[b]["count"],
                "avg_duration_ms": round(db_data[b]["avg_latency"] or 0.0, 2),
                "status": "HEALTHY",
                "rough_edge_detected": False
            }
        else:
            stats[b] = {
                "invocations": 0,
                "avg_duration_ms": 0.0,
                "status": "READY",
                "rough_edge_detected": False
            }

    return stats
