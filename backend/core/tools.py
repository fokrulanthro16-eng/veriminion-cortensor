"""
VeriMinion Deterministic Verification Tools
-------------------------------------------
Implements the 'tools' building block of OpenMinion 0.1 for Cortensor inference validation.
Verifies worker node outputs mathematically, programmatically, and syntactically.
"""

import ast
import json
import math
import time
from typing import Any, Dict, List, Optional
import sympy as sp


def ast_syntax_and_security_verifier(code_snippet: str) -> Dict[str, Any]:
    """
    Parses Python code using AST, audits for dangerous builtins, malicious
    system calls, and structural validity.
    """
    start_time = time.perf_counter()
    violations: List[str] = []
    
    # 1. Parse AST
    try:
        parsed_ast = ast.parse(code_snippet)
    except SyntaxError as e:
        return {
            "valid": False,
            "tool": "ast_syntax_and_security_verifier",
            "ast_nodes_count": 0,
            "security_violations": [f"SyntaxError on line {e.lineno}: {e.msg}"],
            "complexity_score": 0,
            "error": str(e),
            "execution_ms": round((time.perf_counter() - start_time) * 1000, 2),
        }

    # 2. Inspect AST Nodes for banned calls/imports
    dangerous_calls = {"eval", "exec", "__import__", "compile"}
    dangerous_modules = {"subprocess", "socket", "pty", "shutil", "winreg", "ctypes"}

    node_count = 0
    complexity = 1  # Base cyclomatic complexity

    for node in ast.walk(parsed_ast):
        node_count += 1
        
        # Check Imports
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name in dangerous_modules:
                    violations.append(f"Forbidden import '{alias.name}' detected")
        elif isinstance(node, ast.ImportFrom):
            if node.module in dangerous_modules:
                violations.append(f"Forbidden import from '{node.module}' detected")
        
        # Check Function Calls
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in dangerous_calls:
                violations.append(f"Dangerous call '{node.func.id}()' detected")
            elif isinstance(node.func, ast.Attribute):
                if node.func.attr in {"system", "popen", "spawn"}:
                    violations.append(f"Dangerous attribute call '.{node.func.attr}()' detected")
                    
        # Cyclomatic complexity branch points
        elif isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler, ast.With)):
            complexity += 1

    execution_ms = round((time.perf_counter() - start_time) * 1000, 2)
    is_valid = len(violations) == 0

    return {
        "valid": is_valid,
        "tool": "ast_syntax_and_security_verifier",
        "ast_nodes_count": node_count,
        "security_violations": violations,
        "complexity_score": complexity,
        "error": None if is_valid else "; ".join(violations),
        "execution_ms": execution_ms,
    }


def math_symbolic_verifier(expression_a: str, expression_b: str, context: Optional[str] = None) -> Dict[str, Any]:
    """
    Symbolic mathematical equivalence verifier using SymPy.
    Proves whether two mathematical formulas or derivative solutions are identical.
    """
    start_time = time.perf_counter()
    try:
        # Pre-declare common mathematical symbols
        S, K, T, r, sigma, x, y, z, t, alpha, beta = sp.symbols('S K T r sigma x y z t alpha beta', real=True)
        local_symbols = {
            'S': S, 'K': K, 'T': T, 'r': r, 'sigma': sigma,
            'x': x, 'y': y, 'z': z, 't': t, 'alpha': alpha, 'beta': beta,
            'exp': sp.exp, 'log': sp.log, 'sqrt': sp.sqrt, 'pi': sp.pi,
            'sin': sp.sin, 'cos': sp.cos
        }

        # Parse expressions
        sym_a = sp.sympify(expression_a, locals=local_symbols)
        sym_b = sp.sympify(expression_b, locals=local_symbols)

        # Compute difference and simplify
        difference = sp.simplify(sym_a - sym_b)
        is_equivalent = difference == 0

        execution_ms = round((time.perf_counter() - start_time) * 1000, 2)

        return {
            "valid": is_equivalent,
            "tool": "math_symbolic_verifier",
            "context": context or "symbolic_equality",
            "expr_a_latex": sp.latex(sym_a),
            "expr_b_latex": sp.latex(sym_b),
            "difference_simplified": str(difference),
            "is_equivalent": is_equivalent,
            "execution_ms": execution_ms,
            "error": None if is_equivalent else f"Symbolic divergence detected: residual = {difference}"
        }
    except Exception as e:
        return {
            "valid": False,
            "tool": "math_symbolic_verifier",
            "context": context or "symbolic_equality",
            "expr_a_latex": "",
            "expr_b_latex": "",
            "difference_simplified": "ERROR",
            "is_equivalent": False,
            "execution_ms": round((time.perf_counter() - start_time) * 1000, 2),
            "error": f"SymPy parsing failed: {str(e)}"
        }


def deterministic_code_runner(code_snippet: str, test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Executes a pure function against test vectors in a sandboxed, restricted namespace.
    """
    start_time = time.perf_counter()
    safe_globals = {
        "__builtins__": {
            "range": range, "len": len, "int": int, "float": float, "str": str,
            "list": list, "dict": dict, "set": set, "tuple": tuple, "bool": bool,
            "min": min, "max": max, "sum": sum, "abs": abs, "round": round,
            "enumerate": enumerate, "zip": zip, "sorted": sorted, "reversed": reversed
        },
        "math": math
    }
    safe_locals: Dict[str, Any] = {}

    # First execute the definition
    try:
        compiled = compile(code_snippet, "<sandboxed_worker_code>", "exec")
        exec(compiled, safe_globals, safe_locals)
    except Exception as e:
        return {
            "valid": False,
            "tool": "deterministic_code_runner",
            "total_tests": len(test_cases),
            "passed_tests": 0,
            "test_results": [],
            "error": f"Compilation failed: {str(e)}",
            "execution_ms": round((time.perf_counter() - start_time) * 1000, 2)
        }

    # Find the synthesized function
    func = None
    for name, val in safe_locals.items():
        if callable(val) and not name.startswith("_"):
            func = val
            break

    if not func:
        return {
            "valid": False,
            "tool": "deterministic_code_runner",
            "total_tests": len(test_cases),
            "passed_tests": 0,
            "test_results": [],
            "error": "No callable function found in synthesis output",
            "execution_ms": round((time.perf_counter() - start_time) * 1000, 2)
        }

    results = []
    passed = 0
    divergence = None

    for idx, tc in enumerate(test_cases):
        args = tc.get("inputs", [])
        expected = tc.get("expected")
        try:
            actual = func(*args) if isinstance(args, list) else func(**args)
            matches = actual == expected
            if matches:
                passed += 1
            else:
                if divergence is None:
                    divergence = f"Test #{idx+1} mismatch: expected {expected!r}, got {actual!r}"
            results.append({
                "test_index": idx + 1,
                "input": args,
                "expected": expected,
                "actual": actual,
                "passed": matches
            })
        except Exception as ex:
            divergence = f"Test #{idx+1} raised exception: {str(ex)}"
            results.append({
                "test_index": idx + 1,
                "input": args,
                "expected": expected,
                "actual": f"EXCEPTION: {str(ex)}",
                "passed": False
            })

    execution_ms = round((time.perf_counter() - start_time) * 1000, 2)
    all_passed = (passed == len(test_cases))

    return {
        "valid": all_passed,
        "tool": "deterministic_code_runner",
        "total_tests": len(test_cases),
        "passed_tests": passed,
        "test_results": results,
        "error": divergence if not all_passed else None,
        "execution_ms": execution_ms
    }


def schema_compliance_checker(data: Any, required_fields: List[str], expected_types: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """
    Validates dictionary/JSON response against schema contract.
    """
    start_time = time.perf_counter()
    violations = []
    
    if not isinstance(data, dict):
        return {
            "valid": False,
            "tool": "schema_compliance_checker",
            "violations": ["Payload is not a valid JSON object/dict"],
            "execution_ms": round((time.perf_counter() - start_time) * 1000, 2)
        }

    for req in required_fields:
        if req not in data:
            violations.append(f"Missing required field: '{req}'")

    if expected_types:
        type_map = {
            "str": str,
            "int": int,
            "float": (int, float),
            "bool": bool,
            "list": list,
            "dict": dict
        }
        for field, exp_type_name in expected_types.items():
            if field in data:
                expected_cls = type_map.get(exp_type_name)
                if expected_cls and not isinstance(data[field], expected_cls):
                    violations.append(f"Field '{field}' expected type {exp_type_name}, got {type(data[field]).__name__}")

    execution_ms = round((time.perf_counter() - start_time) * 1000, 2)
    is_valid = len(violations) == 0

    return {
        "valid": is_valid,
        "tool": "schema_compliance_checker",
        "violations": violations,
        "validated_keys": list(data.keys()),
        "execution_ms": execution_ms,
        "error": "; ".join(violations) if violations else None
    }


def latency_throughput_benchmark_tool(node_id: str, prompt_tokens: int, completion_tokens: int, raw_latency_ms: float) -> Dict[str, Any]:
    """
    Calculates throughput (tokens/second) and SLA adherence for Cortensor node verification.
    """
    total_tokens = prompt_tokens + completion_tokens
    seconds = max(raw_latency_ms / 1000.0, 0.001)
    tokens_per_sec = round(total_tokens / seconds, 1)

    # SLA thresholds for decentralized inference:
    # Acceptable SLA < 1500 ms, Alert > 2500 ms
    sla_threshold_ms = 1500.0
    sla_breached = raw_latency_ms > sla_threshold_ms

    return {
        "valid": not sla_breached,
        "tool": "latency_throughput_benchmark_tool",
        "node_id": node_id,
        "latency_ms": raw_latency_ms,
        "tokens_per_sec": tokens_per_sec,
        "sla_threshold_ms": sla_threshold_ms,
        "sla_breached": sla_breached,
        "execution_ms": 0.5
    }
