from __future__ import annotations

import asyncio
import json
from pathlib import Path

import httpx
import pathspec
from httpx_sse import aconnect_sse

from ._utils import _with_retry


class RemoteImageBuilderClient:
    """
    Client for the image-builder remote build service.

    Submits a build context to the service, streams build logs via SSE,
    and returns the final image reference on success.
    """

    def __init__(self, api_url: str, token: str, logger=None):
        self._api_url = api_url.rstrip("/")
        self._token = token
        self._logger = logger

    async def build(
        self,
        context_dir: Path,
        image_name: str,
        dockerfile: str = "Dockerfile",
        build_args: dict[str, str] | None = None,
        nydus: bool = True,
    ) -> str:
        """
        Build and push a container image.

        Args:
            context_dir: Local directory to use as the Docker build context.
            image_name: Image name in "name" or "name:tag" format. The namespace
                is derived server-side from the auth token. If no tag is included
                the server defaults to "latest".
            dockerfile: Dockerfile path relative to context_dir.
            build_args: Optional build arguments.
            nydus: Produce a nydus-compressed image (default True).

        Returns:
            str: Full image reference returned by the service (e.g. "registry/namespace/name:tag").

        Raises:
            RuntimeError: If the build fails.
            httpx.HTTPStatusError: If an API request fails.
        """
        import io
        import tarfile as tarfile_module

        # Collect .dockerignore exclusions
        dockerignore_path = context_dir / ".dockerignore"
        if dockerignore_path.exists():
            spec = pathspec.PathSpec.from_lines(
                "gitwildmatch", dockerignore_path.read_text().splitlines()
            )
        else:
            spec = None

        # Build tar.gz of the context in memory
        buf = io.BytesIO()
        with tarfile_module.open(fileobj=buf, mode="w:gz") as tar:
            for file_path in sorted(context_dir.rglob("*")):
                if not file_path.is_file() and not file_path.is_symlink():
                    continue
                relative = file_path.relative_to(context_dir)
                if spec and spec.match_file(str(relative)):
                    continue
                tar.add(str(file_path), arcname=f"./{relative}", recursive=False)
        buf.seek(0)

        headers = {"Authorization": f"Bearer {self._token}"}
        data = {
            "image_name": image_name,
            "dockerfile": dockerfile,
            "build_args": json.dumps(build_args or {}),
            "nydus_convert": "true" if nydus else "false",
        }

        async def _submit():
            buf.seek(0)
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self._api_url}/builds",
                    headers=headers,
                    files={"context": ("context.tar.gz", buf, "application/gzip")},
                    data=data,
                )
                response.raise_for_status()
                return response.json()

        build_data = await _with_retry("imageBuilder.submit", _submit)

        build_id = build_data.get("build_id")
        if not build_id:
            raise RuntimeError(f"No build_id in response: {build_data}")

        try:
            return await self._stream_until_done(build_id)
        except asyncio.CancelledError:
            await self.cancel(build_id)
            raise

    async def _stream_until_done(self, build_id: str) -> str:
        """
        Stream build logs via SSE until the build completes or fails.

        Retries on transient connection errors (e.g. while the build pod is
        still scheduling). Returns the image_ref on success.
        """
        url = f"{self._api_url}/builds/{build_id}/logs"
        headers = {
            "Authorization": f"Bearer {self._token}",
            "Accept": "text/event-stream",
        }
        timeout = httpx.Timeout(connect=10.0, read=None, write=10.0, pool=10.0)

        max_attempts = 60
        wait = 5.0

        for attempt in range(1, max_attempts + 1):
            try:
                async with httpx.AsyncClient(timeout=timeout) as client:
                    async with aconnect_sse(
                        client, "GET", url, headers=headers
                    ) as event_source:
                        saw_done = False
                        async for sse_event in event_source.aiter_sse():
                            data = sse_event.data
                            # JSON control events contain "done" or "error" keys
                            if data.startswith("{") and (
                                '"done"' in data or '"error"' in data
                            ):
                                try:
                                    obj = json.loads(data)
                                    if obj.get("done"):
                                        saw_done = True
                                        break
                                    if "error" in obj:
                                        raise RuntimeError(
                                            f"Build {build_id} failed: {obj['error']}"
                                        )
                                except json.JSONDecodeError:
                                    pass
                            else:
                                if self._logger:
                                    self._logger.debug(f"[image-builder] {data}")

                        if saw_done:
                            status = await self._get_status(build_id)
                            image_ref = status.get("image_ref")
                            if not image_ref:
                                raise RuntimeError(
                                    f"Build succeeded but no image_ref in status: {status}"
                                )
                            return image_ref

            except RuntimeError:
                raise
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404 and attempt < max_attempts:
                    await asyncio.sleep(wait)
                    continue
                raise
            except Exception:
                if attempt >= max_attempts:
                    raise
                await asyncio.sleep(wait)
                continue

            # Stream closed without done — retry
            if attempt >= max_attempts:
                break
            await asyncio.sleep(wait)

        raise RuntimeError(
            f"Build {build_id} log stream ended without completion "
            f"after {max_attempts} attempts"
        )

    async def cancel(self, build_id: str) -> None:
        """Cancel a running build by deleting its job."""
        headers = {"Authorization": f"Bearer {self._token}"}
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                await client.delete(
                    f"{self._api_url}/builds/{build_id}", headers=headers
                )
        except Exception as e:
            if self._logger:
                self._logger.warning(f"Failed to cancel build {build_id}: {e}")

    async def _get_status(self, build_id: str) -> dict:
        """Fetch build status JSON."""
        headers = {"Authorization": f"Bearer {self._token}"}

        async def _do():
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self._api_url}/builds/{build_id}", headers=headers
                )
                response.raise_for_status()
                return response.json()

        return await _with_retry("imageBuilder.getStatus", _do)
