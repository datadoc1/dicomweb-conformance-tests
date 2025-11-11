"""
Vendor identification utilities for DICOMweb conformance runs.

This module performs best-effort identification of the PACS / DICOMweb
implementation being tested, using only information observable via HTTP
(SERVER headers, known info endpoints, JSON bodies, etc).

No credentials are persisted. Authentication values are accepted only
as function parameters and used transiently for HTTP requests.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional, Tuple
from urllib.parse import urljoin

import requests


@dataclass
class VendorProfile:
    """Structured representation of detected PACS/DICOMweb implementation."""

    vendor: str = "Unknown"
    product: str = "Unknown"
    version: str = ""
    base_url: str = ""
    detection_method: str = ""
    server_header: str = ""
    qido_signature: str = ""
    additional_hints: Dict[str, Any] = None

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        # Ensure no accidental sensitive fields are present
        data.pop("credentials", None)
        return data


def _build_auth(username: Optional[str], password: Optional[str]) -> Optional[Tuple[str, str]]:
    if username and password:
        return (username, password)
    return None


def _safe_get(
    url: str,
    auth: Optional[Tuple[str, str]] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: float = 5.0,
) -> Optional[requests.Response]:
    try:
        resp = requests.get(url, auth=auth, headers=headers or {}, timeout=timeout, verify=False)
        return resp
    except Exception:
        return None


def _extract_server_header(resp: Optional[requests.Response]) -> str:
    if not resp:
        return ""
    return resp.headers.get("Server", "") or resp.headers.get("X-Powered-By", "")


def _try_parse_json(resp: Optional[requests.Response]) -> Any:
    if not resp:
        return None
    try:
        return resp.json()
    except Exception:
        return None


def _detect_orthanc(base_url: str, auth: Optional[Tuple[str, str]]) -> Optional[VendorProfile]:
    """
    Orthanc exposes a REST API with /system endpoint containing version info.
    When reachable, we can reliably tag it.
    """
    # Common Orthanc system URL is on the base Orthanc HTTP root, not necessarily DICOMweb base.
    # Try a few candidates:
    candidates = [
        # If base_url is a DICOMweb URL like https://host/dicom-web/, go up one level.
        base_url.rstrip("/").rsplit("/dicom-web", 1)[0] + "/system",
        # Direct system under base_url (if caller already passed Orthanc root):
        urljoin(base_url, "/system"),
    ]

    for url in candidates:
        resp = _safe_get(url, auth=auth)
        data = _try_parse_json(resp)
        if isinstance(data, dict) and ("Version" in data or "OrthancVersion" in data):
            version = data.get("Version") or data.get("OrthancVersion") or ""
            return VendorProfile(
                vendor="Orthanc",
                product="Orthanc",
                version=str(version),
                base_url=base_url,
                detection_method=f"orthanc_system_api:{url}",
                server_header=_extract_server_header(resp),
                qido_signature="",
                additional_hints={
                    "api": "Orthanc /system",
                    "plugins": data.get("Plugins", []),
                },
            )

    return None


def _detect_from_qido(base_url: str, auth: Optional[Tuple[str, str]]) -> Tuple[Optional[VendorProfile], str, str, Dict[str, Any]]:
    """
    Perform a lightweight QIDO-RS query and use headers/body to infer vendor.
    Returns (profile_or_none, server_header, qido_signature, raw_probe_metadata)

    raw_probe_metadata is designed for persistence in the *_pacs_metadata.json file and
    intentionally:
      - Includes request URL and selected response headers
      - Excludes Authorization/Cookie and full body content
      - Truncates any JSON body snapshot to avoid PHI-heavy payloads
    """
    qido_url = urljoin(base_url.rstrip("/") + "/", "studies?limit=1")
    resp = _safe_get(qido_url, auth=auth, headers={"Accept": "application/dicom+json, application/json;q=0.9"})
    if not resp:
        return None, "", "", {}

    # Capture safe headers (exclude sensitive ones)
    header_blacklist = {"authorization", "proxy-authorization", "cookie", "set-cookie"}
    safe_headers = {
        k: v for k, v in resp.headers.items()
        if k.lower() not in header_blacklist
    }

    server_header = _extract_server_header(resp)
    body = _try_parse_json(resp)
    body_str = ""
    if body is not None:
        try:
            # Truncate for signature/snapshot, not full PHI payload
            body_str = json.dumps(body)[:2048]
        except Exception:
            body_str = ""

    # Simple heuristic signatures (best-effort, non-authoritative)
    signature = f"status={resp.status_code};server={server_header};len={len(body_str)}"

    raw_probe_metadata: Dict[str, Any] = {
        "probe_type": "qido_studies_limit_1",
        "request": {
            "url": qido_url,
            "method": "GET",
            "headers": {
                "Accept": "application/dicom+json, application/json;q=0.9"
            },
        },
        "response": {
            "status_code": resp.status_code,
            "headers": safe_headers,
            "body_preview": body_str,
        },
    }

    # Orthanc hint
    if "Orthanc" in server_header or (isinstance(body, dict) and "Orthanc" in json.dumps(body)):
        profile = VendorProfile(
            vendor="Orthanc",
            product="Orthanc (heuristic)",
            version="",
            base_url=base_url,
            detection_method="qido_header_or_body_contains_Orthanc",
            server_header=server_header,
            qido_signature=signature,
            additional_hints={"qido_probe": raw_probe_metadata},
        )
        return profile, server_header, signature, raw_probe_metadata

    # dcm4chee hint
    if "dcm4chee" in server_header.lower():
        profile = VendorProfile(
            vendor="dcm4chee",
            product="dcm4chee-arc (heuristic)",
            version="",
            base_url=base_url,
            detection_method="server_header_contains_dcm4chee",
            server_header=server_header,
            qido_signature=signature,
            additional_hints={"qido_probe": raw_probe_metadata},
        )
        return profile, server_header, signature, raw_probe_metadata

    # Generic Tomcat/Java hints (not strong enough to assert vendor)
    return None, server_header, signature, raw_probe_metadata


def identify_vendor(
    base_url: str,
    username: Optional[str] = None,
    password: Optional[str] = None,
) -> VendorProfile:
    """
    Identify the PACS/DICOMweb implementation for the given endpoint.

    Strategy (best-effort):
      1. Attempt known vendor-specific identification (e.g., Orthanc /system).
      2. Probe QIDO-RS /studies for headers and JSON shape.
      3. Apply simple heuristics based on headers/body.
      4. If unknown, return a VendorProfile with collected hints.

    Notes:
      - Only uses the provided credentials transiently for HTTP calls.
      - Does NOT persist credentials or sensitive data.
      - Intended to be called once per run and attached to the conformance report.
    """
    profile = VendorProfile(base_url=base_url, additional_hints={})
    auth = _build_auth(username, password)

    # 1) Explicit Orthanc detection
    orthanc_profile = _detect_orthanc(base_url, auth)
    if orthanc_profile:
        return orthanc_profile

    # 2) QIDO-based heuristics (and capture raw probe metadata)
    qido_profile, server_header, qido_sig, raw_probe = _detect_from_qido(base_url, auth)
    if qido_profile:
        # Ensure we carry the raw probe metadata through additional_hints
        if qido_profile.additional_hints is None:
            qido_profile.additional_hints = {}
        if raw_probe:
            qido_profile.additional_hints.setdefault("qido_probe", raw_probe)
        return qido_profile
    
    # 3) Fallback: unknown, but store rich hints including probe data
    profile.server_header = server_header
    profile.qido_signature = qido_sig
    profile.detection_method = "heuristic_unknown"
    profile.additional_hints = {
        "note": "Unable to confidently determine vendor; review headers and deployment docs.",
        "server_header": server_header,
        "qido_signature": qido_sig,
        "qido_probe": raw_probe,
    }
    return profile