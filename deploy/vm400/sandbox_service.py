#!/usr/bin/env python3
"""VM400 Sandbox Service - Secure code execution endpoint.

This service runs on a VM sandbox and provides
isolated Python/Bash execution via Docker containers.

Security: All code runs in isolated Docker containers with:
- No network access
- Read-only filesystem
- Memory/CPU limits
- Non-root user

Usage:
    uvicorn sandbox_service:app --host 0.0.0.0 --port 8100
"""

import asyncio
import os
import shutil
import tempfile
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

import docker

app = FastAPI(
    title="MPtoO Sandbox Service",
    description="Secure code execution in isolated containers",
    version="1.0.0",
)

# Configuration
SANDBOX_API_KEY = os.getenv("SANDBOX_API_KEY", "mptoo-sandbox-key-2025")
DOCKER_IMAGE_PYTHON = "python:3.12-slim"
DOCKER_IMAGE_BASH = "ubuntu:22.04"
DEFAULT_TIMEOUT = 30
MAX_TIMEOUT = 120
MEMORY_LIMIT = "512m"
CPU_LIMIT = 0.5


class ExecuteRequest(BaseModel):
    """Request to run code."""

    code: str = Field(..., description="Code to run")
    language: str = Field(default="python", description="python or bash")
    timeout: int = Field(default=DEFAULT_TIMEOUT, ge=1, le=MAX_TIMEOUT)
    stdin: str | None = Field(default=None, description="Standard input")


class ExecuteResponse(BaseModel):
    """Response from code run."""

    run_id: str
    success: bool
    stdout: str
    stderr: str
    exit_code: int
    duration_ms: float
    language: str


def get_docker_client():
    """Get Docker client."""
    return docker.from_env()


def validate_code(code: str, language: str) -> tuple[bool, str]:
    """Validate code for dangerous patterns."""
    dangerous_python = [
        "__import__('os').system",
        "subprocess.call",
        "shutil.rmtree('/'",
    ]
    dangerous_bash = [
        "rm -rf /",
        ":(){ :|:& };:",
        "> /dev/sda",
        "mkfs.",
    ]

    blocked = dangerous_python if language == "python" else dangerous_bash
    for pattern in blocked:
        if pattern in code:
            return False, f"Blocked pattern: {pattern[:20]}..."

    return True, ""


async def run_in_container(
    code: str,
    language: str,
    timeout: int,
    stdin: str | None = None,
) -> dict:
    """Run code in Docker container."""
    run_id = str(uuid.uuid4())[:8]
    start_time = datetime.now()

    client = get_docker_client()
    work_dir = Path(tempfile.mkdtemp(prefix=f"sandbox_{run_id}_"))

    try:
        if language == "python":
            image = DOCKER_IMAGE_PYTHON
            code_file = work_dir / "script.py"
            code_file.write_text(code)
            cmd = ["python", "/workspace/script.py"]
        else:
            image = DOCKER_IMAGE_BASH
            code_file = work_dir / "script.sh"
            code_file.write_text(f"#!/bin/bash\n{code}")
            cmd = ["bash", "/workspace/script.sh"]

        container = client.containers.run(
            image,
            command=cmd,
            volumes={str(work_dir): {"bind": "/workspace", "mode": "ro"}},
            detach=True,
            mem_limit=MEMORY_LIMIT,
            cpu_period=100000,
            cpu_quota=int(CPU_LIMIT * 100000),
            network_disabled=True,
            user="nobody",
            read_only=True,
            tmpfs={"/tmp": "size=64M"},
        )

        try:
            result = container.wait(timeout=timeout)
            exit_code = result["StatusCode"]
        except Exception:
            container.kill()
            exit_code = -1

        stdout = container.logs(stdout=True, stderr=False).decode("utf-8", errors="replace")
        stderr = container.logs(stdout=False, stderr=True).decode("utf-8", errors="replace")

        container.remove(force=True)
        duration = (datetime.now() - start_time).total_seconds() * 1000

        return {
            "run_id": run_id,
            "success": exit_code == 0,
            "stdout": stdout[:10000],
            "stderr": stderr[:5000],
            "exit_code": exit_code,
            "duration_ms": duration,
            "language": language,
        }

    finally:
        shutil.rmtree(work_dir, ignore_errors=True)


@app.post("/run", response_model=ExecuteResponse)
async def run_code(
    request: ExecuteRequest,
    x_api_key: str = Header(..., alias="X-API-Key"),
):
    """Run code in isolated container."""
    if x_api_key != SANDBOX_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

    if request.language not in ["python", "bash"]:
        raise HTTPException(status_code=400, detail="Language must be python or bash")

    is_valid, error = validate_code(request.code, request.language)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error)

    try:
        result = await run_in_container(
            code=request.code,
            language=request.language,
            timeout=request.timeout,
            stdin=request.stdin,
        )
        return ExecuteResponse(**result)
    except docker.errors.DockerException as e:
        raise HTTPException(status_code=500, detail=f"Docker error: {str(e)}")


@app.get("/health")
async def health():
    """Health check."""
    try:
        client = get_docker_client()
        client.ping()
        return {"status": "healthy", "docker": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8100)
