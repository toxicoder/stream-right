import subprocess
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_command(command):
    """
    Executes a shell command.
    Returns (return_code, stdout, stderr).
    """
    try:
        logging.info(f"Running command: {command}")
        # Using shell=True for flexibility with command strings, but requires care with input.
        # Since this is an internal tool, we assume inputs are relatively safe or controlled.
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode != 0:
            logging.error(f"Command failed with code {result.returncode}: {result.stderr}")
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        logging.error(f"Exception executing command: {e}")
        return -1, "", str(e)
