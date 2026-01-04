import logging
import subprocess

def setup_logging(level=logging.INFO):
    """
    Configures the logging for the application.

    Args:
        level (int, optional): The logging level (default: logging.INFO).
    """
    logging.basicConfig(level=level, format='%(asctime)s - %(levelname)s - %(message)s')

def run_command(command, shell=False):
    """
    Executes a shell command.

    Args:
        command (list or str): The command to execute. Should be a list if shell=False.
        shell (bool, optional): Whether to use the shell to execute the command. Defaults to False.

    Returns:
        tuple: (return_code, stdout, stderr)
    """
    try:
        logging.info(f"Running command: {command}")
        # shell=True should be avoided when possible.
        result = subprocess.run(
            command,
            shell=shell,
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
