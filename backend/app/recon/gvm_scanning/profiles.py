"""GVM scan profile helpers."""
from __future__ import annotations

from typing import Dict

from .schemas import GvmScanProfile


DEFAULT_PROFILE_NAMES: Dict[GvmScanProfile, str] = {
    GvmScanProfile.DISCOVERY: "Discovery",
    GvmScanProfile.FULL_AND_FAST: "Full and fast",
    GvmScanProfile.FULL_AND_VERY_DEEP: "Full and very deep",
    GvmScanProfile.HOST_DISCOVERY: "Host Discovery",
    GvmScanProfile.SYSTEM_DISCOVERY: "System Discovery",
    GvmScanProfile.WEB_APPLICATION: "Web Application Tests",
    GvmScanProfile.DATABASE: "Database Servers",
}


def profile_display_name(profile: GvmScanProfile) -> str:
    """Return the display name used by GVM for a profile."""
    return DEFAULT_PROFILE_NAMES.get(profile, profile.value)
