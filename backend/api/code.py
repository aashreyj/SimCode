import os
import subprocess
import uuid
from typing import Optional

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

router = APIRouter()

LANG_CONFIG_MAP = {
    "python": {
        "file": "user_code.py",
        "command": ["python3", "user_code.py"],
        "image": "python:3.10-slim"
    },
    "cpp": {
        "file": "user_code.cpp",
        "command": ["g++ user_code.cpp -o out && ./out"],
        "image": "gcc:latest"
    },
    "java": {
        "file": "Main.java",
        "command": ["javac Main.java && java Main"],
        "image": "openjdk:17-slim"
    },
    "javascript": {
        "file": "user_code.js",
        "command": ["node", "user_code.js"],
        "image": "node:18-slim"
    },
    "shell": {
        "file": "user_code.sh",
        "command": ["bash", "user_code.sh"],
        "image": "ubuntu:22.04"
    }
}


class Code(BaseModel):
    language: str
    prerequisites: Optional[str] = ""
    code: str


@router.post("/execute")
async def run_code(code: Code):
    if code.language not in LANG_CONFIG_MAP.keys():
        return JSONResponse({"message": "Language not supported"}, status_code=400)

    session_id = str(uuid.uuid4())
    base_dir = f"/tmp/{session_id}"
    os.makedirs(base_dir, exist_ok=True)

    # Write user code to file
    with open(f"{base_dir}/{LANG_CONFIG_MAP[code.language]['file']}", "w") as f:
        f.write(code.code)

    # Combine setup + run into run_combined.sh
    run_script = f"""#!/bin/bash
ulimit -t 2
{"ulimit -v 262144" if code.language not in ["javascript", "java"] else ""}

{code.prerequisites}

{' '.join(LANG_CONFIG_MAP[code.language]["command"])}
"""

    with open(f"{base_dir}/run_combined.sh", "w") as f:
        f.write(run_script)

    os.chmod(f"{base_dir}/run_combined.sh", 0o755)

    # Run Docker container with volume mount
    try:
        result = subprocess.run(
            [
                "sudo", "docker", "run", "--rm",
                "-v", f"{base_dir}:/sandbox",
                "-w", "/sandbox",
                f"{LANG_CONFIG_MAP[code.language]['image']}",
                "./run_combined.sh"
            ],
            capture_output=True,
            text=True,
            timeout=60 if code.language != "java" else 300
        )

        if not result.returncode:
            result.stderr = ""

        return JSONResponse({
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode
        })

    except subprocess.TimeoutExpired:
        return JSONResponse({"message": "Execution timed out"}, status_code=408)
    except Exception as err:
        return JSONResponse({"message": "Unknown error occurred", "error": repr(err)}, status_code=500)
