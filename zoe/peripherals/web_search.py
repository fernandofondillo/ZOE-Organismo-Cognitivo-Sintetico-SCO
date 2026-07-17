"""
ZOE Web Search Actuator — Sprint 5.22

Da a ZOE la capacidad de buscar en internet y usar herramientas.
Esto son sus "manos": puede buscar información, leer páginas web,
y usar los resultados para responder mejor.

Uso:
    from zoe.peripherals.web_search import WebSearchActuator
    actuator = WebSearchActuator()
    results = await actuator.search("Python tutorial")
    content = await actuator.fetch_url("https://example.com")
"""

from __future__ import annotations

import logging
import os
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class WebSearchResult:
    """Resultado de una búsqueda web."""
    def __init__(self, title: str, url: str, snippet: str):
        self.title = title
        self.url = url
        self.snippet = snippet

    def to_dict(self) -> Dict:
        return {"title": self.title, "url": self.url, "snippet": self.snippet}

    def __str__(self) -> str:
        return f"{self.title}\n{self.url}\n{self.snippet}"


class WebSearchActuator:
    """
    Actuator que permite a ZOE buscar en internet.

    Sprint 5.22: Implementación inicial usando DuckDuckGo HTML (sin API key).
    No requiere dependencias adicionales — usa urllib de la stdlib.

    Fallback: si no hay internet, devuelve None gracefulmente.
    """

    def __init__(self, max_results: int = 5, timeout: int = 10):
        self.max_results = max_results
        self.timeout = timeout

    @property
    def name(self) -> str:
        return "web_search"

    async def search(self, query: str) -> List[WebSearchResult]:
        """Busca en internet usando DuckDuckGo HTML.

        Args:
            query: texto a buscar

        Returns:
            Lista de WebSearchResult (máximo max_results)
        """
        import asyncio
        import urllib.parse
        import urllib.request

        results: List[WebSearchResult] = []

        try:
            # Usar DuckDuckGo HTML (sin API key, sin dependencias)
            url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            }

            def _fetch():
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    return resp.read().decode("utf-8", errors="replace")

            html = await asyncio.to_thread(_fetch)

            # Parsear resultados de DuckDuckGo HTML
            # Los resultados están en <a class="result__a" href="...">
            import re

            # Buscar enlaces de resultados
            pattern = r'<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>(.*?)</a>'
            matches = re.findall(pattern, html, re.DOTALL)

            for url_match, title_match in matches[:self.max_results]:
                # Limpiar URL (DuckDuckGo usa redirect)
                if "uddg=" in url_match:
                    import urllib.parse as urlparse
                    parsed = urlparse.urlparse(url_match)
                    params = urlparse.parse_qs(parsed.query)
                    clean_url = params.get("uddg", [url_match])[0]
                else:
                    clean_url = url_match

                # Limpiar título (quitar tags HTML)
                clean_title = re.sub(r"<[^>]+>", "", title_match).strip()

                if clean_title and clean_url:
                    results.append(WebSearchResult(
                        title=clean_title,
                        url=clean_url,
                        snippet="",  # Snippet requiere parseo adicional
                    ))

            logger.info(f"WebSearch: '{query[:50]}' → {len(results)} results")

        except Exception as e:
            logger.warning(f"WebSearch failed: {e}")

        return results

    async def fetch_url(self, url: str, max_chars: int = 2000) -> Optional[str]:
        """Descarga el contenido de texto de una URL.

        Args:
            url: URL a descargar
            max_chars: máximo de caracteres a devolver

        Returns:
            Texto de la página, o None si falla
        """
        import asyncio
        import urllib.request
        import re

        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            }

            def _fetch():
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    return resp.read().decode("utf-8", errors="replace")

            html = await asyncio.to_thread(_fetch)

            # Extraer texto del HTML (quitar tags)
            # Qitar script y style
            html = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL | re.IGNORECASE)
            html = re.sub(r"<style[^>]*>.*?</style>", "", html, flags=re.DOTALL | re.IGNORECASE)
            # Quitar tags
            text = re.sub(r"<[^>]+>", " ", html)
            # Limpiar espacios
            text = " ".join(text.split())

            return text[:max_chars]

        except Exception as e:
            logger.warning(f"WebSearch fetch_url failed: {e}")
            return None

    def should_use_search(self, user_input: str) -> bool:
        """Determina si una pregunta del usuario requiere búsqueda web.

        Heurística simple: si contiene palabras clave de búsqueda.
        """
        search_keywords = [
            "busca", "buscar", "buscar en internet", "google",
            "noticias", "actualidad", "últimas", "recent",
            "search", "look up", "find online", "what's new",
            "clima", "tiempo", "precio", "cotización",
        ]
        input_lower = user_input.lower()
        return any(kw in input_lower for kw in search_keywords)
