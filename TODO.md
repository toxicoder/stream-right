# Technical Roadmap & TODO

## High Priority

### 1. Registry State Cleanup (The "Revert" Problem)
**Status:** Pending
**Context:** `src/gpu_manager.py` modifies `HKCU\Software\Microsoft\DirectX\UserGpuPreferences` to enforce high-performance GPU usage but fails to clean up this entry, leading to registry pollution.

**Implementation Plan:**
*   **Modify `src/gpu_manager.py`**:
    *   Add a new method `revert_high_performance(self, process_path: str) -> None`.
    *   Use `winreg.OpenKey` with `winreg.HKEY_CURRENT_USER` and `winreg.KEY_WRITE` to access the key.
    *   Use `winreg.DeleteValue(key, value_name)` where `value_name` corresponds to the `process_path`.
    *   Wrap the deletion in a `try...except FileNotFoundError` block to handle cases where the key or value has already been removed or does not exist, logging a debug message instead of crashing.
*   **Update `src/orchestrator.py`**:
    *   In the `stop()` method, explicitly call `self.gpu_manager.revert_high_performance()` for the Sunshine executable (or the relevant game executable if applicable).
    *   Ensure this is called during the shutdown sequence to guarantee the registry is returned to its original state.

### 2. Crash Resilience (The "Black Screen" Prevention)
**Status:** Pending
**Context:** Exceptions raised during the active streaming phase (after the physical monitor is disabled) can abort the script without re-enabling the monitor, leaving the user with a black screen.

**Implementation Plan:**
*   **Modify `src/orchestrator.py`**:
    *   Identify the critical section in `start()` where `display_manager.toggle_physical_display(enable=False)` is called.
    *   Wrap the subsequent logic (launching Sunshine, waiting for termination) in a `try...finally` block.
    *   **Crucial:** In the `finally` block, enforce the restoration of the physical display:
        ```python
        finally:
            self.logger.info("Ensuring physical display is enabled...")
            self.display_manager.toggle_physical_display(enable=True)
        ```
    *   Alternatively, implement a Context Manager (e.g., `PhysicalDisplayContext`) in `src/display_manager.py` that handles the toggle off/on automatically on enter/exit.

### 3. Admin Privilege Enforcement
**Status:** Pending
**Context:** Components like `src/installer.py` (which uses `pnputil`) and potentially `src/gpu_manager.py` require Administrator privileges to function correctly. Running without them leads to silent failures or permission errors.

**Implementation Plan:**
*   **Update `src/utils.py`**:
    *   Add a function `is_admin() -> bool`.
    *   Implementation: `return ctypes.windll.shell32.IsUserAnAdmin() != 0`.
*   **Update `src/orchestrator.py`**:
    *   In the `main()` function (or `if __name__ == "__main__":` block), call `is_admin()` as the very first step.
    *   If it returns `False`, print a descriptive error message to `stderr` (e.g., "This application requires Administrator privileges to manage drivers and registry settings.") and execute `sys.exit(1)`.

## Medium Priority

### 4. IGDB Token Persistence
**Status:** Pending
**Context:** `src/metadata_provider.py` performs a fresh authentication request to Twitch/IGDB on every execution. This is inefficient, increases latency, and risks hitting rate limits.

**Implementation Plan:**
*   **Modify `src/metadata_provider.py`**:
    *   Define a cache file path (e.g., `.igdb_cache.json` or inside a user app data directory).
    *   **Update `authenticate()`**:
        1.  Check if the cache file exists.
        2.  If it exists, load the JSON content and check the `expires_at` timestamp against `time.time()`.
        3.  If valid, use the cached `access_token`.
        4.  If invalid or missing, proceed with the existing network request to fetch a new token.
        5.  **Save Cache:** After a successful network request, write the `access_token` and calculated `expires_at` (current time + `expires_in` - buffer) to the cache file.

### 5. Robust VDF Parsing
**Status:** Pending
**Context:** `src/game_scanner.py` relies on `re.findall` to parse Steam's `libraryfolders.vdf`. This regex approach is fragile and fails with nested VDF structures or unexpected formatting.

**Implementation Plan:**
*   **Modify `src/game_scanner.py`**:
    *   Deprecate the current regex-based parsing for `libraryfolders.vdf`.
    *   Implement a **Stack-Based Parser** or a **Recursive Descent Parser**:
        *   Iterate through the file line by line.
        *   Track the nesting level using curly braces `{` (push) and `}` (pop).
        *   Extract key-value pairs based on the current nesting context.
    *   Alternatively, look for a lightweight, dependency-free VDF parsing function to include in `src/utils.py` if available (avoiding heavy external dependencies if possible, but a custom simple parser is preferred over regex).
    *   Ensure the parser correctly extracts all library paths, regardless of how deep they are nested or the order of keys.
