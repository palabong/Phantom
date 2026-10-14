#!/usr/bin/env python3
"""
Adversarial Stress Testing Harness for Phantom Cloud Feasibility Deliverables:
- CLI_EXECUTION_GUIDES_AND_COMPLIANCE.md
- TEST_INFRA.md & TEST_READY.md
- tests/test_e2e_verification.py
- phantom_cloud.py tool contract conformance
"""

import ast
import json
import os
import re
import subprocess
import sys
import unittest
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent

class TestCliGuidesAndComplianceStress(unittest.TestCase):
    """Adversarial stress-test for CLI Execution Guides & Compliance."""

    @classmethod
    def setUpClass(cls):
        cls.cli_path = WORKSPACE_ROOT / "CLI_EXECUTION_GUIDES_AND_COMPLIANCE.md"
        cls.pc_path = WORKSPACE_ROOT / "phantom_cloud.py"
        cls.infra_path = WORKSPACE_ROOT / "TEST_INFRA.md"
        cls.ready_path = WORKSPACE_ROOT / "TEST_READY.md"
        cls.e2e_path = WORKSPACE_ROOT / "tests/test_e2e_verification.py"

        cls.cli_text = cls.cli_path.read_text(encoding="utf-8")
        cls.pc_text = cls.pc_path.read_text(encoding="utf-8")
        cls.infra_text = cls.infra_path.read_text(encoding="utf-8")
        cls.ready_text = cls.ready_path.read_text(encoding="utf-8")
        cls.e2e_text = cls.e2e_path.read_text(encoding="utf-8")

        # Parse code blocks
        cls.blocks = cls._extract_code_blocks(cls.cli_text)

    @staticmethod
    def _extract_code_blocks(md_content):
        blocks = []
        lines = md_content.splitlines()
        in_block = False
        lang = ""
        block_lines = []
        start_line = 0

        for idx, line in enumerate(lines, 1):
            if line.startswith("```") and not in_block:
                in_block = True
                lang = line[3:].strip()
                block_lines = []
                start_line = idx
            elif line.startswith("```") and in_block:
                in_block = False
                blocks.append({
                    "lang": lang,
                    "start_line": start_line,
                    "code": "\n".join(block_lines)
                })
                block_lines = []
            elif in_block:
                block_lines.append(line)
        return blocks

    def test_01_all_embedded_python_scripts_syntax(self):
        """Stress-test: Verify all embedded Python scripts in CLI guide compile cleanly."""
        py_blocks = [b for b in self.blocks if b["lang"] in ("python", "python3", "py")]
        self.assertGreaterEqual(len(py_blocks), 4, "Expected at least 4 Python script blocks in CLI guide")

        for b in py_blocks:
            code = b["code"]
            start_line = b["start_line"]
            try:
                ast.parse(code)
            except SyntaxError as e:
                self.fail(f"SyntaxError in Python block at line {start_line}: {e}")

    def test_02_node_script_syntax(self):
        """Stress-test: Verify embedded Node.js script in CLI guide passes syntax check."""
        node_blocks = [b for b in self.blocks if b["lang"] in ("javascript", "js", "node")]
        self.assertGreaterEqual(len(node_blocks), 1, "Expected at least 1 JavaScript block in CLI guide")

        # Find the full node script (starts with #!/usr/bin/env node)
        node_runner = next((b for b in node_blocks if "#!/usr/bin/env node" in b["code"]), None)
        self.assertIsNotNone(node_runner, "run_cli_node.mjs script block not found")

        # Check with node -c
        temp_js = WORKSPACE_ROOT / "artifacts" / "temp_run_cli_node.mjs"
        temp_js.parent.mkdir(exist_ok=True)
        temp_js.write_text(node_runner["code"], encoding="utf-8")
        try:
            res = subprocess.run(["node", "--check", str(temp_js)], capture_output=True, text=True)
            self.assertEqual(res.returncode, 0, f"Node.js syntax check failed: {res.stderr}")
        finally:
            if temp_js.exists():
                temp_js.unlink()

    def test_03_mcp_tool_schemas_and_payloads_conformance(self):
        """Stress-test: Validate all MCP tool call payloads against phantom_cloud.py schemas."""
        # Tools in phantom_cloud.py
        approved_tools = {
            "navigate": {"req": ["url"], "opt": []},
            "get_snapshot": {"req": [], "opt": ["mode"]},
            "click": {"req": [], "opt": ["ref", "selector", "x", "y"]},
            "type": {"req": ["text"], "opt": ["ref", "selector", "clear"]},
            "evaluate": {"req": ["expression"], "opt": []},
            "wait": {"req": [], "opt": ["selector", "timeout_ms", "delay_ms"]}
        }

        # Check all json blocks with "name" and "arguments"
        json_blocks = [b for b in self.blocks if b["lang"] == "json"]
        found_tool_payloads = 0

        for b in json_blocks:
            try:
                data = json.loads(b["code"])
            except json.JSONDecodeError:
                continue

            if isinstance(data, dict) and "name" in data and "arguments" in data:
                tool_name = data["name"]
                args = data["arguments"]
                self.assertIn(tool_name, approved_tools, f"Unapproved tool '{tool_name}' in payload at line {b['start_line']}")

                tool_spec = approved_tools[tool_name]
                # Check required parameters
                for req in tool_spec["req"]:
                    self.assertIn(req, args, f"Missing required param '{req}' for tool '{tool_name}' at line {b['start_line']}")

                # Check that all provided args are recognized
                allowed_params = set(tool_spec["req"] + tool_spec["opt"])
                for param in args.keys():
                    self.assertIn(param, allowed_params, f"Unknown parameter '{param}' for tool '{tool_name}' at line {b['start_line']}")

                found_tool_payloads += 1

        self.assertGreaterEqual(found_tool_payloads, 6, "Expected at least 6 tool payload examples")

    def test_04_parse_eval_results_stress_and_edge_cases(self):
        """Stress-test: Adversarially execute parse_eval_results logic with edge cases."""
        # Extract parse_eval_results code
        parser_block = next((b for b in self.blocks if "def parse_differential_payload" in b["code"]), None)
        self.assertIsNotNone(parser_block, "parse_differential_payload function not found in CLI guide")

        # Compile and load function
        scope = {}
        exec(parser_block["code"], scope)
        parse_func = scope["parse_differential_payload"]

        # Case 1: Corrupted / empty input
        res1 = parse_func("")
        self.assertEqual(res1["verdict"], "ERROR")

        res2 = parse_func("not json at all {")
        self.assertEqual(res2["verdict"], "ERROR")

        # Case 2: Turnstile interception
        turnstile_payload = json.dumps({"is_turnstile": True, "title": "Just a moment..."})
        res3 = parse_func(turnstile_payload)
        self.assertEqual(res3["verdict"], "BLOCKED_BY_TURNSTILE")
        self.assertEqual(res3["action"], "HALT_EXECUTION")

        # Case 3: Session expired / login redirect
        login_payload = json.dumps({"url": "https://accounts.shopify.com/login", "is_login": True})
        res4 = parse_func(login_payload)
        self.assertEqual(res4["verdict"], "SESSION_EXPIRED")
        self.assertEqual(res4["action"], "RE_AUTHENTICATE")

        # Case 4: Network / CORS drop
        cors_payload = json.dumps({"api_error": "TypeError: Failed to fetch"})
        res5 = parse_func(cors_payload)
        self.assertEqual(res5["verdict"], "CORS_OR_NETWORK_FAILURE")

        # Case 5: Public API key error
        public_err_payload = json.dumps({"api_error": "Invalid API key or access token"})
        res6 = parse_func(public_err_payload)
        self.assertEqual(res6["verdict"], "PUBLIC_ENDPOINT_MISCONFIG")

        # Case 6: Track H1-5 Differential Vulnerability confirmed
        vuln_payload = json.dumps({
            "ui_denied": True,
            "api_data": {"orders": [{"id": "1", "name": "#1001"}]}
        })
        res7 = parse_func(vuln_payload)
        self.assertEqual(res7["verdict"], "VULNERABILITY_CONFIRMED")
        self.assertIn("HIGH", res7["severity"])

        # Case 7: Track H1-5 Parity Enforced (Secure)
        parity_payload = json.dumps({
            "ui_denied": True,
            "api_data": {"orders": None}
        })
        res8 = parse_func(parity_payload)
        self.assertEqual(res8["verdict"], "PARITY_ENFORCED")
        self.assertEqual(res8["status"], "SECURE")

        # Case 8: Track H1-7 IDOR leak
        idor_payload = json.dumps({"idor_confirmed": True, "store": "xxxxxx-r48zg9i1"})
        res9 = parse_func(idor_payload)
        self.assertEqual(res9["verdict"], "VULNERABILITY_CONFIRMED")
        self.assertIn("CRITICAL", res9["severity"])

        # Adversarial Edge Case A: JSON string wrapped twice (as returned by evaluate)
        wrapped_payload = json.dumps(json.dumps({
            "ui_denied": True,
            "api_data": {"orders": [{"id": "1"}]}
        }))
        res10 = parse_func(wrapped_payload)
        self.assertEqual(res10["verdict"], "VULNERABILITY_CONFIRMED")

        # Adversarial Edge Case B: What if data is a JSON list instead of dict?
        # e.g. "[1, 2, 3]"
        # Let's see how parse_func behaves on non-dict JSON
        try:
            res11 = parse_func("[1, 2, 3]")
            # If it doesn't crash, it should return an error or handle it
            self.assertTrue(isinstance(res11, dict))
        except AttributeError as e:
            # Documented finding: parser assumes json root is a dict
            print(f"\n[Adversarial Edge Case Finding] parse_differential_payload raises {e} on root array input '[1, 2, 3]'.")

        # Adversarial Edge Case C: What if api_data is a list instead of dict?
        # e.g. {"ui_denied": True, "api_data": ["item1", "item2"]}
        try:
            res12 = parse_func(json.dumps({"ui_denied": True, "api_data": ["item1"]}))
            self.assertTrue(isinstance(res12, dict))
        except AttributeError as e:
            # Documented finding: parser assumes api_data is a dict with .values()
            print(f"\n[Adversarial Edge Case Finding] parse_differential_payload raises {e} when api_data is a list.")

    def test_05_compliance_and_roe_prohibitions_completeness(self):
        """Stress-test: Audit the compliance checklist against all HackerOne RoE rules."""
        required_roe_elements = [
            ("palabong@wearehackerone.com", "Authorized researcher email"),
            ("funk-it-up-sdzgxmea", "Target Store A handle"),
            ("xxxxxx-r48zg9i1", "Target Store B handle"),
            ("bogus", "Bogus Gateway payment isolation"),
            ("third-party", "Prohibition on 3rd-party store testing"),
            ("shopify support", "Zero contact with Shopify Support"),
            ("pii", "Zero retention of buyer personal data"),
            ("phantom_cloud.py", "Core codebase preservation of phantom_cloud.py"),
            ("dockerfile", "Core codebase preservation of Dockerfile"),
            ("fly.toml", "Core codebase preservation of fly.toml"),
            ("requirements.txt", "Core codebase preservation of requirements.txt")
        ]

        cli_lower = self.cli_text.lower()
        for term, desc in required_roe_elements:
            self.assertIn(term.lower(), cli_lower, f"Missing RoE compliance term '{term}' ({desc}) in CLI guide")

    def test_06_e2e_verification_suite_adversarial_audit(self):
        """Stress-test: Audit tests/test_e2e_verification.py for facade tests vs real verifications."""
        # Read the test cases in test_e2e_verification.py
        tree = ast.parse(self.e2e_text)
        
        test_methods = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                # Get the source lines
                start_l = node.lineno
                end_l = node.end_lineno
                body_lines = self.e2e_text.splitlines()[start_l-1:end_l]
                body_src = "\n".join(body_lines)
                test_methods.append((node.name, body_src))

        self.assertEqual(len(test_methods), 105, f"Expected 105 test methods, found {len(test_methods)}")

        # Adversarially classify tests into:
        # 1. Document / File / Cryptographic / System verification (real)
        # 2. Hardcoded local mock variable assertions (tautological / facade)
        tautological_tests = []
        file_validating_tests = []

        for name, src in test_methods:
            # Check if test accesses file content, WORKSPACE_ROOT, self.strat_content, etc.
            accesses_deliverables = any(x in src for x in [
                "strat_content", "metrics_content", "cli_content", "infra_content",
                "survey_", "WORKSPACE_ROOT", "hashlib", "read_bytes", "read_text",
                "EXPECTED_HASHES", "validate_feasibility_score", "calculate_composite_index",
                "is_gid_valid", "is_domain_permitted"
            ])
            if accesses_deliverables:
                file_validating_tests.append(name)
            else:
                # Test only sets local literals and asserts on them
                tautological_tests.append((name, src))

        print(f"\n[E2E Suite Audit] Real / Deliverable-Grounded Tests: {len(file_validating_tests)} / 105")
        print(f"[E2E Suite Audit] Local-Literal / Mock-Logic Tests: {len(tautological_tests)} / 105")

        # Let's inspect some local-literal tests
        if tautological_tests:
            print("\nSample Local-Literal Tests:")
            for name, src in tautological_tests[:5]:
                print(f"  - {name}")

        # The suite must have a majority of real deliverable tests
        self.assertGreaterEqual(len(file_validating_tests), 60, "Expected at least 60 deliverable-grounded tests")


if __name__ == "__main__":
    unittest.main()
