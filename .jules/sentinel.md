## 2024-05-18 - Hardcoded API Key in Fallback Mechanism
**Vulnerability:** A hardcoded AssemblyAI API key (`4823582e76784ac4879c11e7e8574334`) was found in `voice_agent/web_bridge.py` as a fallback return value when the environment variable or `.env` file did not contain the key.
**Learning:** Hardcoding API keys as a fallback mechanism for convenience during development is a critical security vulnerability. It exposes live keys if the repository becomes public or is compromised. We should never hardcode credentials anywhere in the source code.
**Prevention:** Always raise an exception (like `ValueError`) or fail securely if a required secret is missing. Enforce secret scanning in CI/CD pipelines to catch these patterns before they are committed.
