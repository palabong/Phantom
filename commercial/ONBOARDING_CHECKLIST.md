# Phantom Cloud Customer Onboarding Checklist

This checklist defines the step-by-step procedures to configure, test, and activate a customer's Phantom Cloud pilot session.

## 1. Step-by-Step Onboarding Process

### Step 1: Token Issuance
* **Action**: Generate and issue a dedicated Unkey validation token prefixed with `ph_live_` for the customer.
* **Responsible Party**: Phantom Cloud Operations Team.
* **Security Note**: Deliver the token securely using a one-time secret link or encrypted channel. Never log or share the plain token in public channels.

### Step 2: Establish the SSE Server Endpoint
* **Action**: Provide the customer with the secure Server-Sent Events (SSE) gateway URLs:
  * **SSE Connect (GET)**: `https://phantom-cloud-engine.fly.dev/sse?token=<ph_live_...>`
  * **MCP Message Channel (POST)**: `https://phantom-cloud-engine.fly.dev/messages/t/<ph_live_...>?session_id=<unique_uuid>`
* **Responsible Party**: Customer Integration Engineers.

### Step 3: Conduct Smoke Tests
* **Action**: Have the customer perform a basic verification test sequence using an MCP client (such as Claude Desktop or the MCP Inspector):
  1. **Navigate**: Call `navigate(url="https://bot.sannysoft.com")` or another pre-approved test target.
  2. **Snapshot**: Call `get_snapshot()` to ensure the AOM parser returns the correct text-based snapshot successfully.
* **Responsible Party**: Joint (Customer + Phantom Support).

### Step 4: Define Escalation & Support Channels
* **Action**: Share contacts and configure notifications.
  * **Severity 1 (Service Down)**: Contact via dedicated emergency Slack/Teams channel.
  * **Severity 2 (Degraded Performance / Bypass Issues)**: Email support loop at `support@phantom-cloud.io`.
* **Responsible Party**: Phantom Cloud Support Coordinator.

---

## 2. Go-Live Message Template
Once the smoke tests pass, send the following kickoff message to the customer's technical contacts.

```text
Subject: Welcome to Phantom Cloud - Your Pilot Session is Live!

Hello [Customer Team Name],

We are excited to inform you that your Phantom Cloud pilot instance is fully provisioned, verified, and ready for use! 

Below are your onboarding details and configuration parameters to help you get started:

1. Connection Parameters:
   - SSE Connection Endpoint: 
     https://phantom-cloud-engine.fly.dev/sse?token=YOUR_PH_LIVE_TOKEN
   - Message Channel Endpoint: 
     https://phantom-cloud-engine.fly.dev/messages/t/YOUR_PH_LIVE_TOKEN

2. Pilot Scope & Constraints:
   - Concurrency Limit: Max 1 active session (MAX_CONCURRENT_SESSIONS=1).
   - Scoped Tools: 'navigate' and 'get_snapshot'.
   - Rules of Engagement: Ensure all tested domains are listed on your pre-approved allowlist.

3. Recommended Smoke Test (via MCP Client):
   - call 'navigate' with target 'https://bot.sannysoft.com'
   - call 'get_snapshot'
   - verify that you receive the text-based AOM snapshot.

4. Support & Escalations:
   - Slack Support Channel: #[customer]-phantom-pilot
   - General Support Loop: support@phantom-cloud.io

If you have any questions or require immediate support, please ping us directly on the Slack channel. Happy testing!

Best regards,
The Phantom Cloud Operations Team
```
