# -*- coding: utf-8 -*-
"""
Auto-updater: checks GitHub releases for new versions.
"""

from __future__ import annotations

import json
import urllib.request
import urllib.error
import re
from typing import Optional, Tuple
from dataclasses import dataclass

from PySide6.QtCore import QThread, Signal, QObject


GITHUB_API_RELEASES = "https://api.github.com/repos/realLivedInCorner/2-Pyramid/releases"
GITHUB_RELEASES_PAGE = "https://github.com/realLivedInCorner/2-Pyramid/releases"

CURRENT_VERSION = "1.6.0"


@dataclass
class ReleaseInfo:
    tag_name: str
    version: str          # parsed numeric version, e.g. "1.7.0"
    name: str
    body: str
    html_url: str
    assets: list


def _parse_version(tag_name: str) -> str:
    """Extract a clean version string from a tag like 'v1.7.0' or '1.7.0Stable'."""
    tag = tag_name.lstrip("v").lstrip("V")
    match = re.search(r"(\d+\.\d+\.\d+(?:\.\d+)?)", tag)
    if match:
        return match.group(1)
    # fallback: remove common prefixes / suffixes
    tag = tag.replace("Stable", "").replace("Beta", "").replace("Alpha", "").strip()
    return tag


def _version_tuple(version: str) -> Tuple[int, ...]:
    """Convert a version string to a comparable tuple."""
    try:
        return tuple(int(p) for p in version.split("."))
    except (ValueError, TypeError):
        return (0,)


def is_newer(latest_version: str, current_version: str) -> bool:
    """Return True if latest_version > current_version."""
    return _version_tuple(latest_version) > _version_tuple(current_version)


class UpdateCheckWorker(QObject):
    """QObject-based worker that runs in a QThread to check for updates."""

    finished = Signal(object)   # emits ReleaseInfo | None
    error = Signal(str)

    def run(self):
        try:
            release = self._fetch_latest()
            self.finished.emit(release)
        except Exception as exc:
            self.error.emit(str(exc))

    def _fetch_latest(self) -> Optional[ReleaseInfo]:
        req = urllib.request.Request(
            GITHUB_API_RELEASES + "?per_page=1",
            headers={
                "Accept": "application/vnd.github+json",
                "User-Agent": "KyanitePackTool-Updater/1.0",
            },
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            if resp.status != 200:
                raise RuntimeError(f"GitHub API returned HTTP {resp.status}")
            data = json.loads(resp.read().decode("utf-8"))

        if not data:
            return None

        latest = data[0]
        tag = latest.get("tag_name", "")
        version = _parse_version(tag)

        return ReleaseInfo(
            tag_name=tag,
            version=version,
            name=latest.get("name", tag),
            body=latest.get("body", ""),
            html_url=latest.get("html_url", GITHUB_RELEASES_PAGE),
            assets=latest.get("assets", []),
        )


def check_for_updates_blocking() -> Optional[ReleaseInfo]:
    """Synchronous check — use only in a background thread."""
    worker = UpdateCheckWorker()
    # We can't use signals here, so duplicate the logic.
    try:
        return worker._fetch_latest()
    except Exception:
        return None
