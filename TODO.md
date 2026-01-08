# Plans and Improvements

## High Priority
- [x] **Display Manager**: Implement `remove_virtual_display` method in `src/display_manager.py` to allow removing the virtual display.
- [x] **Orchestrator**: Update `stop` method in `src/orchestrator.py` to call `remove_virtual_display` to clean up resources.
- [x] **Orchestrator/Display Manager**: Improve logic to correctly identify and target the virtual display when setting resolution, instead of potentially changing the primary display.

## Medium Priority
- [ ] **GPU Manager**: Implement a method to remove the GPU preference registry key (e.g., `revert_high_performance`) and optionally call it in `stop` or a cleanup command.
- [x] **Installer**: Add checksum verification (SHA256) for downloaded driver files to ensure integrity.
- [ ] **Config**: Add validation for configuration values (e.g., check if paths are valid/absolute) within `Config` class.

## Low Priority
- [ ] **Refactoring**: Migrate from `os.path` to `pathlib` for file path manipulations.
- [ ] **Testing**: Add more comprehensive tests for `DisplayManager` (mocking Windows APIs).
- [ ] **Logging**: Improve log messages to include more context (e.g., which device is being operated on).
