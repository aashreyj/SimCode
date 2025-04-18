ACTION_JOINED = "joined"
ACTION_DISCONNECTED = "disconnected"
ACTION_LANG_CHANGE = "lang_change"
ACTION_CODE_CHANGE = "code_change"
ACTION_PREREQ_CHANGE = "prereq_change"
ACTION_CODE_EXECUTED = "code_executed"

FRONTEND_PORT = 3000
FRONTEND_URL = f"http://localhost:{FRONTEND_PORT}"

USER_SCRIPT_FILE_NAME = "run_combined.sh"
LANG_CONFIG_MAP = {
    "python": {
        "file": "user_code.py",
        "command": ["python3", "user_code.py"],
        "image": "python:3.10-slim",
    },
    "cpp": {
        "file": "user_code.cpp",
        "command": ["g++ user_code.cpp -o out && ./out"],
        "image": "gcc:latest",
    },
    "java": {
        "file": "Main.java",
        "command": ["javac Main.java && java Main"],
        "image": "openjdk:17-slim",
    },
    "javascript": {
        "file": "user_code.js",
        "command": ["node", "user_code.js"],
        "image": "node:18-slim",
    },
    "bash": {
        "file": "user_code.sh",
        "command": ["bash", "user_code.sh"],
        "image": "ubuntu:22.04",
    },
}
DEFAULT_EXECUTION_TIMEOUT = 60
JAVA_EXECUTION_TIMEOUT = 300
