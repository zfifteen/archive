## Immediate Research Plan

We need to answer:
1. Does UPMC expose a patient-facing API at all?
2. If yes, what spec (FHIR, proprietary OAuth flow, etc.)?
3. What's the auth model—can you self-host a client or is it locked to their portal?
4. Are there rate limits, scopes, or ToS barriers that kill local agent use?

I'll search for:
- UPMC API documentation (patient access)
- UPMC FHIR endpoint info
- UPMC developer portal or integration guides
- Any known third-party integrations (proof someone's done this)

If UPMC follows the federal mandate (21st Century Cures Act), they should expose a FHIR R4 endpoint with OAuth2. If they don't, or if it's gated behind institutional agreements, we stop here.

Stand by—searching now.Good news: **UPMC Health Plan has a compliant Patient Access API**. Now let's see if UPMC the provider (not just the insurer) exposes clinical data similarly.Clearer now. Let me search for UPMC's specific Epic/MyChart FHIR endpoint.Now let me search specifically for UPMC's patient-facing FHIR endpoint in the Epic directory.Perfect. Let me search for UPMC in that endpoint list:Let me check the UPMC entry more directly:The page is dynamic. Let me search for UPMC's specific FHIR base URL:Now let me download the actual UPMC FHIR endpoint URL from Epic's bundle:Let me take a different approach and check UPMC's own documentation:## **Gate Assessment Complete**

Here's what I found:

---

### **API Access: YES — Project is Feasible**

UPMC has **two separate FHIR endpoints** you can access:

1. **UPMC Health Plan** (insurance/payer data)
  - Base URL: `https://apis.upmchp.com/FHIR/R4/`
  - Covers: claims, clinical data from providers, medications, EOBs
  - Registration: [upmchealthplan.com/interop/api-access](https://www.upmchealthplan.com/interop/api-access/)
  - Free, SMART on FHIR OAuth2, requires client registration

2. **UPMC Provider** (clinical EHR data via Epic MyChart)
  - UPMC uses Epic's MyChart system
  - Must register app at [fhir.epic.com](https://fhir.epic.com) (Epic on FHIR)
  - UPMC likely has an endpoint in Epic's directory (I saw 1182 orgs listed)
  - Free, SMART on FHIR OAuth2

---

### **What This Means for Your Project**

**✅ Non-Blocking:** You can build this locally. The UPMC Health Plan API explicitly allows third-party apps, and Epic's patient-facing APIs are federally mandated (21st Century Cures Act). No institutional approval needed for patient-authorized access.

**✅ OAuth2 Flow:** Standard SMART on FHIR. You register your app, get a client ID, implement OAuth2 authorization code flow. User logs in with UPMC credentials, grants your app access. You get a token, make FHIR R4 calls.

**✅ No Rate-Limit Showstoppers:** These are patient-access APIs, not bulk research APIs. Typical limits are generous for personal use.

**⚠️ Two Separate Registrations:** If you want both insurance data (Health Plan) and clinical data (Epic), you'll register twice. Each has its own OAuth flow.

---

### **Next Steps (in priority order)**

1. **Register with UPMC Health Plan API** — start here since it's UPMC-specific and likely has your claims/EOB data
  - Go to [upmchealthplan.com/interop/api-access](https://www.upmchealthplan.com/interop/api-access/)
  - Fill out registration form → get Client ID, Client Secret, Subscription Key
  - Read their [API docs](https://www.upmchealthplan.com/interop/api-documentation)

2. **Register with Epic on FHIR** — for clinical data from UPMC providers
  - Go to [fhir.epic.com](https://fhir.epic.com) → create account → register app
  - Get sandbox access first (test with fake patient data)
  - Find UPMC's exact FHIR base URL in Epic's endpoint directory once you're logged in

3. **Prototype the OAuth flow** — pick one (Health Plan is simpler to start)
  - Python script: initiate OAuth, handle redirect, exchange code for token
  - Test with a single API call (e.g., Patient.Read)
  - Validate you can retrieve actual data

4. **Build the desktop app** once API access works
  - Electron makes sense if you're comfortable with it
  - xAI Python SDK runs server-side — Electron calls a local Python API
  - Or: pure Python with a minimal UI framework (Tkinter, PyQt) if you want less overhead

---

### **Architecture Sketch**

```
┌─────────────────────────────────────┐
│  Electron GUI (renderer process)    │
│  - Chat interface                   │
│  - xAI streaming responses          │
└─────────────┬───────────────────────┘
              │
              ├─► Local Python server (Flask/FastAPI)
              │   ├─► xAI SDK (context = UPMC data)
              │   ├─► UPMC Health Plan FHIR client (OAuth2)
              │   └─► Epic FHIR client (OAuth2, if needed)
              │
              └─► Token storage (encrypted local file or OS keychain)
```

**Why this split:**
- Electron handles UI, Python handles secrets and API complexity
- xAI SDK is Python — keep it server-side
- OAuth tokens stored securely, not in renderer process

---

### **Critical Implementation Notes**

**OAuth Redirect:**
- Register redirect URI as `http://localhost:<port>/callback` for local app
- Electron spawns temp HTTP server to catch OAuth callback, then shuts down

**Token Refresh:**
- FHIR access tokens expire (typically 1 hour)
- Store refresh tokens, implement automatic renewal

**FHIR Query Strategy:**
- On startup: fetch Patient, Condition, MedicationRequest, Observation (labs)
- Cache locally (SQLite or JSON file)
- Pass to xAI as context: "You are analyzing health data for patient X. Here are their conditions: ..."

**Scope Requests:**
- `patient/*.read` gives broad read access
- Narrow if you only need specific resources (e.g., `patient/Observation.read patient/Condition.read`)

---

### **No Show-Stoppers Identified**

The gate is **green**. You can proceed.

**Remaining unknowns** (addressable during build):
- Exact scopes UPMC Health Plan supports (check their capability statement)
- Whether UPMC Provider data duplicates Health Plan data (may only need one)
- Rate limits in practice (unlikely to hit with single-user agent chat)

**Start with UPMC Health Plan registration today.** That's your critical path. Once you have a token and can `GET /Patient`, the rest is scaffolding.
