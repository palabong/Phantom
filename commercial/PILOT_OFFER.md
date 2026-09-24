# Phantom Cloud Pilot Offer

This document outlines the scope, parameters, and operational framework for the Phantom Cloud pilot program.

## 1. Pilot Scope
The pilot program provides access to the Phantom Cloud headless browser automation engine, specifically scoped to evaluate its browser stealth and WAF bypass capabilities.

### Included Tools (Standard Capabilities)
* **`navigate`**: Direct browser navigation to target URLs using anti-detection strategies.
* **`get_snapshot`**: Extraction of the text-based Accessibility Object Model (AOM) representation of the active page. Supports dual modes:
  * `"html"` (default): Custom lightweight HTMLParser layout with stable `e*` references.
  * `"ax"`: Native CDP Accessibility Tree layout with stable `ax*` references.
  * *Note*: Element references (`e*` / `ax*`) are valid and resolvable only for the last executing `get_snapshot` mode used.
* **`click`**: Simulates a high-fidelity mouse click on elements (via `e*`/`ax*` references or CSS selectors) or specific coordinates.
* **`type`**: Types text character-by-character into inputs with optional clearing.
* **`evaluate`**: Evaluates a raw JavaScript expression on the page and returns the result.
* **`wait`**: Performs explicit wait on a CSS selector and/or a static delay in milliseconds.

*The interaction tools are fully in scope for the pilot, but are strictly bound by the Rules of Engagement (allowlist-only targets, no credential stuffing, and no destructive actions).*

### Excluded Capabilities & Limitations
* Fully-interactive automated sessions beyond the pre-configured browser-level anti-detection.
* Multi-user isolated environments (the pilot operates under a single-tenant queue model).
* Schedulers, custom automation script development, or API integrations outside the standard Model Context Protocol (MCP) spec.
* Custom visual rendering engines or video/stream extraction.
* Multi-tenant deployments, high-availability 99.9% SLAs, and custom residential proxy blocks.
* Guaranteed bypass of specific named Web Application Firewalls (WAFs) or solutions for specific WebGL/SwiftShader hardware residuals (provided on an iterative, best-effort basis).

## 2. Target Coverage & Allowlist
* The pilot is restricted to **agreed target domains** specified prior to kickoff.
* Targets must be non-destructive public web endpoints owned, operated, or explicitly authorized by the customer for evaluation.
* Any target outside the agreed list will be blocked at the network or routing level.

## 3. Measurable Acceptance Criteria
The success of the pilot will be measured against the following empirical engineering metrics:

| Metric Category | Metric Name | Target Threshold | Measurement Basis |
| :--- | :--- | :--- | :--- |
| **Availability** | Successful Navigate % | $\ge 95\%$ | Proportion of `navigate` requests resulting in successful connection / load (excluding target-side downtime). |
| **Performance** | p50 Snapshot Latency | $< 8.0 \text{ seconds}$ | Median duration between `get_snapshot` call and AOM text representation delivery. |
| **Stability** | Zero-Crash Session Rate | $100\%$ | No application crashes or resource starvation events requiring manual server/container restart. |
| **Bypass Efficacy** | Anti-Detection Reliability | Subjective / Empirical | Ability to load target pages under steady security postures (to be checked via target rendering/snapshots). |

## 4. Pilot Duration & Volume
* **Duration**: Fourteen (14) calendar days from the date of token activation.
* **Indicative Call Volume**: Up to 10,000 total combined calls of `navigate` and `get_snapshot` during the 14-day evaluation window.
* **Concurrency**: Restricted to a maximum of one (1) active session at any given time (`MAX_CONCURRENT_SESSIONS=1`).

## 5. Customer Dependencies & Requirements
To execute the pilot, the customer must provide and configure:
* **Unkey Auth Token**: Access requires the customer to pass the valid `ph_live_` token issued for the pilot.
* **Target Allowlist**: A finalized list of target domains/URLs to be queried.
* **Support Channel**: Designation of a primary engineering contact and a Slack/Teams or email communication loop for status updates.
