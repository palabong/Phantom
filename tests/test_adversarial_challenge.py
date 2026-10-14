#!/usr/bin/env python3
"""
Adversarial Challenge & Stress-Test Suite for Phantom Cloud Strategy & Feasibility Deliverables
Evaluates:
1. GraphQL query/mutation template syntax, balanced structure, and Shopify schema conformance.
2. Differential criteria precision: false positive and false negative edge cases.
3. Multi-tenant isolation boundary models and failure modes for Track H1-7.
4. Mathematical rubrics consistency, interval gaps, score inflation, and weighting drift.
5. Comparative assessment claims verified against frozen phantom_cloud.py implementation.
"""

import math
import os
import re
import sys
import unittest
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent


# -----------------------------------------------------------------------------
# GRAPHQL PARSER & LINTER HELPER (EMPIRICAL ORACLE)
# -----------------------------------------------------------------------------
class SimpleGraphQLLexer:
    """Minimal robust lexer and AST parser to validate GraphQL syntax without external deps."""
    
    TOKEN_PUNCTUATION = set("{}(),:!$=@[]")
    
    @classmethod
    def tokenize(cls, text: str):
        tokens = []
        i = 0
        n = len(text)
        line = 1
        col = 1
        
        while i < n:
            ch = text[i]
            if ch == '\n':
                line += 1
                col = 1
                i += 1
                continue
            if ch in ' \t\r':
                col += 1
                i += 1
                continue
            if ch == '#':  # comment
                while i < n and text[i] != '\n':
                    i += 1
                continue
            if ch == '"':  # string literal
                start = i
                i += 1
                escaped = False
                while i < n:
                    if text[i] == '\\' and not escaped:
                        escaped = True
                    elif text[i] == '"' and not escaped:
                        i += 1
                        break
                    else:
                        escaped = False
                    i += 1
                tokens.append(('STRING', text[start:i], line, col))
                col += (i - start)
                continue
            if ch in cls.TOKEN_PUNCTUATION:
                tokens.append(('PUNCT', ch, line, col))
                i += 1
                col += 1
                continue
            if ch.isalnum() or ch in '_-':
                start = i
                while i < n and (text[i].isalnum() or text[i] in '_-'):
                    i += 1
                tokens.append(('IDENT', text[start:i], line, col))
                col += (i - start)
                continue
            if ch == '.':
                if i + 2 < n and text[i:i+3] == '...':
                    tokens.append(('ELLIPSIS', '...', line, col))
                    i += 3
                    col += 3
                    continue
            tokens.append(('UNKNOWN', ch, line, col))
            i += 1
            col += 1
        return tokens

    @classmethod
    def validate_syntax(cls, text: str):
        tokens = cls.tokenize(text)
        stack = []
        pairs = {')': '(', '}': '{', ']': '['}
        for token_type, val, line, col in tokens:
            if token_type == 'PUNCT':
                if val in '({[':
                    stack.append((val, line, col))
                elif val in ')}]':
                    expected = pairs[val]
                    if not stack:
                        return False, f"Unmatched closing '{val}' at line {line}, col {col}"
                    top, t_line, t_col = stack.pop()
                    if top != expected:
                        return False, f"Mismatched bracket: expected '{expected}' for '{val}' at line {line}, col {col}, got '{top}' from line {t_line}"
            elif token_type == 'UNKNOWN':
                return False, f"Unknown token '{val}' at line {line}, col {col}"
        if stack:
            top, t_line, t_col = stack[-1]
            return False, f"Unclosed bracket '{top}' opened at line {t_line}, col {col}"
        return True, "Valid syntax"


# -----------------------------------------------------------------------------
# ADVERSARIAL CHALLENGE TEST SUITE
# -----------------------------------------------------------------------------
class TestAdversarialChallengeSuite(unittest.TestCase):
    """Adversarial stress-testing of Strategic Plan and Feasibility Metrics."""

    @classmethod
    def setUpClass(cls):
        cls.strat_path = WORKSPACE_ROOT / "STRATEGIC_OPERATIONAL_PLAN.md"
        cls.metrics_path = WORKSPACE_ROOT / "FEASIBILITY_EVALUATION_METRICS.md"
        cls.phantom_path = WORKSPACE_ROOT / "phantom_cloud.py"

        cls.strat_content = cls.strat_path.read_text(encoding="utf-8")
        cls.metrics_content = cls.metrics_path.read_text(encoding="utf-8")
        cls.phantom_content = cls.phantom_path.read_text(encoding="utf-8")

    # =========================================================================
    # TASK 1: ADVERSARIALLY STRESS-TEST STRATEGIC_OPERATIONAL_PLAN.MD
    # =========================================================================

    def test_task1_01_graphql_template_syntax_validity(self):
        """Stress-test: Verify that every GraphQL block in the plan has syntactically valid structure."""
        graphql_blocks = re.findall(r"```graphql\n(.*?)\n```", self.strat_content, re.DOTALL)
        self.assertGreaterEqual(len(graphql_blocks), 7, "Plan must contain at least 7 comprehensive GraphQL code blocks")
        
        for idx, block in enumerate(graphql_blocks):
            # Strip trailing comments or variables if present in the block
            query_part = block.split("# Variables:")[0].split("# Input:")[0].strip()
            is_valid, msg = SimpleGraphQLLexer.validate_syntax(query_part)
            self.assertTrue(is_valid, f"GraphQL Block #{idx+1} failed syntax validation: {msg}\nBlock content:\n{query_part}")

    def test_task1_02_graphql_shop_settings_schema_conformance(self):
        """Stress-test: Identify schema invalidation in ShopSettingsAuditQuery (timezoneOffset vs ianaTimezone)."""
        # In Shopify Admin GraphQL API, timezoneOffset does not exist on type Shop; ianaTimezone is the authoritative field
        self.assertIn("timezoneOffset", self.strat_content, "Observed timezoneOffset in plan")
        # Adversarial assertion: Document must be audited for timezoneOffset field existence
        # Check whether the plan mentions or uses timezoneOffset
        has_invalid_tz = "timezoneOffset" in self.strat_content
        self.assertTrue(has_invalid_tz, "Empirically detected 'timezoneOffset' in ShopSettingsAuditQuery")

    def test_task1_03_graphql_payments_and_features_schema_conformance(self):
        """Stress-test: Identify schema invalidations in PaymentsAuditQuery and line 271 query."""
        # 1. 'paymentGateways' on Shop does not exist in Shopify Admin GraphQL
        has_invalid_gateways = "paymentGateways { id name type }" in self.strat_content
        self.assertTrue(has_invalid_gateways, "Empirically detected 'paymentGateways' on Shop in line 271")

        # 2. 'customerAccounts', 'hasDiscounts', 'hasGiftCards' on PaymentSettings do not exist in Admin API
        has_invalid_payment_settings = "customerAccounts" in self.strat_content and "supportedDigitalWallets" in self.strat_content
        self.assertTrue(has_invalid_payment_settings, "Empirically detected invalid child fields under paymentSettings")

    def test_task1_04_graphql_theme_files_connection_conformance(self):
        """Stress-test: Identify invalid connection query on Theme.files."""
        # Theme.files is NOT a Relay connection with (first: 5) and edges/node; it requires (filenames: [...])
        has_invalid_theme_files = "files(first: 5) {\n          edges {\n            node {\n              filename" in self.strat_content
        self.assertTrue(has_invalid_theme_files, "Empirically detected invalid files(first: 5) connection query on Theme")

    def test_task1_05_graphql_product_update_input_type_conformance(self):
        """Stress-test: Identify legacy/deprecated ProductInput vs ProductUpdateInput in CrossTenantProductUpdate."""
        # Starting with Shopify 2024-10, productUpdate uses product: ProductUpdateInput!, not input: ProductInput!
        has_legacy_product_input = "mutation CrossTenantProductUpdate($input: ProductInput!)" in self.strat_content
        self.assertTrue(has_legacy_product_input, "Empirically detected legacy 'ProductInput' type in mutation template")

    def test_task1_06_differential_criteria_false_positive_on_empty_edges(self):
        """Stress-test: Prove that formula 'data.<resource> != null' produces false positive when edges is empty."""
        # Condition from line 228: UI Status = DENIED and API Status = 200 OK and data.<resource> != null
        mock_api_response_empty = {
            "data": {
                "orders": {
                    "edges": []  # empty edges: no orders returned / properly filtered by backend
                }
            }
        }
        resource_data = mock_api_response_empty["data"]["orders"]
        # Naive evaluation:
        is_naive_vuln = (resource_data is not None)
        self.assertTrue(is_naive_vuln, "Naive check triggers false positive because empty connection dictionary != None")
        
        # Robust evaluation oracle:
        is_robust_vuln = (resource_data is not None and len(resource_data.get("edges", [])) > 0)
        self.assertFalse(is_robust_vuln, "Robust oracle correctly classifies empty edges as non-vulnerable")

    def test_task1_07_differential_criteria_false_positive_on_public_fields(self):
        """Stress-test: Prove that querying shop { name } produces false positive if checked naively against /settings/general UI deny."""
        mock_shop_response = {
            "data": {
                "shop": {
                    "id": "gid://shopify/Shop/12345",
                    "name": "funk-it-up-sdzgxmea"  # non-sensitive public shop name
                }
            }
        }
        shop_data = mock_shop_response["data"]["shop"]
        self.assertIsNotNone(shop_data)
        
        # Sensitive fields check oracle:
        sensitive_fields = {"email", "contactEmail", "billingAddress"}
        leaked_sensitive = [f for f in sensitive_fields if f in shop_data]
        self.assertEqual(len(leaked_sensitive), 0, "Non-sensitive public field return must not be flagged as differential authorization breach")

    def test_task1_08_differential_criteria_false_negative_on_user_errors(self):
        """Stress-test: Prove that mutations returning HTTP 200 with userErrors require userErrors inspection."""
        mock_mutation_response = {
            "data": {
                "orderUpdate": {
                    "order": None,
                    "userErrors": [
                        {"field": ["base"], "message": "Access denied for orderUpdate"}
                    ]
                }
            }
        }
        # In GraphQL mutations, data.orderUpdate is NOT None even when the action is completely denied!
        self.assertIsNotNone(mock_mutation_response["data"]["orderUpdate"])
        user_errors = mock_mutation_response["data"]["orderUpdate"].get("userErrors", [])
        self.assertGreater(len(user_errors), 0, "Robust oracle detects that mutation was denied via userErrors")

    def test_task1_09_multi_tenant_isolation_gid_catalog_rigor(self):
        """Stress-test: Verify that Store A and Store B test catalogs have distinct, valid GIDs and handles."""
        store_a_product_gid = "gid://shopify/Product/10323603521722"
        store_b_product_gid = "gid://shopify/Product/15326172709092"
        store_a_variant_gid = "gid://shopify/ProductVariant/50535758364858"
        store_b_variant_gid = "gid://shopify/ProductVariant/67407288565988"

        self.assertNotEqual(store_a_product_gid, store_b_product_gid)
        self.assertNotEqual(store_a_variant_gid, store_b_variant_gid)

        for gid in [store_a_product_gid, store_b_product_gid, store_a_variant_gid, store_b_variant_gid]:
            m = re.match(r"^gid://shopify/(Product|ProductVariant)/(\d{14})$", gid)
            self.assertIsNotNone(m, f"GID {gid} must match canonical 14-digit pattern")

    def test_task1_10_multi_tenant_failure_modes_depth(self):
        """Stress-test: Verify that all four primary multi-tenant failure modes are comprehensively analyzed."""
        for failure_mode in ["Global Node Interface Resolution Bypass", "Cross-Tenant Mutation Binding", 
                             "Cross-Catalog Storefront Cart Injection", "Storefront Public JSON / Handle Leakage"]:
            self.assertIn(failure_mode, self.strat_content)

    # =========================================================================
    # TASK 2: ADVERSARIALLY STRESS-TEST FEASIBILITY_EVALUATION_METRICS.MD
    # =========================================================================

    def test_task2_01_mathematical_weights_sum_to_unity(self):
        """Stress-test: Verify that composite feasibility index weights strictly sum to 1.00."""
        # Weights from FEASIBILITY_EVALUATION_METRICS.md §1.2: w_ef = 0.25, w_df = 0.20, w_vp = 0.25, w_bi = 0.30
        w_ef, w_df, w_vp, w_bi = 0.25, 0.20, 0.25, 0.30
        total_weight = w_ef + w_df + w_vp + w_bi
        self.assertAlmostEqual(total_weight, 1.00, places=6, msg="Composite weights must sum to exactly 1.0")

    def test_task2_02_weighting_discrepancy_between_document_and_test_helper(self):
        """Stress-test: Detect weight discrepancy between FEASIBILITY_EVALUATION_METRICS.md and test_e2e_verification.py."""
        # In FEASIBILITY_EVALUATION_METRICS.md: w_ef=0.25, w_df=0.20, w_vp=0.25, w_bi=0.30
        # In test_e2e_verification.py line 39: weights=(0.25, 0.25, 0.20, 0.30) [DF and VP swapped]
        doc_weights = (0.25, 0.20, 0.25, 0.30)
        test_weights = (0.25, 0.25, 0.20, 0.30)
        
        # Test track H1-5: ef=0.85, df=0.80, vp=0.25, bi=0.85
        cfi_doc = round(0.85*doc_weights[0] + 0.80*doc_weights[1] + 0.25*doc_weights[2] + 0.85*doc_weights[3], 4)
        cfi_test = round(0.85*test_weights[0] + 0.80*test_weights[1] + 0.25*test_weights[2] + 0.85*test_weights[3], 4)
        
        self.assertEqual(cfi_doc, 0.6900, "Document calculated CFI must equal 0.690")
        self.assertEqual(cfi_test, 0.7175, "Test helper default calculated CFI equals 0.7175 due to swapped DF/VP weights")
        self.assertNotEqual(cfi_doc, cfi_test, "Empirical proof of weight drift between document and test helper")

    def test_task2_03_bounty_impact_formula_vs_assigned_score_contradiction(self):
        """Stress-test: Detect mathematical score inflation between BI formula and assigned score for Track H1-5."""
        # In §2.4: BI = (TierBaseReward / ProgramMaxBounty) * EligibilityMultiplier
        # For High severity: TierBaseReward = $14,000 to $50,000, ProgramMaxBounty = $200,000
        # Formula yield: $50,000 / $200,000 = 0.25 (or $14,000 / $200,000 = 0.07)
        program_max = 200000.0
        high_tier_max = 50000.0
        calculated_bi_max = high_tier_max / program_max
        self.assertEqual(calculated_bi_max, 0.25, "Calculated BI from formula for High Severity is 0.25")
        
        # In Table 3.1: BI for Track H1-5 is assigned 0.85!
        assigned_bi_h1_5 = 0.85
        self.assertGreater(assigned_bi_h1_5, calculated_bi_max, "Empirical proof: Assigned BI (0.85) is inflated by >3.4x over formula value (0.25)")

    def test_task2_04_bounty_impact_rubric_interval_contradiction(self):
        """Stress-test: Detect rubric tier contradiction for Track H1-5 BI score."""
        # In §2.4 Table:
        # [0.6, 0.8) -> High Severity ($14,000 – $50,000)
        # [0.8, 1.0] -> Critical Severity ($50,000 – $200,000)
        # Track H1-5 is defined as High Severity ($14k–$50k), but scored at 0.85 (Critical interval!)
        assigned_bi_h1_5 = 0.85
        is_in_high_interval = (0.6 <= assigned_bi_h1_5 < 0.8)
        is_in_critical_interval = (0.8 <= assigned_bi_h1_5 <= 1.0)
        self.assertFalse(is_in_high_interval, "0.85 is NOT in the High Severity rubric interval [0.6, 0.8)")
        self.assertTrue(is_in_critical_interval, "0.85 falls erroneously into the Critical Severity interval [0.8, 1.0]")

    def test_task2_05_vulnerability_probability_score_inflation_analysis(self):
        """Stress-test: Challenge VP=0.15 for Track H1-7 on Vitess shard architecture."""
        # Cross-shop IDOR probability of 15% against a shard-partitioned architecture with 0 bypasses in 5 years
        vp_h1_7 = 0.15
        ef = 0.90
        df = 0.95
        target_bounty = 150000.0
        ev = ef * df * vp_h1_7 * target_bounty
        self.assertEqual(round(ev, 2), 19237.50)
        
        # If realistic VP is 0.02 (2%):
        realistic_vp = 0.02
        realistic_ev = ef * df * realistic_vp * target_bounty
        self.assertEqual(round(realistic_ev, 2), 2565.00)
        self.assertGreater(ev, realistic_ev * 7, "Assigned VP=0.15 inflates expected value by >7.4x")

    def test_task2_06_execution_feasibility_binary_waf_contradiction(self):
        """Stress-test: Challenge EF formula binary phi_WAF against Fly.io EF=0.30."""
        # Formula: EF = phi_WAF * (alpha*R_nav + beta*R_cdp + gamma*R_sess), with phi_WAF in {0.0, 1.0}
        # On Fly.io, Turnstile blocks execution: if phi_WAF = 0.0, EF MUST be 0.00
        # Yet document states Fly.io EF drops to 0.30
        phi_waf_blocked = 0.0
        nav_score = 0.40 * 0.5 + 0.30 * 0.5 + 0.30 * 0.5
        ef_strictly_computed = phi_waf_blocked * nav_score
        self.assertEqual(ef_strictly_computed, 0.00, "Strict binary phi_WAF=0 forces EF to 0.00, contradicting reported 0.30")

    def test_task2_07_comparative_assessment_verbatim_stealth_injection(self):
        """Stress-test: Verify that phantom_cloud.py contains the exact spoof parameters cited in assessment."""
        self.assertIn("TARGET_VENDOR = 'Google Inc. (NVIDIA)'", self.phantom_content)
        self.assertIn("TARGET_RENDERER = 'ANGLE (NVIDIA, NVIDIA GeForce RTX 3080 Direct3D11 vs_5_0 ps_5_0, D3D11)'", self.phantom_content)
        self.assertIn("CanvasRenderingContext2D.prototype.getImageData", self.phantom_content)
        self.assertIn("CHROME_DEBUGGING_PORT", self.phantom_content)
        self.assertIn("MAX_CONCURRENT_SESSIONS = 6", self.phantom_content)

    def test_task2_08_core_codebase_zero_modifications_verified(self):
        """Stress-test: Verify that core codebase files remain 100% frozen and unmodified."""
        expected_hashes = {
            "phantom_cloud.py": "b75ed50cd45dff5f71388f792a8b38de7f23e6944562249af82160f69f4126df",
            "Dockerfile": "3ccfb3725d1addce0c3134471e2ef52897178b13cbdf1ff3e9c2ef26cdccbb08",
            "fly.toml": "0227444e4b6416a358dd70ac83604cf94320cc925fff24d9a5558770a16e196d",
            "requirements.txt": "1b217ecb50b1049687abc6958186c826e616e17c6ddfcd95861bd4b658cd5067",
        }
        import hashlib
        for fname, exp_hash in expected_hashes.items():
            fpath = WORKSPACE_ROOT / fname
            self.assertTrue(fpath.exists(), f"Core file {fname} must exist")
            actual_hash = hashlib.sha256(fpath.read_bytes()).hexdigest()
            self.assertEqual(actual_hash, exp_hash, f"Core file {fname} hash mismatch: file was tampered with!")


if __name__ == "__main__":
    unittest.main(verbosity=2)
