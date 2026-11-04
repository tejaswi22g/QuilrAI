# QuilrAI
# QuilrAI Technical Assessment

**Author:** Tejaswi Gudimetla  
**GitHub:** [tejaswi22g](https://github.com/tejaswi22g)

## 1. Project Overview

This repository contains my solutions to the four tasks in the QuilrAI technical assessment.

The project focuses on building AI infrastructure components that handle tool execution, security, sensitive information, and model requests.

The assessment is divided into four independent tasks:

| Task | What it does |
|---|---|
| Task 1 – MCP Server | Provides customer information and validates refund requests. |
| Task 2 – MCP Security Gateway | Controls who can access regular and administrator tools. |
| Task 3 – PII Guardrail | Detects and hides sensitive information in streaming AI responses. |
| Task 4 – Model Router | Manages token limits and switches to another model when the primary model fails. |

## 2. Technologies Used

- **Python 3.11** – Main programming language.
- **FastAPI** – Building HTTP APIs.
- **MCP SDK** – Implementing Model Context Protocol tools.
- **Pydantic** – Validating request data.
- **HTTPX** – Sending asynchronous HTTP requests.
- **SQLite** – Storing token usage.
- **asyncio** – Handling asynchronous operations.
- **pytest** – Automated testing.

## 3. Project Structure

```text
QuilrAI/
│
├── task1_mcp_server/
│   └── server.py
│
├── task2_mcp_gateway/
│   ├── auth.py
│   ├── gateway.py
│   └── mock_server.py
│
├── task3_llm_guardrail/
│   ├── __init__.py
│   ├── app.py
│   ├── guardrail.py
│   └── mock_provider.py
│
├── task4_model_router/
│   ├── __init__.py
│   ├── app.py
│   ├── database.py
│   ├── router.py
│   └── mock_providers.py
│
├── tests/
│   ├── test_task1.py
│   ├── test_auth.py
│   ├── test_gateway.py
│   ├── test_task3.py
│   ├── test_task4_database.py
│   ├── test_task4_router.py
│   └── stream_check.py
│
├── requirements.txt
├── .gitignore
└── README.md
```

## 4. Task Implementations

### Task 1 – MCP Customer Server

**Goal:** Create an MCP server that provides customer information and handles refund requests.

Two tools are implemented:

**get_customer_record**
- Accepts a customer ID.
- Checks whether the customer ID follows the expected format.
- Returns customer information when a matching record exists.
- Rejects invalid or nonexistent customer IDs.

**trigger_refund**
- Accepts customer ID, refund amount, and reason.
- Checks that the refund amount is greater than zero.
- Requires a reason of at least 10 characters.
- Rejects unexpected input fields.
- Returns a simulated refund confirmation.

**Validation:** Tested valid and invalid customer IDs, negative and zero refund amounts, short reasons, incorrect data types, and unexpected fields.

**Note:** Refunds are simulated. No actual financial transaction takes place.

### Task 2 – MCP Security Gateway

**Goal:** Build a gateway that checks user permissions before forwarding requests to another MCP server.

Two user roles are supported:

- **Admin:** Can access regular tools and administrator tools.
- **Viewer:** Can access regular tools but cannot execute administrator tools.

How it works:

1. The client sends a request with a Bearer token.
2. The gateway validates the token.
3. The gateway identifies the user's role.
4. It checks whether the requested tool requires administrator access.
5. Authorized requests are forwarded to the downstream server.
6. Unauthorized requests are rejected.

Administrator tools use the `admin_` naming prefix.

Unauthorized requests receive JSON-RPC error code `-32001`.

**Validation:** Tested authentication, tool listing, viewer restrictions, and administrator access. Automated tests also verify that blocked requests never reach the downstream server.

**Note:** Mock credentials are used for assessment testing. Production systems should use secure authentication such as signed JWTs.

### Task 3 – LLM Streaming PII Guardrail

**Goal:** Protect sensitive information before it reaches users in an AI-generated response.

The guardrail detects:

- Email addresses.
- Social Security Numbers (SSNs).
- Credit card number candidates.

How it works:

1. A mock LLM provider generates text in small chunks.
2. The guardrail receives each chunk.
3. A rolling buffer handles sensitive information split across chunks.
4. Detected sensitive values are replaced with `[REDACTED]`.
5. Safe text is streamed to the client.

The implementation also uses the Luhn algorithm to validate credit card number candidates.

**Example**

Input:

```text
Contact john@example.com.
SSN: 123-45-6789.
Card: 4111 1111 1111 1111.
```

Output:

```text
Contact [REDACTED].
SSN: [REDACTED].
Card: [REDACTED].
```

**Validation:** Tested email, SSN, and credit card detection, including sensitive values split across multiple chunks and longer responses.

### Task 4 – Rate-Limited Model Router

**Goal:** Manage model requests, enforce tenant token limits, and automatically switch models when the primary provider is unavailable.

**Token Rate Limiting**

- Each tenant has a limit of 50,000 tokens per rolling minute.
- SQLite stores token usage.
- Each tenant's usage is tracked independently.
- Expired records are cleaned up.
- Database transactions protect concurrent requests from exceeding the configured limit.

**Model Routing**

The router initially sends requests to the primary model.

It switches to the secondary model when:

- The primary model returns HTTP 429 (rate limit exceeded).
- The primary model takes longer than 3 seconds to respond.

If the primary model succeeds, the response is returned directly without using the fallback.

**Validation:** Tested primary model success, HTTP 429 fallback, timeout fallback, tenant isolation, token limits, and concurrent requests.

**Note:** Model providers are simulated for this assessment. Token counts are supplied as estimates by the client in this implementation.

## 5. How to Run the Project

### Prerequisites

- Python 3.11 or later.
- Git.
- Node.js and npm (only needed for MCP Inspector).

### Step 1: Clone the repository

```bash
git clone https://github.com/tejaswi22g/QuilrAI.git
cd QuilrAI
```

### Step 2: Create a virtual environment

Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### Step 3: Install dependencies

```powershell
python -m pip install -r requirements.txt
```

## 6. Running Individual Tasks

Each task runs independently.

**Task 1 – MCP Server**

```powershell
python -m task1_mcp_server.server
```

Use MCP Inspector to connect to the server through STDIO.

**Task 2 – Security Gateway**

Start the mock downstream server:

```powershell
python -m uvicorn task2_mcp_gateway.mock_server:app --host 127.0.0.1 --port 8001
```

Start the gateway in another terminal:

```powershell
python -m uvicorn task2_mcp_gateway.gateway:app --host 127.0.0.1 --port 8000
```

Gateway endpoint:

`http://127.0.0.1:8000/mcp`

**Task 3 – PII Guardrail**

```powershell
python -m uvicorn task3_llm_guardrail.app:app --host 127.0.0.1 --port 8002
```

Test the streaming endpoint:

```powershell
curl.exe -N http://127.0.0.1:8002/stream
```

**Task 4 – Model Router**

```powershell
python -m uvicorn task4_model_router.app:app --host 127.0.0.1 --port 8003
```

API endpoint:

`http://127.0.0.1:8003/generate`

Example request:

```json
{
  "prompt": "Explain cloud computing",
  "estimated_tokens": 100,
  "primary_behavior": "success"
}
```

Required header:

```text
X-Tenant-ID: example-tenant
```

Supported primary behaviors:

- `success`
- `rate_limit`
- `timeout`

## 7. Running Automated Tests

Run all tests from the project root:

```powershell
python -m pytest -v
```

### Test Results

All 35 automated tests passed during development.

| Test Suite | Passed |
|---|---:|
| Task 1 – MCP Server | 8 |
| Task 2 – Authentication | 5 |
| Task 2 – Security Gateway | 3 |
| Task 3 – PII Guardrail | 8 |
| Task 4 – SQLite Rate Limiter | 6 |
| Task 4 – Model Router | 5 |
| **Total** | **35** |

## 8. Conclusion

This assessment demonstrates the implementation of four independent AI infrastructure components:

1. An MCP server with strict request validation.
2. A role-based MCP security gateway.
3. A streaming PII detection and redaction mechanism.
4. A tenant-aware model router with SQLite rate limiting and automatic fallback.

The project was developed using Python and asynchronous programming, with automated tests to verify the main functionality and expected behavior.

## Author

**Tejaswi Gudimetla**

GitHub: [https://github.com/tejaswi22g](https://github.com/tejaswi22g)

Project Repository: [https://github.com/tejaswi22g/QuilrAI](https://github.com/tejaswi22g/QuilrAI)