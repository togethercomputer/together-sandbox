from __future__ import annotations

import asyncio
import os
import shutil
import tempfile
from collections.abc import Callable
from dataclasses import dataclass


async def is_docker_available() -> bool:
    """Check if Docker is available on the system."""
    try:
        proc = await asyncio.create_subprocess_exec(
            "docker", "--version",
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL,
        )
        await proc.wait()
        return proc.returncode == 0
    except (FileNotFoundError, OSError):
        return False


async def find_dockerfile(directory: str) -> dict[str, bool | str | None]:
    """
    Check if a Dockerfile exists in the given directory.

    Returns:
        dict with 'exists' (bool) and 'path' (str | None)
    """
    dockerfile_path = os.path.join(directory, "Dockerfile")
    if os.path.exists(dockerfile_path):
        return {"exists": True, "path": dockerfile_path}
    return {"exists": False, "path": None}


async def create_image_dockerfile(image: str) -> dict[str, str]:
    """
    Create a temporary Dockerfile that uses the given image as its base.

    Returns:
        dict with 'dockerfile_path' and 'tmp_dir'
    """
    tmp_dir = tempfile.mkdtemp(prefix="csb-docker-")
    dockerfile_path = os.path.join(tmp_dir, "Dockerfile")
    with open(dockerfile_path, "w") as f:
        f.write(f"FROM {image}\n")
    return {"dockerfile_path": dockerfile_path, "tmp_dir": tmp_dir}


@dataclass
class DockerBuildOptions:
    dockerfile_path: str | None
    image_name: str
    context: str
    architecture: str = "amd64"
    on_output: Callable[[str], None] | None = None


async def _read_stream_lines(
    stream: asyncio.StreamReader,
    on_output: Callable[[str], None],
) -> list[str]:
    lines: list[str] = []
    async for raw in stream:
        line = raw.decode(errors="replace").rstrip("\n")
        lines.append(line)
        if line:
            on_output(line)
    return lines


async def build_docker_image(options: DockerBuildOptions) -> None:
    """Build a Docker image from a Dockerfile."""
    on_output = options.on_output or (lambda _: None)

    proc = await asyncio.create_subprocess_exec(
        "docker", "build",
        "--platform", f"linux/{options.architecture}",
        "--progress=plain",
        *(['-f', options.dockerfile_path] if options.dockerfile_path else []),
        "-t", options.image_name,
        options.context,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    stdout_lines, stderr_lines = await asyncio.gather(
        _read_stream_lines(proc.stdout, on_output),
        _read_stream_lines(proc.stderr, on_output),
    )
    await proc.wait()

    if proc.returncode != 0:
        raise RuntimeError(
            f"Docker build failed with exit code {proc.returncode}\n"
            + "\n".join(stdout_lines + stderr_lines)
        )

    on_output(f"Docker image built successfully: {options.image_name}")


@dataclass
class DockerLoginOptions:
    username: str
    password: str
    registry: str | None = None
    on_output: Callable[[str], None] | None = None


async def docker_login(options: DockerLoginOptions) -> None:
    """Authenticate with a Docker registry via stdin password."""
    on_output = options.on_output or (lambda _: None)

    args = ["docker", "login"]
    if options.registry:
        args.append(options.registry)
    args.extend(["--username", options.username, "--password-stdin"])

    proc = await asyncio.create_subprocess_exec(
        *args,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    stdout_data, stderr_data = await proc.communicate(input=options.password.encode())

    for line in stdout_data.decode(errors="replace").splitlines():
        if line:
            on_output(line)
    for line in stderr_data.decode(errors="replace").splitlines():
        if line:
            on_output(line)

    if proc.returncode != 0:
        output = stdout_data.decode(errors="replace") + stderr_data.decode(errors="replace")
        raise RuntimeError(
            f"Docker login failed with exit code {proc.returncode}\n{output}"
        )

    registry_label = f" to {options.registry}" if options.registry else ""
    on_output(f"Docker login successful{registry_label}")


async def push_docker_image(
    image_name: str,
    on_output: Callable[[str], None] | None = None,
) -> None:
    """Push a Docker image to a registry."""
    _on_output = on_output or (lambda _: None)

    proc = await asyncio.create_subprocess_exec(
        "docker", "push", image_name,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    stdout_lines, stderr_lines = await asyncio.gather(
        _read_stream_lines(proc.stdout, _on_output),
        _read_stream_lines(proc.stderr, _on_output),
    )
    await proc.wait()

    if proc.returncode != 0:
        raise RuntimeError(
            f"Docker push failed with exit code {proc.returncode}\n"
            + "\n".join(stdout_lines + stderr_lines)
        )

    _on_output(f"Docker image pushed successfully: {image_name}")