"""E2E tests for sandbox exec (command execution) operations."""

from __future__ import annotations

import asyncio
import sys

import pytest

from together_sandbox import Sandbox, CreateExecRequest, ExecStdoutType
from together_sandbox.sandbox.models.create_exec_request_env import CreateExecRequestEnv
from together_sandbox.sandbox.models.exec_stdin import ExecStdin
from together_sandbox.sandbox.models.exec_stdin_type import ExecStdinType
from together_sandbox.sandbox.models.update_exec_request import UpdateExecRequest
from together_sandbox.sandbox.models.update_exec_request_status import (
    UpdateExecRequestStatus,
)
from .helpers import retry_until


@pytest.mark.asyncio
class TestSandboxExecs:
    """E2E tests for creating and managing command executions."""

    async def test_create_exec(self, sandbox: Sandbox):
        """Test creating an exec"""
        exec_item = await sandbox.execs.create(
            CreateExecRequest(command="echo", args=["hello"])
        )
        assert exec_item.id
        assert exec_item.command == "echo"
        assert exec_item.args == ["hello"]
        assert exec_item.pid >= 0

    async def test_create_and_get_exec(self, sandbox: Sandbox):
        """Test creating and getting exec"""
        exec_item = await sandbox.execs.create(
            CreateExecRequest(command="echo", args=["hello"])
        )
        gotten_exec_item = await sandbox.execs.get(exec_item.id)

        assert gotten_exec_item.id == exec_item.id
        assert gotten_exec_item.command == "echo"
        assert gotten_exec_item.args == ["hello"]

    async def test_create_and_list_exec(self, sandbox: Sandbox):
        """Test creating an exec and listing it."""
        exec_item = await sandbox.execs.create(
            CreateExecRequest(command="echo", args=["hello"], autorun=False)
        )
        exec_list = await sandbox.execs.list()

        assert exec_list[0].id == exec_item.id

    async def test_delete_exec(self, sandbox: Sandbox):
        """Test deleting an exec."""
        exec_item = await sandbox.execs.create(
            CreateExecRequest(command="echo", args=["hello"], autorun=False)
        )
        await sandbox.execs.delete(exec_item.id)

        with pytest.raises(RuntimeError, match="Failed to execs.get"):
            await sandbox.execs.get(exec_item.id)

    async def test_get_output(self, sandbox: Sandbox):
        """Test getting exec output."""
        exec_item = await sandbox.execs.create(
            CreateExecRequest(command="echo", args=["hello"])
        )

        await retry_until(
            fn=lambda: sandbox.execs.get_output(exec_item.id),
            predicate=lambda r: any("hello" in item.output for item in r),
            timeout=10.0,
        )

    async def test_exec_exit_code(self, sandbox: Sandbox):
        """Test that exec exit codes are captured correctly."""
        exec_item = await sandbox.execs.create(
            CreateExecRequest(command="sh", args=["-c", "exit 42"])
        )

        await retry_until(
            fn=lambda: sandbox.execs.get_output(exec_item.id),
            predicate=lambda r: any(item.exit_code == 42 for item in r),
            timeout=10.0,
        )

    async def test_exec_stdout_vs_stderr(self, sandbox: Sandbox):
        """Test distinguishing stdout vs stderr output types."""
        exec_item = await sandbox.execs.create(
            CreateExecRequest(command="echo", args=["hello"])
        )

        await retry_until(
            fn=lambda: sandbox.execs.get_output(exec_item.id),
            predicate=lambda r: any(
                "hello" in item.output and ExecStdoutType.STDOUT in item.type_
                for item in r
            ),
            timeout=10.0,
        )

    async def test_exec_with_cwd(self, sandbox: Sandbox):
        """Test exec with cwd (working directory)."""
        await sandbox.directories.create("/exec-cwd-test")
        exec_item = await sandbox.execs.create(
            CreateExecRequest(command="pwd", args=[], cwd="/exec-cwd-test")
        )

        await retry_until(
            fn=lambda: sandbox.execs.get_output(exec_item.id),
            predicate=lambda r: any("/exec-cwd-test" in item.output for item in r),
            timeout=10.0,
        )

    async def test_exec_with_env(self, sandbox: Sandbox):
        """Test exec with custom environment variables."""
        env = CreateExecRequestEnv.from_dict({"MY_VAR": "test_value"})
        exec_item = await sandbox.execs.create(
            CreateExecRequest(command="sh", args=["-c", "echo $MY_VAR"], env=env)
        )

        await retry_until(
            fn=lambda: sandbox.execs.get_output(exec_item.id),
            predicate=lambda r: any("test_value" in item.output for item in r),
            timeout=10.0,
        )

    async def test_exec_with_args(self, sandbox: Sandbox):
        """Test that exec args are forwarded correctly."""
        exec_item = await sandbox.execs.create(
            CreateExecRequest(command="echo", args=["one", "two", "three"])
        )

        await retry_until(
            fn=lambda: sandbox.execs.get_output(exec_item.id),
            predicate=lambda r: any(
                all(token in item.output for token in ["one", "two", "three"])
                for item in r
            ),
            timeout=10.0,
        )

    async def test_exec_autorun_false(self, sandbox: Sandbox):
        """Test that exec with autorun=False does not run immediately."""
        exec_item = await sandbox.execs.create(
            CreateExecRequest(command="sleep", args=["5"], autorun=False)
        )
        item = await sandbox.execs.get(exec_item.id)
        assert item.status != "running"

    async def test_update_exec_to_running(self, sandbox: Sandbox):
        """Test updating exec status to running."""
        exec_item = await sandbox.execs.create(
            CreateExecRequest(command="sleep", args=["5"], autorun=False)
        )
        item = await sandbox.execs.get(exec_item.id)
        assert item.status != "running"

        await sandbox.execs.update(
            exec_item.id,
            UpdateExecRequest(status=UpdateExecRequestStatus.RUNNING),
        )

        await retry_until(
            fn=lambda: sandbox.execs.get(exec_item.id),
            predicate=lambda item: item.status == "RUNNING",
            timeout=10.0,
        )

    async def test_stream_output(self, sandbox: Sandbox):
        """Test streaming exec output via SSE."""
        exec_item = await sandbox.execs.create(
            CreateExecRequest(command="echo", args=["streaming test"])
        )
        events = []

        async def collect_event():
            async for event in sandbox.execs.stream_output(exec_item.id):
                events.append(event)
                return

        async with asyncio.timeout(10):
            await collect_event()

        assert len(events) > 0

    async def test_stream_list(self, sandbox: Sandbox):
        """Test streaming exec list via SSE."""
        events = []

        async def collect_event():
            async for event in sandbox.execs.stream_list():
                events.append(event)
                return

        async with asyncio.timeout(10):
            await collect_event()

        assert len(events) > 0

    async def test_send_stdin(self, sandbox: Sandbox):
        """Test sending stdin to an interactive exec."""
        exec_item = await sandbox.execs.create(
            CreateExecRequest(command="cat", args=[], interactive=True)
        )
        await sandbox.execs.send_stdin(
            exec_item.id,
            ExecStdin(type_=ExecStdinType.STDIN, input_="hello stdin\n"),
        )
        # Small delay to let the process respond
        await asyncio.sleep(0.5)

        await retry_until(
            fn=lambda: sandbox.execs.get_output(exec_item.id),
            predicate=lambda r: any("hello stdin" in item.output for item in r),
            timeout=10.0,
        )
