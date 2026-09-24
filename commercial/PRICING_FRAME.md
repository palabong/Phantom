# Phantom Cloud Pricing Framework

This document outlines the pricing model and cost boundaries for the Phantom Cloud platform.

## 1. Commercial Pricing Model
The pricing of the Phantom Cloud platform consists of two primary operational components:

### A. Fixed-Fee Pilot
* A flat operational setup fee covering infrastructure provisioning (Xvfb, isolated Starlette backend, initial Chrome configuration), dedicated resources, and initial operational support.
* Includes up to the standard limit of 10,000 monthly or pilot calls.

### B. Optional Call Overage
* Volume-based pay-as-you-go model for calls exceeding the allotted pilot allocation.
* Calculated based on combined counts of the `navigate` and `get_snapshot` tool calls.

---

## 2. Price Ranges
Specific commercial rates, tiers, and limits are **to be defined against the VDP/BB strategic document ranges**. To maintain alignment with internal strategic projections, absolute prices, minimum commitments, and overage rates are governed strictly by the corresponding strategic document ranges and are finalized during commercial contract negotiations.

---

## 3. Scope Exclusions (What is Not Included in the Base Pilot Price)
To maintain infrastructure stability and focus during the pilot phase, the following features are strictly excluded from the standard pricing structure:

* **Multi-Tenant Deployment**: All sessions share the baseline single-tenant server state with concurrency limits (`MAX_CONCURRENT_SESSIONS=1`). Multi-tenant orchestration and isolated session pools are subject to enterprise add-on pricing.
* **Guaranteed SLA**: High availability guarantees (such as 99.9% uptime SLAs) are not active. System availability is provided on a best-effort basis during the pilot.
* **Guaranteed Bypass of Specific WAF Solutions**: While Phantom Cloud employs advanced anti-fingerprinting and behavioral emulation, we do not provide a contractually guaranteed bypass rate or SLA for any specific WAF (e.g., Cloudflare, Akamai, Imperva, etc.). Anti-detection capability is provided on an iterative, best-effort basis.
* **Dedicated Custom Proxies / Residential IP Rotations**: Basic IP transport is provided, but custom geo-location residential proxies, dedicated IP blocks, or customer-owned proxy integrations are not included under the standard pricing.
