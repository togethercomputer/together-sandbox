from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.sandbox_recovery_status_type_1 import SandboxRecoveryStatusType1
from ..models.sandbox_recovery_status_type_2_type_1 import (
    SandboxRecoveryStatusType2Type1,
)
from ..models.sandbox_recovery_status_type_3_type_1 import (
    SandboxRecoveryStatusType3Type1,
)
from ..models.sandbox_requested_stop_type_type_1 import SandboxRequestedStopTypeType1
from ..models.sandbox_requested_stop_type_type_2_type_1 import (
    SandboxRequestedStopTypeType2Type1,
)
from ..models.sandbox_requested_stop_type_type_3_type_1 import (
    SandboxRequestedStopTypeType3Type1,
)
from ..models.sandbox_start_type_type_1 import SandboxStartTypeType1
from ..models.sandbox_start_type_type_2_type_1 import SandboxStartTypeType2Type1
from ..models.sandbox_start_type_type_3_type_1 import SandboxStartTypeType3Type1
from ..models.sandbox_status import SandboxStatus
from ..models.sandbox_stop_reason_type_1 import SandboxStopReasonType1
from ..models.sandbox_stop_reason_type_2_type_1 import SandboxStopReasonType2Type1
from ..models.sandbox_stop_reason_type_3_type_1 import SandboxStopReasonType3Type1

T = TypeVar("T", bound="Sandbox")


@_attrs_define
class Sandbox:
    """
    Attributes:
        id (str): Short identifier (6–8 characters).
        project_id (str):
        status (SandboxStatus):
        ephemeral (bool):
        cluster_name (str):
        current_version_number (int):
        next_version_number (int):
        millicpu (int): CPU allocation in millicpu.
        gpu (int):
        memory_bytes (int):
        disk_bytes (int):
        version_count (int):
        agent_version (str):
        agent_type (str):
        agent_token (str):
        agent_url (str):
        created_at (datetime.datetime):
        start_requested_at (datetime.datetime | None):
        start_type (None | SandboxStartTypeType1 | SandboxStartTypeType2Type1 | SandboxStartTypeType3Type1):
        started_at (datetime.datetime | None):
        stop_requested_at (datetime.datetime | None):
        requested_stop_type (None | SandboxRequestedStopTypeType1 | SandboxRequestedStopTypeType2Type1 |
            SandboxRequestedStopTypeType3Type1):
        stopped_at (datetime.datetime | None):
        stop_reason (None | SandboxStopReasonType1 | SandboxStopReasonType2Type1 | SandboxStopReasonType3Type1):
        specs_updated_at (datetime.datetime | None):
        recovery_status (None | SandboxRecoveryStatusType1 | SandboxRecoveryStatusType2Type1 |
            SandboxRecoveryStatusType3Type1):
        recovery_started_at (datetime.datetime | None):
        recovery_finished_at (datetime.datetime | None):
        updated_at (datetime.datetime):
    """

    id: str
    project_id: str
    status: SandboxStatus
    ephemeral: bool
    cluster_name: str
    current_version_number: int
    next_version_number: int
    millicpu: int
    gpu: int
    memory_bytes: int
    disk_bytes: int
    version_count: int
    agent_version: str
    agent_type: str
    agent_token: str
    agent_url: str
    created_at: datetime.datetime
    start_requested_at: datetime.datetime | None
    start_type: (
        None
        | SandboxStartTypeType1
        | SandboxStartTypeType2Type1
        | SandboxStartTypeType3Type1
    )
    started_at: datetime.datetime | None
    stop_requested_at: datetime.datetime | None
    requested_stop_type: (
        None
        | SandboxRequestedStopTypeType1
        | SandboxRequestedStopTypeType2Type1
        | SandboxRequestedStopTypeType3Type1
    )
    stopped_at: datetime.datetime | None
    stop_reason: (
        None
        | SandboxStopReasonType1
        | SandboxStopReasonType2Type1
        | SandboxStopReasonType3Type1
    )
    specs_updated_at: datetime.datetime | None
    recovery_status: (
        None
        | SandboxRecoveryStatusType1
        | SandboxRecoveryStatusType2Type1
        | SandboxRecoveryStatusType3Type1
    )
    recovery_started_at: datetime.datetime | None
    recovery_finished_at: datetime.datetime | None
    updated_at: datetime.datetime
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        project_id = self.project_id

        status = self.status.value

        ephemeral = self.ephemeral

        cluster_name = self.cluster_name

        current_version_number = self.current_version_number

        next_version_number = self.next_version_number

        millicpu = self.millicpu

        gpu = self.gpu

        memory_bytes = self.memory_bytes

        disk_bytes = self.disk_bytes

        version_count = self.version_count

        agent_version = self.agent_version

        agent_type = self.agent_type

        agent_token = self.agent_token

        agent_url = self.agent_url

        created_at = self.created_at.isoformat()

        start_requested_at: None | str
        if isinstance(self.start_requested_at, datetime.datetime):
            start_requested_at = self.start_requested_at.isoformat()
        else:
            start_requested_at = self.start_requested_at

        start_type: None | str
        if isinstance(self.start_type, SandboxStartTypeType1):
            start_type = self.start_type.value
        elif isinstance(self.start_type, SandboxStartTypeType2Type1):
            start_type = self.start_type.value
        elif isinstance(self.start_type, SandboxStartTypeType3Type1):
            start_type = self.start_type.value
        else:
            start_type = self.start_type

        started_at: None | str
        if isinstance(self.started_at, datetime.datetime):
            started_at = self.started_at.isoformat()
        else:
            started_at = self.started_at

        stop_requested_at: None | str
        if isinstance(self.stop_requested_at, datetime.datetime):
            stop_requested_at = self.stop_requested_at.isoformat()
        else:
            stop_requested_at = self.stop_requested_at

        requested_stop_type: None | str
        if isinstance(self.requested_stop_type, SandboxRequestedStopTypeType1):
            requested_stop_type = self.requested_stop_type.value
        elif isinstance(self.requested_stop_type, SandboxRequestedStopTypeType2Type1):
            requested_stop_type = self.requested_stop_type.value
        elif isinstance(self.requested_stop_type, SandboxRequestedStopTypeType3Type1):
            requested_stop_type = self.requested_stop_type.value
        else:
            requested_stop_type = self.requested_stop_type

        stopped_at: None | str
        if isinstance(self.stopped_at, datetime.datetime):
            stopped_at = self.stopped_at.isoformat()
        else:
            stopped_at = self.stopped_at

        stop_reason: None | str
        if isinstance(self.stop_reason, SandboxStopReasonType1):
            stop_reason = self.stop_reason.value
        elif isinstance(self.stop_reason, SandboxStopReasonType2Type1):
            stop_reason = self.stop_reason.value
        elif isinstance(self.stop_reason, SandboxStopReasonType3Type1):
            stop_reason = self.stop_reason.value
        else:
            stop_reason = self.stop_reason

        specs_updated_at: None | str
        if isinstance(self.specs_updated_at, datetime.datetime):
            specs_updated_at = self.specs_updated_at.isoformat()
        else:
            specs_updated_at = self.specs_updated_at

        recovery_status: None | str
        if isinstance(self.recovery_status, SandboxRecoveryStatusType1):
            recovery_status = self.recovery_status.value
        elif isinstance(self.recovery_status, SandboxRecoveryStatusType2Type1):
            recovery_status = self.recovery_status.value
        elif isinstance(self.recovery_status, SandboxRecoveryStatusType3Type1):
            recovery_status = self.recovery_status.value
        else:
            recovery_status = self.recovery_status

        recovery_started_at: None | str
        if isinstance(self.recovery_started_at, datetime.datetime):
            recovery_started_at = self.recovery_started_at.isoformat()
        else:
            recovery_started_at = self.recovery_started_at

        recovery_finished_at: None | str
        if isinstance(self.recovery_finished_at, datetime.datetime):
            recovery_finished_at = self.recovery_finished_at.isoformat()
        else:
            recovery_finished_at = self.recovery_finished_at

        updated_at = self.updated_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "project_id": project_id,
                "status": status,
                "ephemeral": ephemeral,
                "cluster_name": cluster_name,
                "current_version_number": current_version_number,
                "next_version_number": next_version_number,
                "millicpu": millicpu,
                "gpu": gpu,
                "memory_bytes": memory_bytes,
                "disk_bytes": disk_bytes,
                "version_count": version_count,
                "agent_version": agent_version,
                "agent_type": agent_type,
                "agent_token": agent_token,
                "agent_url": agent_url,
                "created_at": created_at,
                "start_requested_at": start_requested_at,
                "start_type": start_type,
                "started_at": started_at,
                "stop_requested_at": stop_requested_at,
                "requested_stop_type": requested_stop_type,
                "stopped_at": stopped_at,
                "stop_reason": stop_reason,
                "specs_updated_at": specs_updated_at,
                "recovery_status": recovery_status,
                "recovery_started_at": recovery_started_at,
                "recovery_finished_at": recovery_finished_at,
                "updated_at": updated_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        project_id = d.pop("project_id")

        status = SandboxStatus(d.pop("status"))

        ephemeral = d.pop("ephemeral")

        cluster_name = d.pop("cluster_name")

        current_version_number = d.pop("current_version_number")

        next_version_number = d.pop("next_version_number")

        millicpu = d.pop("millicpu")

        gpu = d.pop("gpu")

        memory_bytes = d.pop("memory_bytes")

        disk_bytes = d.pop("disk_bytes")

        version_count = d.pop("version_count")

        agent_version = d.pop("agent_version")

        agent_type = d.pop("agent_type")

        agent_token = d.pop("agent_token")

        agent_url = d.pop("agent_url")

        created_at = isoparse(d.pop("created_at"))

        def _parse_start_requested_at(data: object) -> datetime.datetime | None:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                start_requested_at_type_0 = isoparse(data)

                return start_requested_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None, data)

        start_requested_at = _parse_start_requested_at(d.pop("start_requested_at"))

        def _parse_start_type(
            data: object,
        ) -> (
            None
            | SandboxStartTypeType1
            | SandboxStartTypeType2Type1
            | SandboxStartTypeType3Type1
        ):
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                start_type_type_1 = SandboxStartTypeType1(data)

                return start_type_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, str):
                    raise TypeError()
                start_type_type_2_type_1 = SandboxStartTypeType2Type1(data)

                return start_type_type_2_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, str):
                    raise TypeError()
                start_type_type_3_type_1 = SandboxStartTypeType3Type1(data)

                return start_type_type_3_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(
                None
                | SandboxStartTypeType1
                | SandboxStartTypeType2Type1
                | SandboxStartTypeType3Type1,
                data,
            )

        start_type = _parse_start_type(d.pop("start_type"))

        def _parse_started_at(data: object) -> datetime.datetime | None:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                started_at_type_0 = isoparse(data)

                return started_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None, data)

        started_at = _parse_started_at(d.pop("started_at"))

        def _parse_stop_requested_at(data: object) -> datetime.datetime | None:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                stop_requested_at_type_0 = isoparse(data)

                return stop_requested_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None, data)

        stop_requested_at = _parse_stop_requested_at(d.pop("stop_requested_at"))

        def _parse_requested_stop_type(
            data: object,
        ) -> (
            None
            | SandboxRequestedStopTypeType1
            | SandboxRequestedStopTypeType2Type1
            | SandboxRequestedStopTypeType3Type1
        ):
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                requested_stop_type_type_1 = SandboxRequestedStopTypeType1(data)

                return requested_stop_type_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, str):
                    raise TypeError()
                requested_stop_type_type_2_type_1 = SandboxRequestedStopTypeType2Type1(
                    data
                )

                return requested_stop_type_type_2_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, str):
                    raise TypeError()
                requested_stop_type_type_3_type_1 = SandboxRequestedStopTypeType3Type1(
                    data
                )

                return requested_stop_type_type_3_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(
                None
                | SandboxRequestedStopTypeType1
                | SandboxRequestedStopTypeType2Type1
                | SandboxRequestedStopTypeType3Type1,
                data,
            )

        requested_stop_type = _parse_requested_stop_type(d.pop("requested_stop_type"))

        def _parse_stopped_at(data: object) -> datetime.datetime | None:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                stopped_at_type_0 = isoparse(data)

                return stopped_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None, data)

        stopped_at = _parse_stopped_at(d.pop("stopped_at"))

        def _parse_stop_reason(
            data: object,
        ) -> (
            None
            | SandboxStopReasonType1
            | SandboxStopReasonType2Type1
            | SandboxStopReasonType3Type1
        ):
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                stop_reason_type_1 = SandboxStopReasonType1(data)

                return stop_reason_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, str):
                    raise TypeError()
                stop_reason_type_2_type_1 = SandboxStopReasonType2Type1(data)

                return stop_reason_type_2_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, str):
                    raise TypeError()
                stop_reason_type_3_type_1 = SandboxStopReasonType3Type1(data)

                return stop_reason_type_3_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(
                None
                | SandboxStopReasonType1
                | SandboxStopReasonType2Type1
                | SandboxStopReasonType3Type1,
                data,
            )

        stop_reason = _parse_stop_reason(d.pop("stop_reason"))

        def _parse_specs_updated_at(data: object) -> datetime.datetime | None:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                specs_updated_at_type_0 = isoparse(data)

                return specs_updated_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None, data)

        specs_updated_at = _parse_specs_updated_at(d.pop("specs_updated_at"))

        def _parse_recovery_status(
            data: object,
        ) -> (
            None
            | SandboxRecoveryStatusType1
            | SandboxRecoveryStatusType2Type1
            | SandboxRecoveryStatusType3Type1
        ):
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                recovery_status_type_1 = SandboxRecoveryStatusType1(data)

                return recovery_status_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, str):
                    raise TypeError()
                recovery_status_type_2_type_1 = SandboxRecoveryStatusType2Type1(data)

                return recovery_status_type_2_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, str):
                    raise TypeError()
                recovery_status_type_3_type_1 = SandboxRecoveryStatusType3Type1(data)

                return recovery_status_type_3_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(
                None
                | SandboxRecoveryStatusType1
                | SandboxRecoveryStatusType2Type1
                | SandboxRecoveryStatusType3Type1,
                data,
            )

        recovery_status = _parse_recovery_status(d.pop("recovery_status"))

        def _parse_recovery_started_at(data: object) -> datetime.datetime | None:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                recovery_started_at_type_0 = isoparse(data)

                return recovery_started_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None, data)

        recovery_started_at = _parse_recovery_started_at(d.pop("recovery_started_at"))

        def _parse_recovery_finished_at(data: object) -> datetime.datetime | None:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                recovery_finished_at_type_0 = isoparse(data)

                return recovery_finished_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None, data)

        recovery_finished_at = _parse_recovery_finished_at(
            d.pop("recovery_finished_at")
        )

        updated_at = isoparse(d.pop("updated_at"))

        sandbox = cls(
            id=id,
            project_id=project_id,
            status=status,
            ephemeral=ephemeral,
            cluster_name=cluster_name,
            current_version_number=current_version_number,
            next_version_number=next_version_number,
            millicpu=millicpu,
            gpu=gpu,
            memory_bytes=memory_bytes,
            disk_bytes=disk_bytes,
            version_count=version_count,
            agent_version=agent_version,
            agent_type=agent_type,
            agent_token=agent_token,
            agent_url=agent_url,
            created_at=created_at,
            start_requested_at=start_requested_at,
            start_type=start_type,
            started_at=started_at,
            stop_requested_at=stop_requested_at,
            requested_stop_type=requested_stop_type,
            stopped_at=stopped_at,
            stop_reason=stop_reason,
            specs_updated_at=specs_updated_at,
            recovery_status=recovery_status,
            recovery_started_at=recovery_started_at,
            recovery_finished_at=recovery_finished_at,
            updated_at=updated_at,
        )

        sandbox.additional_properties = d
        return sandbox

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
