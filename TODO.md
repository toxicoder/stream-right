# Fixes and Improvements

## High Priority
- [x] **Configuration Management**: Move hardcoded paths (e.g., `sunshine_path`, `driver_tool_path`) to a configuration file or environment variables.
- [x] **Logging**: Centralize logging configuration to avoid multiple `basicConfig` calls and inconsistent formats.
- [x] **Security**: Remove `shell=True` in `utils.run_command` to prevent potential shell injection vulnerabilities.
- [x] **Error Handling**: Add verification checks for external tools (Sunshine, Virtual Driver) before attempting to use them.

## Medium Priority
- [x] **Display Manager**: Improve `create_virtual_display` to verify if the display was actually created.
- [x] **Display Manager**: Improve `toggle_physical_display` reliability (consider retry logic or alternative APIs).
- [ ] **GPU Manager**: Add permission checks for Registry modifications or handle failures more gracefully.
- [ ] **Installation**: Implement the `install` command in `orchestrator.py` to automate dependency setup.

## Low Priority
- [ ] **Code Style**: Ensure consistent docstrings and import sorting.
- [ ] **Testing**: Add more unit tests for edge cases and failure scenarios.
