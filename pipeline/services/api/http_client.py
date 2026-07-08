"""
http_client.py
--------------
Purpose  : Thin HTTP client for posting detection payloads to the REST API.
"""

import logging
import time
from typing import Any, Dict

import requests

from pipeline.services.api.config import BACKEND_URL, API_KEY, TIMEOUT, MAX_RETRIES, RETRY_BASE

logger = logging.getLogger(__name__)


class BackendHTTPClient:
    """
    Thin HTTP client for posting detection payloads to the Node.js REST API.
    Thread-safe: uses a requests.Session with connection pooling.
    Retries up to MAX_RETRIES times with exponential backoff on 5xx / timeout.
    """

    _DETECTION_ENDPOINT = "/api/detection"

    def __init__(
        self,
        base_url:    str = BACKEND_URL,
        api_key:     str = API_KEY,
        timeout:     int = TIMEOUT,
        max_retries: int = MAX_RETRIES,
    ) -> None:
        self._base_url    = base_url.rstrip("/")
        self._timeout     = timeout
        self._max_retries = max_retries

        self._session = requests.Session()
        self._session.headers.update({
            "Content-Type": "application/json",
            "Accept":       "application/json",
        })
        if api_key:
            self._session.headers["Authorization"] = f"Bearer {api_key}"

        logger.info(
            "BackendHTTPClient initialised | url=%s | timeout=%ds | retries=%d",
            self._base_url, timeout, max_retries,
        )

    def post_detection(self, payload: Dict[str, Any]) -> bool:
        url = f"{self._base_url}{self._DETECTION_ENDPOINT}"

        for attempt in range(1, self._max_retries + 1):
            try:
                resp = self._session.post(url, json=payload, timeout=self._timeout)

                if resp.status_code == 200 or resp.status_code == 201:
                    logger.info(
                        "Detection posted | person_id=%s | status=%d",
                        payload.get("person_id"), resp.status_code,
                    )
                    return True

                if resp.status_code < 500:
                    logger.error(
                        "Backend rejected detection (status=%d): %s",
                        resp.status_code, resp.text[:200],
                    )
                    return False

                logger.warning(
                    "Backend error (status=%d) — attempt %d/%d",
                    resp.status_code, attempt, self._max_retries,
                )

            except requests.exceptions.Timeout:
                logger.warning("POST timeout — attempt %d/%d", attempt, self._max_retries)
            except requests.exceptions.ConnectionError:
                logger.warning("Connection error — attempt %d/%d", attempt, self._max_retries)
            except Exception:
                logger.exception("Unexpected error in post_detection — attempt %d.", attempt)

            if attempt < self._max_retries:
                backoff = RETRY_BASE * (2 ** (attempt - 1))
                logger.debug("Retrying in %.1fs …", backoff)
                time.sleep(backoff)

        logger.error(
            "Failed to post detection after %d attempts (person_id=%s).",
            self._max_retries, payload.get("person_id"),
        )
        return False

    def health_check(self) -> bool:
        url = f"{self._base_url}/api/health"
        try:
            resp = self._session.get(url, timeout=self._timeout)
            ok = resp.status_code < 300
            logger.debug("Backend health check → %s (%d)", "OK" if ok else "FAIL", resp.status_code)
            return ok
        except Exception:
            logger.warning("Backend health check failed — backend may be down.")
            return False

    def close(self) -> None:
        self._session.close()
