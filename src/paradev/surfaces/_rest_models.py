"""Validated request models loaded only with ParaDev's optional REST surface."""

from __future__ import annotations

from typing import Annotated

from typing_extensions import Self

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

from paradev.surfaces._rest_contract import NONBLANK_RUN_ID_PATTERN, desktop_build_interrupt_request_schema

NonblankRunId = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, pattern=NONBLANK_RUN_ID_PATTERN),
]


class DesktopBuildInterruptRequest(BaseModel):
    """Accept one exact build run id in camelCase or snake_case form."""

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra=desktop_build_interrupt_request_schema(),
    )

    run_id_camel: NonblankRunId | None = Field(default=None, alias="runId")
    run_id: NonblankRunId | None = None

    @model_validator(mode="after")
    def validate_exact_run_id(self) -> Self:
        """Require one unambiguous alias after string normalization."""

        if self.run_id_camel is None and self.run_id is None:
            raise ValueError("Request field 'runId' must be a non-empty string.")
        if self.run_id_camel is not None and self.run_id is not None and self.run_id_camel != self.run_id:
            raise ValueError("Request fields 'runId' and 'run_id' must match when both are provided.")
        return self

    def exact_run_id(self) -> str:
        """Return the validated normalized run id."""

        run_id = self.run_id_camel if self.run_id_camel is not None else self.run_id
        if run_id is None:
            raise ValueError("Request field 'runId' must be a non-empty string.")
        return run_id
