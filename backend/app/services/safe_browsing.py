"""
Google Safe Browsing integration with strict timeout, domain cache,
and graceful error handling.
"""
import logging
from functools import lru_cache

import requests

from app.config import SAFE_BROWSING_API_KEY, SAFE_BROWSING_TIMEOUT

logger = logging.getLogger(__name__)

SAFE_BROWSING_URL = "https://safebrowsing.googleapis.com/v4/threatMatches:find"


@lru_cache(maxsize=256)
def _cached_safe_browsing_lookup(url: str) -> str:
    """
    Perform the actual Safe Browsing API call.
    Cached per URL to avoid repeated API calls within the process lifetime.
    """
    try:
        payload = {
            "client": {
                "clientId": "fake-job-detector",
                "clientVersion": "1.0.0",
            },
            "threatInfo": {
                "threatTypes": [
                    "MALWARE",
                    "SOCIAL_ENGINEERING",
                    "UNWANTED_SOFTWARE",
                    "POTENTIALLY_HARMFUL_APPLICATION",
                ],
                "platformTypes": ["ANY_PLATFORM"],
                "threatEntryTypes": ["URL"],
                "threatEntries": [{"url": url}],
            },
        }

        response = requests.post(
            SAFE_BROWSING_URL,
            params={"key": SAFE_BROWSING_API_KEY},
            json=payload,
            timeout=SAFE_BROWSING_TIMEOUT,
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("matches"):
                logger.info(f"Safe Browsing: MALICIOUS — {url}")
                return "malicious"
            return "clean"
        elif response.status_code == 429:
            logger.warning("Safe Browsing: quota exceeded (429)")
            return "error"
        else:
            logger.warning(
                f"Safe Browsing: HTTP {response.status_code} for {url}"
            )
            return "error"

    except requests.Timeout:
        logger.warning(f"Safe Browsing: timeout for {url}")
        return "error"
    except requests.RequestException as e:
        logger.warning(f"Safe Browsing: request failed — {e}")
        return "error"
    except Exception as e:
        logger.error(f"Safe Browsing: unexpected error — {e}")
        return "error"


def check_safe_browsing(url: str) -> str:
    """
    Check a URL against Google Safe Browsing API v4.

    Returns:
        "clean"     — no threats found
        "malicious" — threats detected
        "error"     — API error or timeout
        "skipped"   — no API key configured
    """
    if not SAFE_BROWSING_API_KEY:
        return "skipped"

    if not url or not url.strip():
        return "skipped"

    return _cached_safe_browsing_lookup(url.strip())
