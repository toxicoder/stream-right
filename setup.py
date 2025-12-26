from setuptools import setup, find_packages

setup(
    name="easy-game-streaming",
    version="0.1.0",
    description="Simplifies game streaming using Moonlight and Sunshine on Windows 11",
    author="Your Name",
    packages=find_packages(),
    install_requires=[
        "pywin32",
        "psutil",
    ],
    entry_points={
        "console_scripts": [
            "easy-stream=src.orchestrator:main",
        ],
    },
)
