# Phantom Cloud Rules of Engagement and Scope of Use

This document establishes the binding operational rules, boundaries, and legal responsibilities governing the use of the Phantom Cloud platform.

## 1. invitational and Continuous Security Context
Phantom Cloud is built exclusively for authorized, invitational, and continuous security evaluation, vulnerability research, and automated data validation. It must only be used in a manner consistent with legitimate security operations and explicit customer mandate.

## 2. Strictly Prohibited Actions (Zero-Tolerance Policy)
Any breach of the following restrictions will result in immediate suspension of access and termination of the pilot program:

* **No Targets Outside the Pre-Approved Allowlist**:
  * Users are strictly prohibited from navigating to or querying any domains, IP addresses, or subdomains not explicitly declared and verified on the target allowlist.
* **No Credential Stuffing or Authentication Bruteforcing**:
  * Phantom Cloud tools (`navigate`, etc.) must not be used to perform automated login brute-forcing, password spraying, or credential stuffing operations on any target systems.
* **No Destructive Actions or DDoS Simulation**:
  * Do not initiate actions designed to degrade, disable, or exhaust target resources. High-volume stress testing, denial-of-service simulations, and payload execution that modifies remote database/filesystem states are strictly prohibited.
* **No Evasion of Legal Hold or Abuse Mechanisms**:
  * Do not attempt to bypass target site access bans, CAPTCHA blocks, or abuse indicators on systems where explicit legal, administrative, or operational blocks have been placed on the customer or customer's infrastructure.

## 3. Allocation of Responsibility for Proxies & Compliance
To ensure lawful and ethical operations:

### A. IP Transit & Proxy Compliance
* **IP Reputation & Sourcing**: Phantom Cloud uses baseline cloud and proxy routing. The selection and use of specific proxy channels or rotating IPs is governed by network compliance rules.
* **Compliance with Local and International Laws**: The customer is solely responsible for ensuring that all data extraction, site navigation, and snapshot gathering processes are fully compliant with:
  * Local jurisdictions where targets are hosted.
  * Terms of Service (ToS) or explicit data extraction policies of target endpoints.
  * Data privacy regulations (e.g., GDPR, CCPA) regarding any personal data captured in snapshots.

### B. Customer Liability & Indemnification
* The customer warrants that they possess full legal rights, permissions, and licenses to access and interact with the target list.
* Phantom Cloud, its developers, and providers assume no responsibility for target-side blocks, legal notices, or actions arising from unauthorised or abusive use of the platform.
