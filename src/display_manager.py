import logging
import time
from .utils import run_command

# Handle Windows-specific imports
try:
    import win32api
    import win32con
    import ctypes
    from ctypes import wintypes
except ImportError:
    win32api = None
    win32con = None
    ctypes = None
    wintypes = None

# Constants for Monitor Power
SC_MONITORPOWER = 0xF170
monitor_on = -1
monitor_low_power = 1
monitor_off = 2
WM_SYSCOMMAND = 0x0112
HWND_BROADCAST = 0xFFFF

class DisplayManager:
    """
    Handles virtual display creation, resolution setting, and physical display power control.
    """
    def __init__(self):
        if not all([win32api, win32con, ctypes]):
             logging.warning("Windows APIs not found. DisplayManager functionality will be limited.")

    def create_virtual_display(self, driver_exe_path, index=0):
        """
        Creates a virtual monitor using the provided driver executable.
        Assumes the driver executable has an 'add' command.
        """
        logging.info("Creating virtual display...")
        # Example command: VirtualDriverControl.exe add --res=1920x1080 --hz=60
        # For simplicity, we just call 'add' here, or whatever the driver supports.
        # This implementation assumes the driver tool is at `driver_exe_path`.

        # Note: Actual arguments depend on the specific driver tool being used.
        # This is a placeholder based on TDD description.
        cmd = [driver_exe_path, "add"]
        code, stdout, stderr = run_command(cmd)
        if code == 0:
            logging.info("Virtual display created successfully.")
            return True
        else:
            logging.error(f"Failed to create virtual display: {stderr}")
            return False

    def set_resolution(self, width, height, device_name=None):
        """
        Sets the resolution of the display.
        If device_name is None, it tries to find the virtual display or primary.
        """
        if not win32api:
            logging.error("win32api not available.")
            return False

        try:
            if not device_name:
                # In a real scenario, we'd iterate EnumDisplayDevices to find the correct one.
                # For now, we'll try to change the default/primary if no device specified,
                # or you'd pass specific device name like \\.\DISPLAY2
                device = win32api.EnumDisplayDevices(None, 0)
                device_name = device.DeviceName

            logging.info(f"Setting resolution for {device_name} to {width}x{height}")

            devmode = win32api.EnumDisplaySettings(device_name, win32con.ENM_CURRENT_SETTINGS)
            devmode.PelsWidth = width
            devmode.PelsHeight = height
            devmode.Fields = win32con.DM_PELSWIDTH | win32con.DM_PELSHEIGHT

            result = win32api.ChangeDisplaySettingsEx(device_name, devmode, win32con.CDS_TEST)
            if result != win32con.DISP_CHANGE_SUCCESSFUL:
                logging.error(f"Resolution change test failed with code {result}")
                return False

            result = win32api.ChangeDisplaySettingsEx(device_name, devmode, 0)
            if result == win32con.DISP_CHANGE_SUCCESSFUL:
                logging.info("Resolution changed successfully.")
                return True
            else:
                logging.error(f"Resolution change failed with code {result}")
                return False

        except Exception as e:
            logging.error(f"Exception setting resolution: {e}")
            return False

    def toggle_physical_display(self, enable: bool):
        """
        Turns the physical display on or off.
        """
        if not ctypes:
            logging.error("ctypes not available.")
            return False

        try:
            lparam = monitor_on if enable else monitor_off
            logging.info(f"Setting monitor power to: {'ON' if enable else 'OFF'} ({lparam})")

            # SendMessage(HWND_BROADCAST, WM_SYSCOMMAND, SC_MONITORPOWER, lparam)
            ctypes.windll.user32.SendMessageW(
                HWND_BROADCAST,
                WM_SYSCOMMAND,
                SC_MONITORPOWER,
                lparam
            )
            return True
        except Exception as e:
            logging.error(f"Failed to toggle display: {e}")
            return False
