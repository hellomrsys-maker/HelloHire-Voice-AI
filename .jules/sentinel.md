## 2024-05-18 - [Critical] Hardcoded AssemblyAI API Key in Web Bridge

**Vulnerability:** A hardcoded AssemblyAI API key (`"4823582e76784ac4879c11e7e8574334"`) was found directly in the source code of `voice_agent/web_bridge.py` inside the `load_api_key` function as a fallback return value.

**Learning:** Developers sometimes leave personal or testing API keys in the code during rapid prototyping or hackathons (like the AssemblyAI Voice Agent Hackathon this project was part of) and forget to remove them before committing. This can lead to unauthorized usage and quota exhaustion.

**Prevention:** Never hardcode secrets. Always rely on environment variables (`os.environ`) or secure secret managers. If an API key is strictly required for execution, fail fast by raising a `ValueError` or exiting, rather than providing a fallback value.
