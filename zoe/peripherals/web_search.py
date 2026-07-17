"""
ZOE v1.0 — WebSearchActuator

Sprint 5.22+5.23 — Actuator que permite a ZOE buscar en internet y leer páginas.

Implementación:
- Usa DuckDuckGo Lite (https://lite.duckduckgo.com/lite/) que devuelve HTML
  simple y estable (sin JavaScript, sin anti-bot challenge).
- No requiere API key ni dependencias externas (solo stdlib urllib).
- Snippets reales extraídos del HTML (no solo titles).

Sprint 5.23 F0-5 (BUG-006 fix): la versión anterior usaba
``https://html.duckduckgo.com/html/`` con regex ``class="result__a"``,
que dejó de funcionar cuando DDG redirigió a una página anti-bot.
Esta versión usa ``lite.duckduckgo.com`` con regex sobre tabla HTML
simple que se mantiene estable.

Uso:
    from zoe.peripherals.web_search import WebSearchActuator

    ws = WebSearchActuator(max_results=5, timeout=15)
    results = await ws.search("python asyncio tutorial")
    # results: List[WebSearchResult(title, url, snippet)]

    text = await ws.fetch_url("https://example.com/article", max_chars=4000)

    if ws.should_use_search("busca información sobre X"):
        # ...
"""

from __future__ import annotations

import asyncio
import logging
import re
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from typing import List, Optional

logger = logging.getLogger(__name__)


@dataclass
class WebSearchResult:
    """Resultado individual de búsqueda web."""

    title: str
    url: str
    snippet: str = ""

    def to_dict(self) -> dict:
        return {"title": self.title, "url": self.url, "snippet": self.snippet}


# Palabras clave que indican que el usuario quiere buscar en internet
# (mezcla español + inglés, como los demás componentes de ZOE).
_SEARCH_TRIGGERS_ES = [
    "busca",
    "buscar",
    "búscame",
    "buscar en internet",
    "buscar en la web",
    "buscar online",
    "googlea",
    "googlear",
    "¿qué es",
    "¿qué son",
    "¿quién es",
    "¿quién fue",
    "¿cuándo",
    "¿dónde",
    "¿por qué",
    "noticias",
    "últimas noticias",
    "información sobre",
    "información de",
    "definición de",
]
_SEARCH_TRIGGERS_EN = [
    "search for",
    "search the web",
    "find information about",
    "find info about",
    "google",
    "look up",
    "lookup",
    "what is",
    "what are",
    "who is",
    "who was",
    "when did",
    "where is",
    "why is",
    "latest news",
    "news about",
    "information about",
    "info about",
    "definition of",
]


class WebSearchActuator:
    """
    Actuator de búsqueda web via DuckDuckGo Lite.

    Sprint 5.22: implementación inicial.
    Sprint 5.23 F0-5: migrada a lite.duckduckgo.com tras cambio anti-bot
    en html.duckduckgo.com.
    """

    # User-Agent moderno y genérico
    _USER_AGENT = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )

    def __init__(self, max_results: int = 5, timeout: int = 15):
        self.max_results = max_results
        self.timeout = timeout
        self._total_searches: int = 0
        self._total_fetches: int = 0
        self._last_query: str = ""

    async def search(self, query: str) -> List[WebSearchResult]:
        """
        Busca ``query`` en DuckDuckGo Lite y retorna hasta
        ``self.max_results`` resultados con title, url y snippet.

        Sprint 5.23 F0-5: usa POST a ``https://lite.duckduckgo.com/lite/``
        con form data ``q=<query>&kl=wt-wi``. El endpoint GET redirige
        a una página de selección de región; POST devuelve resultados reales.
        """
        if not query or not query.strip():
            return []

        self._total_searches += 1
        self._last_query = query

        url = "https://lite.duckduckgo.com/lite/"
        # DDG Lite espera form data POST, no query string GET.
        data = urllib.parse.urlencode({"q": query, "kl": "wt-wi"}).encode("utf-8")
        headers = {
            "User-Agent": self._USER_AGENT,
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "es,en;q=0.9",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        try:
            html = await asyncio.to_thread(
                self._fetch_url_sync_post, url, data, headers, self.timeout
            )
        except Exception as e:
            logger.warning("WebSearchActuator.search fetch failed: %s", e)
            return []

        results = self._parse_lite_html(html)
        logger.info(
            "WebSearchActuator: query=%r -> %d results",
            query[:60],
            len(results),
        )
        return results[: self.max_results]

    async def fetch_url(self, url: str, max_chars: int = 5000) -> str:
        """
        Descarga una URL y devuelve el texto plano (HTML sin tags),
        truncado a ``max_chars``.
        """
        if not url or not url.startswith(("http://", "https://")):
            return ""

        self._total_fetches += 1
        headers = {
            "User-Agent": self._USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,*/*",
            "Accept-Language": "es,en;q=0.9",
        }

        try:
            html = await asyncio.to_thread(
                self._fetch_url_sync, url, headers, self.timeout
            )
        except Exception as e:
            logger.warning("WebSearchActuator.fetch_url failed (%s): %s", url, e)
            return ""

        text = self._strip_html(html)
        if len(text) > max_chars:
            text = text[:max_chars] + "..."
        return text

    def should_use_search(self, text: str) -> bool:
        """
        Heurística: ¿el usuario quiere que busquemos en internet?
        """
        if not text:
            return False
        t = text.lower().strip()
        # Coincidencia exacta de frase
        for trigger in _SEARCH_TRIGGERS_ES + _SEARCH_TRIGGERS_EN:
            if trigger in t:
                return True
        return False

    def get_stats(self) -> dict:
        return {
            "total_searches": self._total_searches,
            "total_fetches": self._total_fetches,
            "last_query": self._last_query,
            "max_results": self.max_results,
            "timeout": self.timeout,
        }

    # ===================================================================
    # Internal helpers (síncronos, llamados via asyncio.to_thread)
    # ===================================================================

    @staticmethod
    def _fetch_url_sync(url: str, headers: dict, timeout: int) -> str:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            # Forzar utf-8 con replace para no romper con caracteres raros
            data = resp.read()
            return data.decode("utf-8", errors="replace")

    @staticmethod
    def _fetch_url_sync_post(
        url: str, data: bytes, headers: dict, timeout: int
    ) -> str:
        """HTTP POST síncrono (Sprint 5.23 F0-5)."""
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            return raw.decode("utf-8", errors="replace")

    @staticmethod
    def _parse_lite_html(html: str) -> List[WebSearchResult]:
        """
        Parsea el HTML de lite.duckduckgo.com/lite/.

        DDG Lite renderiza resultados en una tabla con clase ``result-link``
        para el anchor y un ``<td class=\"result-snippet\">`` para el snippet.
        Esta estructura es muy estable desde 2018.

        Fallback: si no encuentra ``result-link``, intenta con regex genérica
        sobre anchors ``<a href="...">title</a>`` filtrando URLs internas.
        """
        results: List[WebSearchResult] = []

        # Intento 1: anchors con class="result-link"
        # Pattern: <a [...] class="result-link" [...] href="URL">TITLE</a>
        # Y luego un <td class="result-snippet">SNIPPET</td> cercano
        link_pattern = re.compile(
            r'<a[^>]+class="result-link"[^>]+href="([^"]+)"[^>]*>(.*?)</a>',
            re.IGNORECASE | re.DOTALL,
        )
        snippet_pattern = re.compile(
            r'<td[^>]+class="result-snippet"[^>]*>(.*?)</td>',
            re.IGNORECASE | re.DOTALL,
        )

        links = link_pattern.findall(html)
        snippets = snippet_pattern.findall(html)

        for i, (raw_url, raw_title) in enumerate(links):
            url = WebSearchActuator._unwrap_ddg_url(raw_url)
            if not url:
                continue
            title = WebSearchActuator._strip_html(raw_title).strip()
            if not title:
                continue
            snippet = ""
            if i < len(snippets):
                snippet = WebSearchActuator._strip_html(snippets[i]).strip()
            results.append(WebSearchResult(title=title, url=url, snippet=snippet))

        if results:
            return results

        # Intento 2 (fallback): buscar todos los anchors con href http
        # y descartar los de duckduckgo.com
        generic_pattern = re.compile(
            r'<a[^>]+href="(https?://[^"]+)"[^>]*>(.*?)</a>',
            re.IGNORECASE | re.DOTALL,
        )
        for raw_url, raw_title in generic_pattern.findall(html):
            if "duckduckgo.com" in raw_url:
                continue
            if raw_url.startswith("https://duckduckgo.com"):
                continue
            title = WebSearchActuator._strip_html(raw_title).strip()
            if not title or len(title) < 5:
                continue
            results.append(WebSearchResult(title=title, url=raw_url, snippet=""))
            if len(results) >= 20:
                break

        return results

    @staticmethod
    def _unwrap_ddg_url(raw_url: str) -> str:
        """
        DDG Lite a veces envuelve la URL final en un redirect.
        Formatos posibles:
        - //duckduckgo.com/l/?uddg=<encoded_url>&...
        - https://duckduckgo.com/l/?uddg=<encoded_url>
        - URL directa (http/https)
        """
        if not raw_url:
            return ""
        if raw_url.startswith("//"):
            raw_url = "https:" + raw_url
        if "uddg=" in raw_url:
            parsed = urllib.parse.urlparse(raw_url)
            qs = urllib.parse.parse_qs(parsed.query)
            uddg = qs.get("uddg", [])
            if uddg:
                return urllib.parse.unquote(uddg[0])
        if raw_url.startswith(("http://", "https://")):
            return raw_url
        return ""

    @staticmethod
    def _strip_html(html: str) -> str:
        """Convierte HTML a texto plano: elimina scripts/styles/tags/entities."""
        if not html:
            return ""
        # Eliminar scripts y styles completos
        html = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r"<style[^>]*>.*?</style>", "", html, flags=re.DOTALL | re.IGNORECASE)
        # Eliminar tags
        text = re.sub(r"<[^>]+>", " ", html)
        # Decodificar entidades HTML comunes
        entities = {
            "&amp;": "&",
            "&lt;": "<",
            "&gt;": ">",
            "&quot;": '"',
            "&#39;": "'",
            "&#x27;": "'",
            "&#x2F;": "/",
            "&nbsp;": " ",
            "&aacute;": "á",
            "&eacute;": "é",
            "&iacute;": "í",
            "&oacute;": "ó",
            "&uacute;": "ú",
            "&ntilde;": "ñ",
            "&Aacute;": "Á",
            "&Eacute;": "É",
            "&Iacute;": "Í",
            "&Oacute;": "Ó",
            "&Uacute;": "Ú",
            "&Ntilde;": "Ñ",
        }
        for entity, char in entities.items():
            text = text.replace(entity, char)
        # Colapsar whitespace
        text = re.sub(r"\s+", " ", text)
        return text.strip()
