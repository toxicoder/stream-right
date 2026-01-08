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

    def _get_display_devices(self):
        """Helper to enumerate all display devices."""
        devices = []
        if not win32api:
            return devices
        i = 0
        while True:
            try:
                device = win32api.EnumDisplayDevices(None, i)
                devices.append(device.DeviceName)
                i += 1
            except Exception:
                break
        return devices

    def create_virtual_display(self, driver_exe_path, index=0):
        """
        Creates a virtual monitor using the provided driver executable.
        Assumes the driver executable has an 'add' command.

        Args:
            driver_exe_path (str): The path to the Virtual Display Driver executable.
            index (int, optional): The index for the virtual display (default is 0).

        Returns:
            str: The DeviceName of the created display (e.g. \\.\DISPLAY2) if successful, None otherwise.
        """
        logging.info("Creating virtual display...")

        initial_devices = self._get_display_devices()
        logging.info(f"Initial devices: {initial_devices}")

        # Example command: VirtualDriverControl.exe add --res=1920x1080 --hz=60
        # For simplicity, we just call 'add' here, or whatever the driver supports.
        # This implementation assumes the driver tool is at `driver_exe_path`.
        cmd = [driver_exe_path, "add"]
        code, stdout, stderr = run_command(cmd)

        if code != 0:
            logging.error(f"Failed to create virtual display: {stderr}")
            return None

        # Verify creation and identify new device
        if win32api:
            try:
                # Wait briefly for the system to register the new display
                time.sleep(1)
                final_devices = self._get_display_devices()
                logging.info(f"Final devices: {final_devices}")

                new_devices = list(set(final_devices) - set(initial_devices))

                if new_devices:
                    new_device = new_devices[0]
                    logging.info(f"Virtual display verified created: {new_device}")
                    return new_device
                else:
                    logging.warning("Virtual display creation command succeeded, but no new device found.")
                    return None

            except Exception as e:
                logging.warning(f"Failed to verify monitor creation: {e}")
                # If verification fails due to API error, we can't identify the device
                return None

        logging.info("Virtual display created successfully (verification skipped). Returning placeholder.")
        # Without win32api, we can't identify the device.
        return None

    def remove_virtual_display(self, driver_exe_path):
        """
        Removes the virtual display.

        Args:
            driver_exe_path (str): The path to the Virtual Display Driver executable.
        """
        logging.info("Removing virtual display...")
        cmd = [driver_exe_path, "remove"]
        code, stdout, stderr = run_command(cmd)

        if code == 0:
            logging.info("Virtual display removed successfully.")
        else:
            logging.error(f"Failed to remove virtual display: {stderr}")

    def set_resolution(self, width, height, device_name=None):
        r"""
        Sets the resolution of the display.
        If device_name is None, it tries to find the virtual display or primary.

        Args:
            width (int): The target width.
            height (int): The target height.
            device_name (str, optional): The name of the display device (e.g., r"\\.\DISPLAY1"). Defaults to None.

        Returns:
            bool: True if the resolution was set successfully, False otherwise.
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

        Args:
            enable (bool): True to turn the display on, False to turn it off.

        Returns:
            bool: True if the command was sent successfully (after retries), False otherwise.
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
