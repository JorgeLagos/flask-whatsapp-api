import hashlib
import logging
import mimetypes
import os
import unicodedata
from typing import Any, Dict, Optional

import requests

from utils.ai_processor import AIProcessor

logger = logging.getLogger("app.services.ai.saia_console_client")


class SAIAConsoleClient:
    """Synchronous client for SAIA: upload bytes and chat with a file.

    Exposes upload_bytes(...) and chat_with_file(...). Uses requests and a
    small in-process cache to avoid re-uploading identical bytes.
    """

    def __init__(
        self,
        api_token: str,
        organization_id: str,
        project_id: str,
        assistant_id: str,
        base_url: str = "https://api.saia.ai",
        timeout: int = 60,
    ):
        self.api_token = api_token
        self.organization_id = organization_id
        self.project_id = project_id
        self.assistant_id = assistant_id
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.default_headers = {
            "Authorization": f"Bearer {self.api_token}",
            "organizationId": self.organization_id,
            "projectId": self.project_id,
        }
        self.processor = AIProcessor(
            api_token,
            organization_id,
            project_id,
            base_url=f"{self.base_url}/chat",
            request_timeout=timeout,
        )
        self._upload_cache: Dict[str, Dict] = {}
        self.metrics = {"upload_cache_hits": 0, "upload_cache_misses": 0}

    @staticmethod
    def _sanitize_header_value(v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        try:
            s = str(v)
        except Exception:
            s = repr(v)
        nfkd = unicodedata.normalize("NFKD", s)
        ascii_only = "".join(c for c in nfkd if ord(c) < 128)
        return "".join(ch for ch in ascii_only if ch.isprintable())

    @staticmethod
    def _guess_content_type(path: str) -> str:
        mt, _ = mimetypes.guess_type(path)
        return mt or "application/octet-stream"

    @staticmethod
    def _sha256(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    def upload_bytes(self, data: bytes, file_name: str, folder: Optional[str] = None, alias: Optional[str] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/v1/files"
        file_size = len(data)
        file_hash = self._sha256(data)
        content_type = self._guess_content_type(file_name or "file")

        headers = dict(self.default_headers)
        headers["Accept"] = "application/json"
        alias_used = alias or os.path.splitext(os.path.basename(file_name))[0]
        headers["fileName"] = self._sanitize_header_value(alias_used)
        headers["folder"] = self._sanitize_header_value(folder or "test1")

        cache_key = f"{alias_used}:{file_hash}"
        cached = self._upload_cache.get(cache_key)
        if cached:
            try:
                self.metrics["upload_cache_hits"] += 1
            except Exception:
                pass
            return dict(cached)
        else:
            try:
                self.metrics["upload_cache_misses"] += 1
            except Exception:
                pass

        files = {"file": (file_name, data, content_type)}
        try:
            r = requests.post(url, headers=headers, files=files, timeout=self.timeout)
            r.raise_for_status()
            try:
                j = r.json()
            except Exception:
                j = {"text": r.text}

            result = {
                "status_code": r.status_code,
                "headers": dict(r.headers),
                "file_name_used": file_name,
                "file_alias_used": alias_used,
                "file_size": file_size,
                "file_sha256": file_hash,
            }
            if isinstance(j, dict):
                result.update(j)
            else:
                result["json"] = j

            # Cache successful uploads
            if r.status_code < 400:
                try:
                    self._upload_cache[cache_key] = dict(result)
                    if len(self._upload_cache) > 256:
                        self._upload_cache.pop(next(iter(self._upload_cache)))
                except Exception:
                    pass
            return result
        except requests.RequestException as e:
            logger.exception("Error uploading bytes: %s", e)
            return {"error": "request_error", "detail": str(e)}

    def chat_with_file(self, prompt: str, file_id: str, assistant_id: Optional[str] = None, file_name_used: Optional[str] = None) -> Dict[str, Any]:
        aid = assistant_id or self.assistant_id
        extra_headers = {"fileName": file_name_used} if file_name_used else None
        try:
            # Use AIProcessor synchronous process
            resp = self.processor.process(aid, prompt, extra_headers=extra_headers, stream=False)
            # Add some sent headers/payload info for debugging
            try:
                sent_payload = self.processor._prepare_payload(aid, prompt, stream=False)
                sent_headers = dict(self.processor.headers)
                if extra_headers:
                    sent_headers.update(extra_headers)
                if "Authorization" in sent_headers:
                    sent_headers["Authorization"] = "Bearer *****"
                if isinstance(resp, dict):
                    resp.setdefault("sent_payload", sent_payload)
                    resp.setdefault("sent_headers", sent_headers)
            except Exception:
                pass
            return resp
        except Exception as e:
            logger.exception("Chat exception: %s", e)
            return {"error": "chat_failed", "detail": str(e)}

    def aclose(self) -> None:
        # no-op for sync client
        return None
    
