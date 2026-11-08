## 2024-05-24 - Hardcoded API Key in Web Bridge Fallback
**Vulnerability:** A hardcoded AssemblyAI API key ("4823582e76784ac4879c11e7e8574334") was found in `voice_agent/web_bridge.py` as a fallback when `ASSEMBLYAI_API_KEY` was missing in the environment or `.env` file.
**Learning:** Hardcoding credentials as fallbacks, even for ease of development, introduces critical security risks if the code is exposed or leaked.
**Prevention:** Remove hardcoded fallbacks and enforce environment variables or secure configuration files, raising errors when required secrets are missing to fail securely.
