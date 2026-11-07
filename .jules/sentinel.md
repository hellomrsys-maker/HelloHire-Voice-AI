## 2025-05-18 - Hardcoded API Key in WebSocket Bridge
**Vulnerability:** Found a hardcoded AssemblyAI API key used as a fallback in `voice_agent/web_bridge.py`.
**Learning:** This is a common pattern where developers add hardcoded fallbacks for local development or testing convenience, which then accidentally get committed.
**Prevention:** Always require secrets to be passed via environment variables or explicitly loaded config files (e.g., `.env`), and fail fast (e.g., raise ValueError) if they are missing. Avoid fallback keys entirely.
