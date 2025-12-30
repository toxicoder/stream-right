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

    def check_registry_access(self):
        """
        Checks if the process has write access to the registry key.

        Returns:
            bool: True if write access is available (or if exception handling suggests it might be), False if access is explicitly denied.
        """
        if not winreg:
            return False

        reg_path = r"Software\Microsoft\DirectX\UserGpuPreferences"
        try:
            # Try to open the key with write permission
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_WRITE)
            winreg.CloseKey(key)
            return True
        except OSError as e:
            # If Access Denied, return False
            if e.winerror == 5:
                return False
            # If File Not Found (2), we assume we can create it (or handled by CreateKey)
            # For other errors, we also optimistically return True to let CreateKey handle it
            return True

    def force_high_performance(self, process_path):
        """
        Forces the specified process to use the dGPU via Windows Registry.
        This targets the 'UserGpuPreferences' registry key on Windows 10/11.

        Args:
            process_path (str): The full path to the executable to configure.

        Returns:
            bool: True if the registry value was set successfully, False otherwise.
        """
        if not winreg:
            logging.error("Cannot modify registry: winreg module missing.")
            return False

        if not self.check_registry_access():
            logging.error("Permission denied while accessing registry. Please run as Administrator.")
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
