# Technical Design Document: Easy Game Streaming with Moonlight and Sunshine

## 1. Overview

This document outlines the technical design for a GitHub repository that simplifies game streaming using Moonlight (client) and Sunshine (server). The focus is on automating the pre- and post-streaming setup to ensure a seamless experience, particularly on Windows 11 laptops with hybrid graphics (e.g., Intel iGPU and NVIDIA dGPU). The solution handles virtual display creation, resolution matching, display switching, and physical display power management. It does not modify Moonlight or Sunshine core functionality but acts as a wrapper to orchestrate the environment.

The repository will contain scripts, configuration files, and documentation to make setup "super easy." Users can run a single command or executable to prepare the host for streaming, launch Sunshine, and revert changes post-streaming.

Key goals:
- Enable headless streaming by using a virtual display.
- Match the virtual display resolution to the Moonlight client's resolution (or a scaled version with the same aspect ratio).
- Turn off the physical display during streaming to save power (especially on laptops).
- Handle automatic GPU switching on hybrid systems to ensure the dGPU is used for optimal performance.
- Support smooth transitions: Extend desktop to virtual display, stream, then revert to physical display.

## 2. Requirements

### Functional Requirements
- **Virtual Display Management**: Create a virtual monitor on demand, set its resolution dynamically based on client input or detection.
- **Resolution Handling**: Query or accept Moonlight client resolution (e.g., via command-line args or Sunshine logs). If exact match isn't possible, select the closest resolution with the same aspect ratio (e.g., 16:9).
- **Display Switching**: Extend the desktop to the virtual display, set it as the capture target for Sunshine, and disable the physical display during streaming.
- **GPU Management**: Force Sunshine and related processes to use the dGPU on Optimus-enabled laptops.
- **Streaming Lifecycle**:
  - Pre-stream: Setup virtual display, adjust resolution, turn off physical display.
  - During stream: Monitor session (e.g., via Sunshine process) and keep physical display off.
  - Post-stream: Re-enable physical display, remove virtual display if desired.
- **User Experience**: Minimal configuration; provide a GUI or CLI for starting/stopping.

### Non-Functional Requirements
- **Platform**: Windows 11 (x64).
- **Dependencies**: Minimal external tools; leverage open-source drivers and APIs.
- **Performance**: Low overhead; virtual display should support up to 4K@60Hz or higher.
- **Security**: No elevated privileges beyond what's needed for display changes.
- **Compatibility**: Work with NVIDIA GPUs; test on laptops with Optimus (e.g., Intel + NVIDIA).

### Assumptions
- Sunshine and Moonlight are pre-installed.
- User has administrative access for driver installation.
- Client resolution is provided manually or detected via Sunshine's API/logs (if available).

## 3. Architecture

The system is a modular script-based application, primarily in Python for cross-compatibility and ease of use. It integrates with Windows APIs for display management and external drivers for virtual displays.

### High-Level Components
- **Setup Script**: Installs dependencies (e.g., virtual display driver).
- **Core Orchestrator**: A main script/executable that handles lifecycle (pre/during/post-stream).
- **Display Manager Module**: Handles virtual display creation, resolution setting, and physical display power control.
- **GPU Manager Module**: Configures NVIDIA settings to force dGPU usage.
- **Streaming Monitor**: Watches Sunshine process or uses hooks to detect start/end of sessions.
- **Configuration File**: JSON/YAML for user settings (e.g., preferred resolutions, display IDs).

### Data Flow
1. User runs the orchestrator script (e.g., `stream_setup.py start --client-res=1920x1080`).
2. GPU Manager forces dGPU for Sunshine.
3. Display Manager creates/extends virtual display and sets resolution.
4. Physical display is turned off.
5. Sunshine is launched, configured to capture virtual display.
6. On session end (detected via process exit or timeout), revert: Re-enable physical display, optionally remove virtual display.

### Tech Stack
- **Language**: Python 3.10+ (for scripting and API calls).
- **Libraries**:
  - `pywin32`: For Windows API interactions (e.g., display settings via `user32.dll`).
  - `psutil`: For process monitoring (Sunshine detection).
  - `subprocess`: For running external tools/commands.
  - `ctypes`: For low-level API calls (e.g., monitor power).
- **External Tools**:
  - Virtual Display Driver (from GitHub: VirtualDrivers/Virtual-Display-Driver) for creating virtual monitors.
  - SetResolution (command-line tool) or direct API for resolution changes.
  - NVIDIA Control Panel APIs or registry tweaks for GPU forcing.
- **Build/Packaging**: PyInstaller for creating a standalone EXE; GitHub Actions for CI/CD.

## 4. Detailed Design

### 4.1 Virtual Display Creation
- Use Virtual-Display-Driver (open-source, supports high-res/refresh rates).
- Installation: Script downloads and installs the driver (requires admin).
- Creation: Use the driver's control app/API to add a virtual monitor (e.g., via command-line: `VirtualDriverControl.exe add --res=1920x1080 --hz=60`).
- Extension: Use Windows API (`ChangeDisplaySettingsEx`) to extend the desktop to the virtual display.

### 4.2 Resolution Setting
- Detect available modes: `EnumDisplaySettings` API to list resolutions for the virtual display.
- Set resolution: `ChangeDisplaySettingsEx` with `DMDO_DEFAULT` flag.
- Client Matching: Accept resolution as input (e.g., CLI arg). If aspect ratio mismatch, calculate closest (e.g., for 1920x1080 client, use 3840x2160 if supported, else scale down).
- Fallback: Default to 1920x1080@60Hz.

### 4.3 Physical Display Control
- Turn off: Use Windows API call `SendMessage(HWND_BROADCAST, WM_SYSCOMMAND, SC_MONITORPOWER, 2)` via `ctypes`.
- Avoid locking: Combine with `nircmd.exe monitor off` (if needed) or adjust power settings to prevent sleep/lock.
- Re-enable: Send `SC_MONITORPOWER, -1` or simulate input to wake.
- Identification: Use `EnumDisplayMonitors` to distinguish physical vs. virtual (based on driver name or ID).

### 4.4 GPU Switching
- On Optimus laptops: Use NVIDIA API or Windows Graphics settings.
- Force dGPU: Add Sunshine.exe to Windows Graphics settings (`rundll32.exe` or registry: HKCU\Software\Microsoft\DirectX\UserGpuPreferences).
- Detection: Query WMI (`Win32_VideoController`) to check for multiple GPUs.
- Auto-Switch: Set Sunshine to "High Performance" in NVIDIA Control Panel via script (e.g., `nvapi.dll` calls if needed).

### 4.5 Streaming Integration
- Launch Sunshine: `subprocess` to run with config pointing to virtual display (e.g., edit `sunshine.conf` to set `display=\\.\DISPLAY2`).
- Session Detection: Poll `psutil` for Sunshine process; on start, trigger setup; on exit, trigger teardown.
- Resolution Detection: Parse Sunshine logs for client info or require manual input.

### 4.6 Error Handling and Logging
- Log to file/console using `logging` module.
- Handle failures: E.g., if virtual driver install fails, fallback to error message.
- Timeouts: If physical display doesn't turn off, retry.

## 5. Workflow

### Pre-Streaming Setup
1. Check/install Virtual Display Driver.
2. Force dGPU for Sunshine.
3. Create virtual display if not present.
4. Set virtual resolution based on input.
5. Extend desktop.
6. Turn off physical display.
7. Launch Sunshine configured for virtual capture.

### During Streaming
- Monitor process; keep physical off.
- If client changes resolution (if detectable), adjust virtual dynamically.

### Post-Streaming Teardown
1. Detect Sunshine exit.
2. Re-enable physical display.
3. Disconnect/remove virtual display.
4. Revert GPU settings if needed.

## 6. Potential Challenges and Mitigations
- **Driver Compatibility**: Virtual-Display-Driver may require signature enforcement disabled (mitigation: Guide users on boot options).
- **Resolution Detection**: If Sunshine doesn't expose client res easily, require user input or use defaults.
- **Power Management**: Physical display might not stay off; use timers or hooks.
- **Laptop-Specific Issues**: Battery drain; advise AC power.
- **Testing**: Test on physical hardware; emulate with VMs where possible.
- **Updates**: Sunshine/Moonlight changes; make config modular.

## 7. Repository Structure
```
easy-game-streaming/
├── src/
│   ├── display_manager.py
│   ├── gpu_manager.py
│   ├── orchestrator.py
│   └── utils.py
├── config/
│   └── settings.json
├── docs/
│   └── TECHNICAL_DESIGN.md (this doc)
├── tools/
│   └── (downloaded drivers/tools)
├── README.md
├── setup.py (for installation)
└── requirements.txt
```

## 8. Installation and Usage
- Clone repo: `git clone https://github.com/[username]/easy-game-streaming.git`
- Install deps: `pip install -r requirements.txt`
- Run setup: `python src/orchestrator.py install`
- Start: `python src/orchestrator.py start --client-res=1920x1080`
- Stop: `python src/orchestrator.py stop`

## 9. Future Enhancements
- GUI interface (using Tkinter or PyQt).
- Auto-detect client resolution via Sunshine web API.
- Multi-monitor support.
- macOS/Linux compatibility (if demand arises).
