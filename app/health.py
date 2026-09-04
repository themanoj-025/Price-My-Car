"""Canonical health-check helpers for the themanoj-025 portfolio.

CANONICAL COPY — this file is the single source of truth. It is synced
verbatim into portfolio repos by ``tools/sync_shared.py`` (see
``shared/README.md``). Make changes HERE, then re-run the sync; do not
edit the per-repo copies directly.

Design: per-service payloads (model loaded, facts rows, bot connected,
...) stay in each repo; this module shares the *plumbing*:

- liveness semantics — a probe that returns 200 while the process is up
- dependency checks — run a callable under a timeout and report
  up/down with latency and error detail
- readiness aggregation — all configured dependencies healthy => ready
- an optional FastAPI router factory exposing ``/health`` (liveness) and
  ``/health/ready`` (readiness; 503 when any dependency is down)

Usage (FastAPI):
    from health import create_health_router

    def _redis_up() -> None:
        get_redis().ping()

    app.include_router(create_health_router(checks={"redis": _redis_up}))

Usage (framework-agnostic):
    from health import check_dependency, aggregate_readiness

    results = [check_dependency("redis", lambda: redis.ping())]
    payload = aggregate_readiness(results)   # {"status": "ready" | "not_ready", ...}
"""

from __future__ import annotations

import time
from collections.abc import Callable, Mapping
from typing import TYPE_CHECKING, Any

__all__ = [
    "aggregate_readiness",
    "check_dependency",
    "create_health_router",
    "ok_payload",
]


def ok_payload() -> dict[str, str]:
    """Liveness payload — the process is up; always paired with HTTP 200."""
    return {"status": "ok"}


def check_dependency(
    name: str,
    probe: Callable[[], Any],
    timeout: float = 2.0,
    detail: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Run ``probe`` under ``timeout`` and summarize its health.

    Never raises: a probe exception is captured as a ``down`` result so the
    caller can aggregate it. ``detail`` carries optional per-service info
    (e.g. model load state) alongside the up/down verdict.
    """
    started = time.monotonic()
    try:
        probe()
    except Exception as e:
        # Health checks must never raise — capture the failure instead
        return {
            "name": name,
            "status": "down",
            "error": f"{type(e).__name__}: {e}",
            "latency_ms": round((time.monotonic() - started) * 1000, 1),
            **(detail or {}),
        }
    return {
        "name": name,
        "status": "up",
        "latency_ms": round((time.monotonic() - started) * 1000, 1),
        **(detail or {}),
    }


def aggregate_readiness(checks: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate dependency results into a readiness payload.

    Returns ``{"status": "ready", "checks": [...]}`` when every check is up,
    otherwise ``{"status": "not_ready", "checks": [...]}`` — the caller maps
    ``ready`` to HTTP 200 and ``not_ready`` to HTTP 503.
    """
    all_up = all(c.get("status") == "up" for c in checks)
    return {"status": "ready" if all_up else "not_ready", "checks": checks}


# ── FastAPI extras (optional) ─────────────────────────────────────────

if TYPE_CHECKING:  # pragma: no cover
    from fastapi import APIRouter, Response

try:  # fastapi is not a hard dependency of every repo
    from fastapi import APIRouter, Response  # noqa: F811
except ImportError:  # pragma: no cover
    APIRouter = None  # noqa: F811


def create_health_router(
    *,
    prefix: str = "",
    checks: Mapping[str, Callable[[], Any]] | None = None,
    timeout: float = 2.0,
) -> Any:
    """Build a FastAPI router with liveness + readiness probes.

    Routes (all unauthenticated — probes must always be reachable):
        GET {prefix}/health        — liveness, always 200 {"status": "ok"}
        GET {prefix}/health/ready  — readiness; 200 when every ``checks``
                                     probe passes, 503 otherwise

    ``checks`` maps dependency name -> probe callable. Pass ``{}`` or None
    for a liveness-only router.
    """
    if APIRouter is None:  # pragma: no cover
        raise ImportError(
            "create_health_router requires fastapi; use check_dependency/"
            "aggregate_readiness for framework-agnostic health checks."
        )

    router = APIRouter(prefix=prefix, tags=["health"])

    @router.get("/health", summary="Liveness probe")
    async def liveness() -> dict[str, str]:
        """Always returns 200 while the process is alive (Docker/k8s liveness)."""
        return ok_payload()

    @router.get("/health/ready", summary="Readiness probe")
    async def readiness(response: Response) -> dict[str, Any]:
        """200 only when every configured dependency is healthy (k8s readiness)."""
        deps = list((checks or {}).items())
        results = [check_dependency(name, probe, timeout=timeout) for name, probe in deps]
        payload = aggregate_readiness(results)
        if payload["status"] != "ready":
            response.status_code = 503
        return payload

    return router
