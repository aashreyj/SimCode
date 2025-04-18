import os
import subprocess
import uuid
from http import HTTPStatus

from fastapi.responses import JSONResponse

from ..constants import (
    DEFAULT_EXECUTION_TIMEOUT,
    JAVA_EXECUTION_TIMEOUT,
    LANG_CONFIG_MAP,
    USER_SCRIPT_FILE_NAME,
)
from ..models.code import Code

"""
Get the combined execution script from the user code and prerequisites
"""
def get_combined_script(code: Code) -> str:
    return f"""#!/bin/bash
ulimit -t 2
{"ulimit -v 262144" if code.language not in ["javascript", "java"] else ""}

{code.prerequisites}

{' '.join(LANG_CONFIG_MAP[code.language]["command"])}
"""


"""
Prepare sandboxed environment for code execution
"""
def create_sandbox_env(session_id: str, code: Code) -> str:
    base_dir = f"/tmp/{session_id}"
    os.makedirs(base_dir, exist_ok=True)

    # Write user code to file
    with open(f"{base_dir}/{LANG_CONFIG_MAP[code.language]["file"]}", "w") as f:
        f.write(code.code)

    # Combine setup + run into single script
    run_script = get_combined_script(code)

    with open(f"{base_dir}/{USER_SCRIPT_FILE_NAME}", "w") as f:
        f.write(run_script)
        os.chmod(f"{base_dir}/{USER_SCRIPT_FILE_NAME}", 0o755)
    return base_dir


"""
This function executes the user code in a Docker container.
It uses a sandboxed environment to ensure security and isolation.
"""
def execute_code(code: Code):
    session_id = str(uuid.uuid4())
    base_dir = create_sandbox_env(session_id, code)

    # Run Docker container with volume mount
    try:
        result = subprocess.run(
            [
                "docker",
                "run",
                "--rm",
                "-v",
                f"{base_dir}:/sandbox",
                "-w",
                "/sandbox",
                f"{LANG_CONFIG_MAP[code.language]["image"]}",
                f"./{USER_SCRIPT_FILE_NAME}",
            ],
            capture_output=True,
            text=True,
            timeout=(
                DEFAULT_EXECUTION_TIMEOUT
                if code.language != "java"
                else JAVA_EXECUTION_TIMEOUT
            ),
        )

        if not result.returncode:
            result.stderr = ""

        return JSONResponse(
            {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode,
            }
        )

    except subprocess.TimeoutExpired:
        return JSONResponse(
            {"message": "Execution timed out"}, status_code=HTTPStatus.REQUEST_TIMEOUT
        )
    except Exception as err:
        return JSONResponse(
            {"message": "Unknown error occurred", "error": repr(err)},
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        )
