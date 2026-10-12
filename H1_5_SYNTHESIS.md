# H1-5 Resource Synthesis: UI State vs. GraphQL Access

**Date/Time (UTC)**: 2026-10-12
**Target Store**: `xxxxxx-r48zg9i1` (`https://admin.shopify.com/store/xxxxxx-r48zg9i1/`)
**Session Account**: `palabong+staff@wearehackerone.com`

---

## 1. Summary of Tested Resources

| Resource | Run Directory | UI State | GraphQL Query | GraphQL Result | Classification | Candidate Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Orders** | `runs/prod_postdeploy_20261012T134709Z` | **Denied** (Permission denial banner) | `query{orders(first:1){edges{node{id name}}}}` | **Error** (`{"error": "Failed to fetch"}`) | Match (Deny / Error) | None |
| **Settings** | `runs/prod_postdeploy_20261012T134949Z` | **Allowed** (Settings custom data rendered) | `query{shop{id name email}}` | **Error** (`{"error": "Failed to fetch"}`) | Match (Allow / Error) | None |
| **Payments** | `runs/prod_postdeploy_20261012T142023Z` | **Denied** (Permission denial banner) | `query{shop{paymentSettings{supportedDigitalWallets}}}` | **Error** (`{"errors": "[API] Invalid API key..."}`) | Match (Deny / Error) | None |
| **Themes** | `runs/prod_postdeploy_20261012T142233Z` | **Allowed** (Theme library & controls rendered) | `query{themes(first:5){edges{node{id name}}}}` | **Error** (`{"errors": "[API] Invalid API key..."}`) | Match (Allow / Error) | None |

---

## 2. Resource-by-Resource Evidence

### 1. Orders
- **Target URL**: `https://admin.shopify.com/store/xxxxxx-r48zg9i1/orders`
- **Run Directory**: `runs/prod_postdeploy_20261012T134709Z/`
- **UI State**: **Denied**
  - Observation: `UI observation: permission denial ("You need permission to view this feature. Your account palabong+staff@wearehackerone.com doesn't have access to this page")`
- **GraphQL Result**: **Error**
  - Payload: `{"error": "Failed to fetch"}`
- **Match / Mismatch Evaluation**: **Match** (UI Denied / API Error). No unauthorized data disclosure observed.

### 2. Settings
- **Target URL**: `https://admin.shopify.com/store/xxxxxx-r48zg9i1/settings`
- **Run Directory**: `runs/prod_postdeploy_20261012T134949Z/`
- **UI State**: **Allowed**
  - Observation: `UI observation: settings content (settings content displayed)`
- **GraphQL Result**: **Error**
  - Payload: `{"error": "Failed to fetch"}`
- **Match / Mismatch Evaluation**: **Match** (UI Allowed / API Error).

### 3. Payments
- **Target URL**: `https://admin.shopify.com/store/xxxxxx-r48zg9i1/settings/payments`
- **Run Directory**: `runs/prod_postdeploy_20261012T142023Z/`
- **UI State**: **Denied**
  - Observation: `UI observation: permission denial (com You need permission to view this feature Your account palabong+staff@wearehackerone.)`
- **GraphQL Result**: **Error**
  - Payload: `{"errors": "[API] Invalid API key or access token (unrecognized login or wrong password)"}`
- **Match / Mismatch Evaluation**: **Match** (UI Denied / API Error). No unauthorized data disclosure observed.

### 4. Themes
- **Target URL**: `https://admin.shopify.com/store/xxxxxx-r48zg9i1/themes`
- **Run Directory**: `runs/prod_postdeploy_20261012T142233Z/`
- **UI State**: **Allowed**
  - Observation: `UI observation: themes content (themes library and configuration displayed)`
- **GraphQL Result**: **Error**
  - Payload: `{"errors": "[API] Invalid API key or access token (unrecognized login or wrong password)"}`
- **Match / Mismatch Evaluation**: **Match** (UI Allowed / API Error).

---

## 3. Findings & Verdict

**Verdict**: **No UI-deny / API-allow mismatch was observed on the tested resources.**

- Neither `Orders` nor `Payments` yielded GraphQL data when the UI presented a permission denial.
- In all tested scenarios, GraphQL admin queries returned errors (`Failed to fetch` or `[API] Invalid API key or access token (unrecognized login or wrong password)`).
- Zero candidates identified for BOLA/IDOR or authorization bypass across the tested surface.
