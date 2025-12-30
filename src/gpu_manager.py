import logging
try:
    import winreg
except ImportError:
    winreg = None

class GPUManager:
    """
    Configures NVIDIA settings to force dGPU usage.
    """
    def __init__(self):
        if winreg is None:
            logging.warning("winreg module not found. GPUManager may not function correctly on this platform.")

    def force_high_performance(self, process_path):
        """
        Forces the specified process to use the dGPU via Windows Registry.
        This targets the 'UserGpuPreferences' registry key on Windows 10/11.
        """
        if not winreg:
            logging.error("Cannot modify registry: winreg module missing.")
            return False

        try:
            # Registry path for Graphics Performance Preferences
            reg_path = r"Software\Microsoft\DirectX\UserGpuPreferences"

            # Open the key (create if not exists)
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, reg_path)

            # Set the value.
            # Format: "Path\To\App.exe"="GpuPreference=2;"
            # 0=Let Windows Decide, 1=Power Saving, 2=High Performance
            value = "GpuPreference=2;"

            winreg.SetValueEx(key, process_path, 0, winreg.REG_SZ, value)
            winreg.CloseKey(key)
            logging.info(f"Set high performance GPU preference for {process_path}")
            return True
        except OSError as e:
            if e.winerror == 5: # Access Denied
                logging.error(f"Permission denied while accessing registry. Please run as Administrator. Error: {e}")
            else:
                logging.error(f"OSError accessing registry: {e}")
            return False
        except Exception as e:
            logging.error(f"Failed to set GPU preference: {e}")
            return False
