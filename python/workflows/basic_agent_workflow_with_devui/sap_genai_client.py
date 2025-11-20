"""Utility helpers to wire Microsoft Agent Framework agents to SAP AI Core."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, Iterable, Optional

from dotenv import load_dotenv

from agent_framework.azure import AzureOpenAIChatClient

try:
    from ai_core_sdk.ai_core_v2_client import AICoreV2Client
except ImportError as exc:  # pragma: no cover - env guidance
    raise ImportError(
        "Package 'ai-core-sdk' is required. Install with 'pip install ai-core-sdk'."
    ) from exc

try:
    from gen_ai_hub.proxy import GenAIHubProxyClient
except ImportError as exc:  # pragma: no cover - env guidance
    raise ImportError(
        "Package 'generative-ai-hub-sdk' is required. Install with 'pip install generative-ai-hub-sdk'."
    ) from exc


load_dotenv()


@dataclass(frozen=True)
class SapAiCoreSettings:
    """Configuration needed to talk to SAP AI Core via GenAI Hub."""

    resource_group: str = os.getenv("AICORE_RESOURCE_GROUP", "default")
    scenario_id: str = os.getenv("AICORE_SCENARIO_ID", "foundation-models")
    deployment_name: Optional[str] = os.getenv("AICORE_DEPLOYMENT_NAME")
    api_version: str = os.getenv("AICORE_API_VERSION", "2023-05-15")

    def default_headers(self) -> Dict[str, str]:
        return {"AI-Resource-Group": self.resource_group}


def _get_deployment_url(settings: SapAiCoreSettings) -> str:
    client = AICoreV2Client.from_env()
    response = client.deployment.query(
        resource_group=settings.resource_group,
        scenario_id=settings.scenario_id,
    )
    resources: Iterable[Any] = getattr(response, "resources", []) or []

    selected = None
    for candidate in resources:
        candidate_name = getattr(candidate, "name", None) or getattr(candidate, "id", None)
        if settings.deployment_name and candidate_name != settings.deployment_name:
            continue
        selected = candidate
        break

    if not selected:
        selected = next(iter(resources), None)

    if not selected:
        raise RuntimeError(
            "No SAP AI Core deployments were returned. Verify the resource group and scenario id."
        )

    url = getattr(selected, "deployment_url", None)
    if not url:
        raise RuntimeError("Selected deployment is missing 'deployment_url'.")
    return url


def _infer_deployment_name(url: str) -> Optional[str]:
    parts = [part for part in url.rstrip("/").split("/") if part]
    if "deployments" in parts:
        idx = parts.index("deployments")
        if idx + 1 < len(parts):
            return parts[idx + 1]
    return None


def _get_bearer_token(settings: SapAiCoreSettings) -> str:
    proxy = GenAIHubProxyClient(resource_group=settings.resource_group)
    token = proxy.get_ai_core_token()
    return token.replace("Bearer ", "")


def build_sap_chat_client(settings: Optional[SapAiCoreSettings] = None) -> AzureOpenAIChatClient:
    """Return an AzureOpenAIChatClient configured to route calls through SAP AI Core."""

    settings = settings or SapAiCoreSettings()
    deployment_url = _get_deployment_url(settings)
    deployment_name = settings.deployment_name or _infer_deployment_name(deployment_url)
    if not deployment_name:
        raise RuntimeError(
            "Set AICORE_DEPLOYMENT_NAME or ensure the deployment URL contains '/deployments/<name>'."
        )

    token = _get_bearer_token(settings)

    return AzureOpenAIChatClient(
        deployment_name=deployment_name,
        base_url=deployment_url,
        api_key=token,
        api_version=settings.api_version,
        default_headers=settings.default_headers(),
    )


__all__ = ["SapAiCoreSettings", "build_sap_chat_client"]
