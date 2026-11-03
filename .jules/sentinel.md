## 2025-05-18 - [CRITICAL] Fix hardcoded AssemblyAI API key exposure
**Vulnerability:** A real AssemblyAI API key was hardcoded in `voice_agent/web_bridge.py` as a fallback in the `load_api_key` function.
**Learning:** Development testing often introduces temporary hardcoded secrets that are accidentally committed. `voice_agent/assemblyai_stream.py` had the secure implementation (raising an error), but `web_bridge.py` had an insecure fallback.
**Prevention:** Instead of falling back to a hardcoded default key, always fail securely by raising a `ValueError` with instructions to set the environment variable. Ensure secrets scanning tools are in the CI pipeline to catch these before commits.
