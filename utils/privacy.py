"""Fail-closed data-transmission policy for the legal assistant.

Online provider calls remain disabled until a separate reviewed UI flow
implements explicit, one-operation/one-payload authorization.
This module intentionally exposes no environment-only bypass.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TransmissionDenied(RuntimeError):
    provider: str
    operation: str

    def __str__(self) -> str:
        # Do not include request contents, paths or provider exception details.
        return "Online AI transmission is disabled pending explicit reviewed consent."


def require_approved_transmission(provider: str, operation: str, payload: str) -> None:
    """Prevent any cloud AI request in security Phase 1, even with an API key.

    The payload is deliberately neither logged nor retained.
    A future phase must add reviewed exact-payload consent before enabling calls.
    """
    del payload
    raise TransmissionDenied(provider=provider, operation=operation)
