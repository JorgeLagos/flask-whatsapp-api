import json
import logging
import re
import time
import uuid
from typing import Any, Dict, Optional, Union

import requests
from dotenv import load_dotenv

# Configure a proper hierarchical logger
logger = logging.getLogger("app.services.ai.processor")

# Load environment variables
load_dotenv()


class AIProcessor:
    """
    Synchronous AI processor for SAIA chat endpoint.
    Only essential behavior preserved: prepare payload, POST, extract text or JSON.
    """

    def __init__(
        self,
        api_token: str,
        organization_id: str,
        project_id: str,
        base_url: str = "https://api.saia.ai/chat",
        request_timeout: int = 60,
    ):
        self.api_token = api_token
        self.organization_id = organization_id
        self.project_id = project_id
        self.url = base_url
        self.request_timeout = request_timeout
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_token}",
            "organizationId": self.organization_id,
            "projectId": self.project_id,
        }

    def _prepare_payload(self, assistant_id: str, content: Any, stream: bool = False) -> Dict[str, Any]:
        if not isinstance(content, str):
            try:
                content_str = json.dumps(content, ensure_ascii=False)
            except Exception:
                content_str = str(content)
        else:
            content_str = content

        return {
            "model": f"saia:assistant:{assistant_id}",
            "messages": [{"role": "user", "content": content_str}],
            "stream": stream,
        }

    def _parse_ai_response(self, response_text: str) -> Dict[str, Any]:
        clean = re.sub(r"```json\\s*|\\s*```", "", response_text, flags=re.DOTALL).strip()
        try:
            return json.loads(clean)
        except json.JSONDecodeError:
            logger.debug("Respuesta no es JSON válido, devolviendo como mensaje de texto")
            return {"message": response_text}

    def process(self, assistant_id: str, content: Any, extra_headers: Optional[Dict[str, str]] = None, stream: bool = False) -> Dict[str, Any]:
        start_time = time.time()
        request_id = uuid.uuid4().hex[:8]
        logger.debug(f"[{request_id}] Procesando solicitud para assistant_id={assistant_id}")
        payload = self._prepare_payload(assistant_id, content, stream=stream)
        headers = dict(self.headers)
        if extra_headers:
            for hk, hv in (extra_headers or {}).items():
                try:
                    headers[str(hk)] = str(hv)
                except Exception:
                    headers[str(hk)] = repr(hv)

        try:
            r = requests.post(self.url, headers=headers, json=payload, timeout=self.request_timeout)
            r.raise_for_status()
            data = r.json()

            # extract a textual payload if possible
            raw = None
            if isinstance(data, dict) and "choices" in data and data.get("choices"):
                choice0 = data["choices"][0]
                if isinstance(choice0, dict):
                    msg = choice0.get("message") or choice0.get("delta") or choice0
                    if isinstance(msg, dict):
                        raw = msg.get("content") or msg.get("text") or msg.get("payload")
                    elif isinstance(msg, str):
                        raw = msg
                elif isinstance(choice0, str):
                    raw = choice0

            if raw is None:
                # try to find first string in response
                def find_string(o):
                    if isinstance(o, str):
                        return o
                    if isinstance(o, list):
                        for v in o:
                            s = find_string(v)
                            if s:
                                return s
                        return None
                    if isinstance(o, dict):
                        for v in o.values():
                            s = find_string(v)
                            if s:
                                return s
                        return None
                    return None

                raw = find_string(data)

            if raw is None:
                result = data
            else:
                if isinstance(raw, str) and raw.strip() == "":
                    return {"error": "no_text_found", "user_message": "No se detectó texto en el archivo o imagen."}
                result = self._parse_ai_response(raw)
                if isinstance(result, dict):
                    m = result.get("message")
                    if isinstance(m, str) and m.strip() == "":
                        return {"error": "no_text_found", "user_message": "No se detectó texto en el archivo o imagen."}

            elapsed = time.time() - start_time
            logger.debug(f"[{request_id}] Procesamiento completado en {elapsed:.2f}s")
            return result
        except requests.HTTPError as e:
            try:
                text = r.text
            except Exception:
                text = str(e)
            logger.error(f"[{request_id}] Error HTTP: {text}")
            return {"error": "http_error", "detail": text}
        except Exception as e:
            logger.exception("Error en process: %s", e)
            return {"error": "internal_error", "detail": str(e)}
