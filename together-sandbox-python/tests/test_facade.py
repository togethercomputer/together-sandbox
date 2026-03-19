"""Unit tests for the Together Sandbox unified facade."""

from __future__ import annotations

import os
from unittest.mock import MagicMock

import pytest

from together_sandbox.facade import _resolve_connection, Sandbox, TogetherSandbox, ExecsFacade, FilesFacade, PortsFacade
from together_sandbox.api.models.vm_start_response_data_2 import VmStartResponseData2


# ─── Helpers ──────────────────────────────────────────────────────────────────


def _make_vm_info(**overrides) -> VmStartResponseData2:
    """Build a VmStartResponseData2 with sensible defaults."""
    defaults = dict(
        bootup_type="cold",
        cluster="us-east-1",
        id_="test-sandbox-123",
        latest_pitcher_version="1.0.0",
        pitcher_manager_version="1.0.0",
        pitcher_token="pitcher-tok",
        pitcher_url="https://pitcher.example.com",
        pitcher_version="1.0.0",
        reconnect_token="reconnect-tok",
        use_pint=False,
        user_workspace_path="/home/user/workspace",
        vm_agent_type="pint",
        workspace_path="/workspace",
        pint_token=None,
        pint_url=None,
    )
    defaults.update(overrides)
    return VmStartResponseData2(**defaults)


# ─── _resolve_connection tests ────────────────────────────────────────────────


class TestResolveConnection:
    def test_prefers_pint_when_use_pint_true_and_fields_present(self):
        vm_info = _make_vm_info(
            use_pint=True,
            pint_url="https://pint.example.com",
            pint_token="pint-tok",
        )
        url, token = _resolve_connection(vm_info)
        assert url == "https://pint.example.com"
        assert token == "pint-tok"

    def test_falls_back_to_pitcher_when_use_pint_false(self):
        vm_info = _make_vm_info(
            use_pint=False,
            pint_url="https://pint.example.com",
            pint_token="pint-tok",
        )
        url, token = _resolve_connection(vm_info)
        assert url == "https://pitcher.example.com"
        assert token == "pitcher-tok"

    def test_falls_back_to_pitcher_when_pint_url_none(self):
        vm_info = _make_vm_info(
            use_pint=True,
            pint_url=None,
            pint_token=None,
        )
        url, token = _resolve_connection(vm_info)
        assert url == "https://pitcher.example.com"
        assert token == "pitcher-tok"

    def test_falls_back_to_pitcher_when_pint_token_none(self):
        vm_info = _make_vm_info(
            use_pint=True,
            pint_url="https://pint.example.com",
            pint_token=None,
        )
        url, token = _resolve_connection(vm_info)
        assert url == "https://pitcher.example.com"
        assert token == "pitcher-tok"


# ─── TogetherSandbox tests ───────────────────────────────────────────────────


class TestTogetherSandbox:
    def test_raises_without_api_key(self, monkeypatch):
        monkeypatch.delenv("TOGETHER_API_KEY", raising=False)
        with pytest.raises(ValueError, match="api_key must be provided"):
            TogetherSandbox()

    def test_reads_api_key_from_env(self, monkeypatch):
        monkeypatch.setenv("TOGETHER_API_KEY", "test-key-from-env")
        sdk = TogetherSandbox()
        assert sdk.sandboxes is not None

    def test_accepts_explicit_api_key(self, monkeypatch):
        monkeypatch.delenv("TOGETHER_API_KEY", raising=False)
        sdk = TogetherSandbox(api_key="explicit-key")
        assert sdk.sandboxes is not None


# ─── Sandbox tests ────────────────────────────────────────────────────


class TestSandbox:
    def test_id_property(self):
        vm_info = _make_vm_info(id_="test-id-456")
        mock_sandbox_client = MagicMock()
        mock_api_client = MagicMock()
        sb = Sandbox(vm_info, mock_sandbox_client, mock_api_client)
        assert sb.id == "test-id-456"

    def test_vm_info_property(self):
        vm_info = _make_vm_info()
        sb = Sandbox(vm_info, MagicMock(), MagicMock())
        assert sb.vm_info is vm_info

    def test_delegates_files_namespace(self):
        mock_sandbox_client = MagicMock()
        sb = Sandbox(_make_vm_info(), mock_sandbox_client, MagicMock())
        assert isinstance(sb.files, FilesFacade)

    def test_delegates_directories_namespace(self):
        mock_sandbox_client = MagicMock()
        sb = Sandbox(_make_vm_info(), mock_sandbox_client, MagicMock())
        assert sb.directories is mock_sandbox_client.directories

    def test_delegates_execs_namespace(self):
        mock_sandbox_client = MagicMock()
        sb = Sandbox(_make_vm_info(), mock_sandbox_client, MagicMock())
        assert isinstance(sb.execs, ExecsFacade)

    def test_delegates_tasks_namespace(self):
        mock_sandbox_client = MagicMock()
        sb = Sandbox(_make_vm_info(), mock_sandbox_client, MagicMock())
        assert sb.tasks is mock_sandbox_client.tasks

    def test_delegates_ports_namespace(self):
        mock_sandbox_client = MagicMock()
        sb = Sandbox(_make_vm_info(), mock_sandbox_client, MagicMock())
        assert isinstance(sb.ports, PortsFacade)


