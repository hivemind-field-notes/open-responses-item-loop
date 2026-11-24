# Open Responses Item Loop — Companion Code Repository

**HiveMind Solutions · HiveMind Field Notes Vol. 02**  
*One offline Python loop for tools, events, and transcripts*

Every example in this repository runs offline with **Python 3.12 standard library only** — no third-party packages, no external network calls, and no API keys required.

## Requirements

- Linux / POSIX shell
- Python **3.12** (`python3 --version`)
- Standard library only (`json`, `sqlite3`, `urllib.request`, `http.server`, `unittest`, `re`, etc.)

## Repository Layout

```text
.
├── contract.json            # Frozen book contract (case study: pump p3 / 210 kPa, schema, API, 8 drift flags)
└── chapters/
    ├── ch01/                # First pass item loop (run_pump.py)
    ├── ch02/                # Message roles, parts, refusals & assistant phases
    ├── ch03/                # Function declarations, validation & tool results
    ├── ch04/                # Wire fixtures, SSE parser & semantic event reducer (fold.py)
    ├── ch05/                # Bounded offline tool-calling loop (loop.py)
    ├── ch06/                # Canonical SQLite transcript (transcript.py, store_pump.py)
    ├── ch07/                # 2026-04-24 conformance checker, drift report & runnable solutions
    └── ch08/                # Quick reference kit + stdlib HTTP adapter (http_transport.py)
```

## Offline Verification

```bash
# Chapter 6: build pump.sqlite3
(cd chapters/ch06 && rm -f pump.sqlite3 && python3 store_pump.py && python3 next_input.py && python3 rollback.py && python3 pending.py)

# Chapter 7: conformance check (self-test + Chapter 6 database) & drift report
(cd chapters/ch07 && python3 check_db.py && python3 check_db.py ../ch06/pump.sqlite3 && python3 drift.py)

# Chapter 8: reference kit + cross-check on Chapter 6 DB + loopback HTTP test
(cd chapters/ch08 && rm -f reference.db && sh run_ref.sh && python3 transcript.py check ../ch06/pump.sqlite3 && python3 -m unittest test_http_transport.py -v)
```

## Pointing `http_transport.py` at a Real Endpoint

`chapters/ch08/http_transport.py` uses `urllib.request` and works with any Open Responses or OpenAI-compatible HTTP endpoint:

- **Local Ollama:**
  ```bash
  export OPEN_RESPONSES_URL="http://127.0.0.1:11434/v1/responses"
  export OPEN_RESPONSES_MODEL="qwen3:8b"
  ```
- **Local vLLM:**
  ```bash
  export OPEN_RESPONSES_URL="http://127.0.0.1:8000/v1/responses"
  export OPEN_RESPONSES_MODEL="Qwen/Qwen2.5-Coder-7B-Instruct"
  ```
- **OpenRouter:**
  ```bash
  export OPEN_RESPONSES_URL="https://openrouter.ai/api/v1/responses"
  export OPEN_RESPONSES_API_KEY="sk-or-..."
  export OPEN_RESPONSES_MODEL="openai/gpt-4.1-mini"
  ```
