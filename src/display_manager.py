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
SM_CMONITORS = 80

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

        initial_monitors = 0
        if win32api:
            try:
                initial_monitors = win32api.GetSystemMetrics(SM_CMONITORS)
                logging.info(f"Initial monitor count: {initial_monitors}")
            except Exception as e:
                logging.warning(f"Failed to get initial monitor count: {e}")

        # Example command: VirtualDriverControl.exe add --res=1920x1080 --hz=60
        # For simplicity, we just call 'add' here, or whatever the driver supports.
        # This implementation assumes the driver tool is at `driver_exe_path`.

        # Note: Actual arguments depend on the specific driver tool being used.
        # This is a placeholder based on TDD description.
        cmd = [driver_exe_path, "add"]
        code, stdout, stderr = run_command(cmd)

        if code != 0:
            logging.error(f"Failed to create virtual display: {stderr}")
            return False

        # Verify creation
        if win32api:
            try:
                # Wait briefly for the system to register the new display
                time.sleep(1)
                final_monitors = win32api.GetSystemMetrics(SM_CMONITORS)
                logging.info(f"Final monitor count: {final_monitors}")

                if final_monitors > initial_monitors:
                    logging.info("Virtual display verified created.")
                    return True
                elif final_monitors == initial_monitors:
                    logging.warning("Virtual display creation command succeeded, but monitor count did not increase.")
                    # We'll treat this as a failure to be safe, or just a warning?
                    # The task asks to "verify if the display was actually created".
                    # Returning False here enforces the verification.
                    return False
            except Exception as e:
                logging.warning(f"Failed to verify monitor count: {e}")
                # If verification fails due to API error, fall back to command success
                return True

        logging.info("Virtual display created successfully (verification skipped).")
        return True

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

        retries = 3
        for i in range(retries):
            try:
                lparam = monitor_on if enable else monitor_off
                logging.info(f"Setting monitor power to: {'ON' if enable else 'OFF'} ({lparam}) - Attempt {i+1}")

                # SendMessage(HWND_BROADCAST, WM_SYSCOMMAND, SC_MONITORPOWER, lparam)
                ctypes.windll.user32.SendMessageW(
                    HWND_BROADCAST,
                    WM_SYSCOMMAND,
                    SC_MONITORPOWER,
                    lparam
                )
                return True
            except Exception as e:
                logging.warning(f"Attempt {i+1} failed to toggle display: {e}")
                time.sleep(0.5)

        logging.error("Failed to toggle display after retries.")
        return False
