## 2025-01-22 - Hardcoded API Key
**Vulnerability:** Hardcoded AssemblyAI API key found in `voice_agent/web_bridge.py`.
**Learning:** Secrets shouldn't be hardcoded into the source code as it exposes them to anyone who has access to the codebase.
**Prevention:** Fallback to raising an error or returning None when the API key is not found in the environment variables.
