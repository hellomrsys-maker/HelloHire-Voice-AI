# Legacy Training Modules (Archived)

> [!NOTE]
> These modules are preserved strictly for historical reference and backward compatibility with earlier unit tests.
> **DO NOT USE FOR NEW TRAINING WORKFLOWS.**

## Active Training Architecture
All active training is standardized according to Section 13 of `RULEBOOK.md`:
- **Single-Screen JavaScript Engine**:
  ```powershell
  node English_engine/train.js
  node Hindustani_engine/train.js
  node train.js --all
  ```
- **Dedicated Single-File Engine**:
  ```powershell
  py English_engine/train.py
  py Hindustani_engine/train.py
  ```
