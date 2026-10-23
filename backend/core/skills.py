"""
VeriMinion Composable Domain Skill Packs
---------------------------------------
Implements the 'skills' building block of OpenMinion 0.1 for Cortensor inference validation.
Packs domain knowledge, evaluation heuristics, and verifiable rules.
"""

from typing import Any, Dict, List, Optional
from backend.core.tools import (
    ast_syntax_and_security_verifier,
    math_symbolic_verifier,
    deterministic_code_runner,
    schema_compliance_checker,
    latency_throughput_benchmark_tool
)


class AdversarialCodeAuditSkill:
    """
    Evaluates algorithmic code and smart contract implementations for
    security violations, reentrancy patterns, and malicious AST structures.
    """
    skill_name = "AdversarialCodeAuditSkill"
    version = "1.0.0"

    @classmethod
    def audit(cls, code_snippet: str, test_vectors: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        # 1. Run AST Syntax & Security Verification
        ast_result = ast_syntax_and_security_verifier(code_snippet)
        
        # 2. Check for common Solidity/Python reentrancy or state mutations before transfer
        reentrancy_risk = False
        lower_code = code_snippet.lower()
        if "transfer" in lower_code and ("bal" in lower_code or "balance" in lower_code):
            # Check pattern: transfer called before updating balance / bal
            t_idx = lower_code.find("transfer")
            # Look for state assignment patterns after transfer
            for pattern in ["bal -=", "bal =", "balance -=", "balance =", "balances["]:
                b_idx = lower_code.find(pattern)
                if b_idx != -1 and b_idx > t_idx:
                    reentrancy_risk = True
                    break

        runner_result = None
        if test_vectors and ast_result["valid"]:
            runner_result = deterministic_code_runner(code_snippet, test_vectors)

        all_clean = ast_result["valid"] and not reentrancy_risk
        if runner_result:
            all_clean = all_clean and runner_result["valid"]

        return {
            "skill": cls.skill_name,
            "passed": all_clean,
            "ast_audit": ast_result,
            "reentrancy_risk_flagged": reentrancy_risk,
            "dynamic_runner": runner_result,
            "recommendation": "APPROVE" if all_clean else "QUARANTINE_ADVISORY"
        }


class QuantitativeProofSkill:
    """
    Validates derivative pricing models, Black-Scholes PDE solutions, and
    algebraic proofs using SymPy symbolic verification.
    """
    skill_name = "QuantitativeProofSkill"
    version = "1.0.0"

    @classmethod
    def verify_derivative(cls, submitted_formula: str, canonical_formula: str, context: str = "Derivative Pricing") -> Dict[str, Any]:
        symbolic_res = math_symbolic_verifier(submitted_formula, canonical_formula, context)
        return {
            "skill": cls.skill_name,
            "passed": symbolic_res["valid"],
            "symbolic_verification": symbolic_res,
            "recommendation": "VALIDATED" if symbolic_res["valid"] else "BYZANTINE_DRIFT_ALERT"
        }


class ByzantineConsensusSkill:
    """
    Calculates multi-node consensus, applies Byzantine Fault Tolerance (BFT)
    scoring thresholds (e.g., 2f+1 quorum), and detects adversarial outliers.
    """
    skill_name = "ByzantineConsensusSkill"
    version = "1.0.0"

    @classmethod
    def evaluate_quorum(cls, node_evaluations: List[Dict[str, Any]]) -> Dict[str, Any]:
        total_nodes = len(node_evaluations)
        if total_nodes == 0:
            return {"consensus_reached": False, "quorum_ratio": 0.0, "byzantine_nodes": []}

        valid_nodes = [n for n in node_evaluations if n.get("is_valid", False)]
        invalid_nodes = [n for n in node_evaluations if not n.get("is_valid", False)]

        # Byzantine Fault Tolerance standard: > 2/3 agreement for consensus
        quorum_ratio = round(len(valid_nodes) / total_nodes, 2)
        consensus_reached = quorum_ratio >= 0.66

        byzantine_nodes = [
            {
                "node_id": n["node_id"],
                "divergence": n.get("divergence_reason", "Validation failure"),
                "severity": "CRITICAL" if not n.get("is_valid") else "LOW"
            }
            for n in invalid_nodes
        ]

        return {
            "skill": cls.skill_name,
            "total_nodes": total_nodes,
            "honest_nodes_count": len(valid_nodes),
            "byzantine_nodes_count": len(invalid_nodes),
            "quorum_ratio": quorum_ratio,
            "consensus_reached": consensus_reached,
            "byzantine_nodes": byzantine_nodes,
            "consensus_verdict": "CONSENSUS_AFFIRMED" if consensus_reached else "CONSENSUS_FAILURE_BYZANTINE_MAJORITY"
        }


class CortensorTelemetrySkill:
    """
    Analyzes decentralized inference node SLA metrics, token rates,
    and formats comprehensive diagnostic bundles for the Cortensor Portal.
    """
    skill_name = "CortensorTelemetrySkill"
    version = "1.0.0"

    @classmethod
    def evaluate_sla(cls, node_id: str, prompt_tokens: int, completion_tokens: int, latency_ms: float) -> Dict[str, Any]:
        benchmark = latency_throughput_benchmark_tool(node_id, prompt_tokens, completion_tokens, latency_ms)
        return {
            "skill": cls.skill_name,
            "benchmark": benchmark,
            "sla_tier": "TIER_1_SUPERIOR" if latency_ms < 300 else ("TIER_2_ACCEPTABLE" if latency_ms < 1500 else "SLA_BREACHED")
        }
