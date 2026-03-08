"""Agents avancés S3 - Recherche web, crawling, et recherche sémantique.

Ce module fournit des agents autonomes pour:
- Recherche web via DuckDuckGo/SearXNG
- Crawling intelligent de pages web
- Recherche sémantique via Qdrant
- Orchestration multi-sources
"""

import asyncio
import json
import os
import re
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional
from urllib.parse import quote_plus, urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

# Configuration
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
DEFAULT_MODEL = os.getenv("LLM_MODEL", "qwen3-coder:30b")
QDRANT_URL = os.getenv("QDRANT_URL", "http://mptoo-qdrant:6333")
SEARXNG_URL = os.getenv("SEARXNG_URL", "http://localhost:8888")


# ============ Data Classes ============


@dataclass
class SearchResult:
    """Résultat de recherche web."""

    title: str
    url: str
    snippet: str
    source: str = "web"
    score: float = 0.0
    metadata: dict = field(default_factory=dict)


@dataclass
class CrawlResult:
    """Résultat de crawling."""

    url: str
    title: str
    content: str
    links: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    error: str | None = None


@dataclass
class VectorSearchResult:
    """Résultat de recherche vectorielle."""

    id: str
    content: str
    score: float
    metadata: dict = field(default_factory=dict)


@dataclass
class AggregatedResult:
    """Résultat agrégé de toutes les sources."""

    query: str
    web_results: list[SearchResult] = field(default_factory=list)
    crawl_results: list[CrawlResult] = field(default_factory=list)
    vector_results: list[VectorSearchResult] = field(default_factory=list)
    synthesis: str | None = None
    sources_used: list[str] = field(default_factory=list)
    total_documents: int = 0
    search_time_seconds: float = 0.0


class SearchStatus(str, Enum):
    """Statut de recherche."""

    PENDING = "pending"
    SEARCHING_WEB = "searching_web"
    CRAWLING = "crawling"
    VECTOR_SEARCH = "vector_search"
    SYNTHESIZING = "synthesizing"
    COMPLETED = "completed"
    FAILED = "failed"


# ============ Helper Functions ============


async def call_ollama(prompt: str, system: str = "", format_json: bool = True) -> dict | str:
    """Appel à l'API Ollama."""
    async with httpx.AsyncClient(timeout=180.0) as client:
        payload = {
            "model": DEFAULT_MODEL,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            "stream": False,
        }
        if format_json:
            payload["format"] = "json"

        response = await client.post(f"{OLLAMA_URL}/api/chat", json=payload)
        response.raise_for_status()
        content = response.json()["message"]["content"]

        if format_json:
            # Handle potential JSON parsing issues
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                # Try to extract JSON from response
                json_match = re.search(r"\{.*\}", content, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
                return {"error": "Invalid JSON", "raw": content}
        return content


def clean_text(html_content: str) -> str:
    """Nettoie le contenu HTML pour extraire le texte."""
    soup = BeautifulSoup(html_content, "html.parser")

    # Supprimer scripts, styles, etc.
    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()

    text = soup.get_text(separator=" ", strip=True)
    # Nettoyer les espaces multiples
    text = re.sub(r"\s+", " ", text)
    return text[:10000]  # Limiter la taille


# ============ Web Search Agent ============


class WebSearchAgent:
    """Agent de recherche web via DuckDuckGo et SearXNG."""

    DUCKDUCKGO_URL = "https://api.duckduckgo.com/"

    def __init__(self, use_searxng: bool = True):
        self.use_searxng = use_searxng
        self.searxng_url = SEARXNG_URL

    async def search(self, query: str, num_results: int = 10) -> list[SearchResult]:
        """Effectue une recherche web."""
        results = []

        # Essayer SearXNG d'abord si disponible
        if self.use_searxng:
            searxng_results = await self._search_searxng(query, num_results)
            results.extend(searxng_results)

        # Fallback DuckDuckGo si pas assez de résultats
        if len(results) < num_results:
            ddg_results = await self._search_duckduckgo(query, num_results - len(results))
            results.extend(ddg_results)

        # Si toujours pas de résultats, utiliser la recherche HTML
        if not results:
            html_results = await self._search_duckduckgo_html(query, num_results)
            results.extend(html_results)

        return results[:num_results]

    async def _search_searxng(self, query: str, num_results: int) -> list[SearchResult]:
        """Recherche via SearXNG (instance locale)."""
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(
                    f"{self.searxng_url}/search",
                    params={
                        "q": query,
                        "format": "json",
                        "categories": "general",
                        "language": "fr-FR",
                    },
                )
                if response.status_code == 200:
                    data = response.json()
                    return [
                        SearchResult(
                            title=r.get("title", ""),
                            url=r.get("url", ""),
                            snippet=r.get("content", "")[:500],
                            source="searxng",
                            score=1.0 - (i * 0.1),
                            metadata={"engine": r.get("engine", "unknown")},
                        )
                        for i, r in enumerate(data.get("results", [])[:num_results])
                    ]
        except Exception:
            pass
        return []

    async def _search_duckduckgo(self, query: str, num_results: int) -> list[SearchResult]:
        """Recherche via DuckDuckGo Instant Answer API."""
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(
                    self.DUCKDUCKGO_URL,
                    params={"q": query, "format": "json", "no_html": 1, "skip_disambig": 1},
                )
                if response.status_code == 200:
                    data = response.json()
                    results = []

                    # Abstract (résumé principal)
                    if data.get("Abstract"):
                        results.append(
                            SearchResult(
                                title=data.get("Heading", query),
                                url=data.get("AbstractURL", ""),
                                snippet=data.get("Abstract", ""),
                                source="duckduckgo",
                                score=1.0,
                            )
                        )

                    # Related topics
                    for i, topic in enumerate(data.get("RelatedTopics", [])[:num_results]):
                        if isinstance(topic, dict) and "Text" in topic:
                            results.append(
                                SearchResult(
                                    title=topic.get("Text", "")[:100],
                                    url=topic.get("FirstURL", ""),
                                    snippet=topic.get("Text", ""),
                                    source="duckduckgo",
                                    score=0.8 - (i * 0.1),
                                )
                            )

                    return results
        except Exception:
            pass
        return []

    async def _search_duckduckgo_html(self, query: str, num_results: int) -> list[SearchResult]:
        """Recherche via DuckDuckGo HTML (fallback)."""
        try:
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                response = await client.get(
                    "https://html.duckduckgo.com/html/",
                    params={"q": query},
                    headers={"User-Agent": "Mozilla/5.0 (compatible; MPtoO-Bot/1.0)"},
                )
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "html.parser")
                    results = []

                    for i, result in enumerate(soup.select(".result")[:num_results]):
                        title_elem = result.select_one(".result__title")
                        snippet_elem = result.select_one(".result__snippet")
                        link_elem = result.select_one(".result__url")

                        if title_elem and snippet_elem:
                            # Extraire l'URL réelle
                            href = title_elem.find("a")
                            url = href.get("href", "") if href else ""

                            results.append(
                                SearchResult(
                                    title=title_elem.get_text(strip=True),
                                    url=url,
                                    snippet=snippet_elem.get_text(strip=True),
                                    source="duckduckgo_html",
                                    score=0.7 - (i * 0.05),
                                )
                            )

                    return results
        except Exception:
            pass
        return []


# ============ Web Crawler Agent ============


class WebCrawlerAgent:
    """Agent de crawling web intelligent."""

    def __init__(self, max_depth: int = 2, max_pages: int = 10):
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.visited_urls: set[str] = set()

    async def crawl(self, urls: list[str], extract_links: bool = True) -> list[CrawlResult]:
        """Crawle une liste d'URLs."""
        results = []

        for url in urls[: self.max_pages]:
            if url in self.visited_urls:
                continue

            result = await self._crawl_page(url, extract_links)
            if result:
                results.append(result)
                self.visited_urls.add(url)

        return results

    async def _crawl_page(self, url: str, extract_links: bool = True) -> CrawlResult | None:
        """Crawle une page individuelle."""
        try:
            async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
                response = await client.get(
                    url,
                    headers={
                        "User-Agent": "Mozilla/5.0 (compatible; MPtoO-Evaluator/1.0)",
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                        "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
                    },
                )

                if response.status_code != 200:
                    return CrawlResult(
                        url=url, title="", content="", error=f"HTTP {response.status_code}"
                    )

                content_type = response.headers.get("content-type", "")
                if "text/html" not in content_type and "application/xhtml" not in content_type:
                    return CrawlResult(
                        url=url, title="", content="", error=f"Non-HTML content: {content_type}"
                    )

                soup = BeautifulSoup(response.text, "html.parser")

                # Extraire le titre
                title_tag = soup.find("title")
                title = title_tag.get_text(strip=True) if title_tag else ""

                # Extraire le contenu principal
                # Essayer plusieurs sélecteurs pour le contenu principal
                main_content = None
                for selector in ["article", "main", ".content", "#content", ".post", ".article"]:
                    main_content = soup.select_one(selector)
                    if main_content:
                        break

                if not main_content:
                    main_content = soup.find("body")

                content = clean_text(str(main_content)) if main_content else ""

                # Extraire les liens
                links = []
                if extract_links:
                    base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
                    for a in soup.find_all("a", href=True):
                        href = a["href"]
                        if href.startswith("/"):
                            href = urljoin(base_url, href)
                        if (
                            href.startswith("http")
                            and urlparse(href).netloc == urlparse(url).netloc
                        ):
                            links.append(href)

                # Métadonnées
                metadata = {}
                meta_desc = soup.find("meta", attrs={"name": "description"})
                if meta_desc:
                    metadata["description"] = meta_desc.get("content", "")

                meta_keywords = soup.find("meta", attrs={"name": "keywords"})
                if meta_keywords:
                    metadata["keywords"] = meta_keywords.get("content", "")

                return CrawlResult(
                    url=url,
                    title=title,
                    content=content,
                    links=list(set(links))[:20],  # Limiter les liens
                    metadata=metadata,
                )

        except Exception as e:
            return CrawlResult(url=url, title="", content="", error=str(e))

    async def deep_crawl(self, start_url: str, depth: int = 2) -> list[CrawlResult]:
        """Crawl en profondeur à partir d'une URL."""
        all_results = []
        urls_to_crawl = [start_url]
        current_depth = 0

        while current_depth < depth and urls_to_crawl and len(all_results) < self.max_pages:
            # Crawle le niveau actuel
            results = await self.crawl(urls_to_crawl)
            all_results.extend(results)

            # Collecte les nouveaux liens
            urls_to_crawl = []
            for result in results:
                for link in result.links:
                    if link not in self.visited_urls:
                        urls_to_crawl.append(link)

            current_depth += 1

        return all_results


# ============ Qdrant Vector Search Agent ============


class QdrantSearchAgent:
    """Agent de recherche vectorielle via Qdrant."""

    def __init__(self, collection_name: str = "mptoo_documents"):
        self.collection_name = collection_name
        self.qdrant_url = QDRANT_URL

    async def search(self, query: str, limit: int = 10) -> list[VectorSearchResult]:
        """Recherche sémantique dans Qdrant."""
        try:
            # D'abord, générer l'embedding de la requête via Ollama
            embedding = await self._get_embedding(query)
            if not embedding:
                return []

            # Recherche dans Qdrant
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.qdrant_url}/collections/{self.collection_name}/points/search",
                    json={"vector": embedding, "limit": limit, "with_payload": True},
                )

                if response.status_code == 200:
                    data = response.json()
                    return [
                        VectorSearchResult(
                            id=str(r.get("id", "")),
                            content=r.get("payload", {}).get("content", ""),
                            score=r.get("score", 0.0),
                            metadata=r.get("payload", {}),
                        )
                        for r in data.get("result", [])
                    ]
        except Exception:
            pass
        return []

    async def _get_embedding(self, text: str) -> list[float] | None:
        """Génère un embedding via Ollama."""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{OLLAMA_URL}/api/embeddings",
                    json={
                        "model": "nomic-embed-text",  # Modèle d'embedding
                        "prompt": text,
                    },
                )
                if response.status_code == 200:
                    return response.json().get("embedding")
        except Exception:
            pass
        return None

    async def collection_exists(self) -> bool:
        """Vérifie si la collection existe."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.qdrant_url}/collections/{self.collection_name}")
                return response.status_code == 200
        except Exception:
            return False

    async def create_collection(self, vector_size: int = 768) -> bool:
        """Crée la collection si elle n'existe pas."""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.put(
                    f"{self.qdrant_url}/collections/{self.collection_name}",
                    json={"vectors": {"size": vector_size, "distance": "Cosine"}},
                )
                return response.status_code in [200, 201]
        except Exception:
            return False

    async def index_documents(self, documents: list[dict]) -> int:
        """Indexe des documents dans Qdrant."""
        indexed = 0

        for i, doc in enumerate(documents):
            try:
                content = doc.get("content", "")
                embedding = await self._get_embedding(content[:8000])  # Limite pour l'embedding

                if embedding:
                    async with httpx.AsyncClient(timeout=30.0) as client:
                        response = await client.put(
                            f"{self.qdrant_url}/collections/{self.collection_name}/points",
                            json={
                                "points": [
                                    {
                                        "id": i,
                                        "vector": embedding,
                                        "payload": {
                                            "content": content[:5000],
                                            "url": doc.get("url", ""),
                                            "title": doc.get("title", ""),
                                            "source": doc.get("source", "unknown"),
                                            "indexed_at": datetime.now().isoformat(),
                                        },
                                    }
                                ]
                            },
                        )
                        if response.status_code in [200, 201]:
                            indexed += 1
            except Exception:
                continue

        return indexed


# ============ Advanced Synthesis Agent ============


class SynthesisAgent:
    """Agent de synthèse des résultats multi-sources."""

    SYSTEM_PROMPT = """Tu es un expert en analyse et synthèse d'informations.
Tu reçois des résultats de recherche de plusieurs sources (web, crawling, base vectorielle).
Tu dois produire une synthèse structurée et pertinente.

Réponds TOUJOURS en JSON avec cette structure:
{
    "summary": "Résumé exécutif (2-3 phrases)",
    "key_points": ["point clé 1", "point clé 2", ...],
    "sources_analysis": {
        "web": "analyse des sources web",
        "crawl": "analyse des pages crawlées",
        "vector": "analyse de la base de connaissances"
    },
    "confidence": 0.0 à 1.0,
    "recommendations": ["recommandation 1", ...]
}"""

    async def synthesize(
        self,
        query: str,
        web_results: list[SearchResult],
        crawl_results: list[CrawlResult],
        vector_results: list[VectorSearchResult],
    ) -> dict:
        """Synthétise les résultats de toutes les sources."""

        # Préparer le contexte pour le LLM
        context = f"""Question: {query}

=== RÉSULTATS DE RECHERCHE WEB ({len(web_results)} résultats) ===
"""
        for r in web_results[:5]:
            context += f"\n- [{r.title}]({r.url})\n  {r.snippet}\n"

        context += f"\n=== PAGES CRAWLÉES ({len(crawl_results)} pages) ===\n"
        for r in crawl_results[:3]:
            if not r.error:
                context += f"\n- {r.title} ({r.url})\n  {r.content[:500]}...\n"

        context += f"\n=== BASE DE CONNAISSANCES ({len(vector_results)} documents) ===\n"
        for r in vector_results[:3]:
            context += f"\n- Score: {r.score:.2f}\n  {r.content[:500]}...\n"

        prompt = f"""Analyse ces résultats et produis une synthèse structurée:

{context}

Génère une synthèse en JSON."""

        result = await call_ollama(prompt, self.SYSTEM_PROMPT)
        return result


# ============ Advanced Evaluation Workflow ============


class AdvancedEvaluationWorkflow:
    """Workflow d'évaluation avancé avec recherche multi-sources."""

    def __init__(self, on_status_change: Callable[[SearchStatus, str], None] | None = None):
        self.web_search = WebSearchAgent()
        self.crawler = WebCrawlerAgent()
        self.vector_search = QdrantSearchAgent()
        self.synthesis = SynthesisAgent()

        self.status = SearchStatus.PENDING
        self._on_status_change = on_status_change

    def _update_status(self, status: SearchStatus, message: str = "") -> None:
        """Met à jour le statut et notifie."""
        self.status = status
        if self._on_status_change:
            self._on_status_change(status, message)

    async def run(self, query: str, options: dict | None = None) -> AggregatedResult:
        """Exécute le workflow de recherche avancée."""
        options = options or {}
        start_time = datetime.now()

        result = AggregatedResult(query=query)

        try:
            # Phase 1: Recherche web
            self._update_status(SearchStatus.SEARCHING_WEB, "Recherche web en cours...")
            web_results = await self.web_search.search(
                query, num_results=options.get("web_results", 10)
            )
            result.web_results = web_results
            result.sources_used.append("web")

            # Phase 2: Crawling des URLs trouvées
            if options.get("enable_crawling", True) and web_results:
                self._update_status(SearchStatus.CRAWLING, "Crawling des pages...")
                urls_to_crawl = [r.url for r in web_results[:5] if r.url]
                crawl_results = await self.crawler.crawl(urls_to_crawl)
                result.crawl_results = [r for r in crawl_results if not r.error]
                result.sources_used.append("crawl")

            # Phase 3: Recherche vectorielle
            if options.get("enable_vector_search", True):
                self._update_status(SearchStatus.VECTOR_SEARCH, "Recherche sémantique...")
                if await self.vector_search.collection_exists():
                    vector_results = await self.vector_search.search(query, limit=10)
                    result.vector_results = vector_results
                    result.sources_used.append("vector")

            # Phase 4: Synthèse
            self._update_status(SearchStatus.SYNTHESIZING, "Synthèse des résultats...")
            synthesis_result = await self.synthesis.synthesize(
                query, result.web_results, result.crawl_results, result.vector_results
            )
            result.synthesis = json.dumps(synthesis_result, ensure_ascii=False, indent=2)

            # Calcul des statistiques
            result.total_documents = (
                len(result.web_results) + len(result.crawl_results) + len(result.vector_results)
            )
            result.search_time_seconds = (datetime.now() - start_time).total_seconds()

            self._update_status(SearchStatus.COMPLETED, "Recherche terminée")

        except Exception as e:
            self._update_status(SearchStatus.FAILED, str(e))
            raise

        return result


# ============ Public API ============


async def quick_search(query: str) -> AggregatedResult:
    """Recherche rapide avec paramètres par défaut."""
    workflow = AdvancedEvaluationWorkflow()
    return await workflow.run(
        query, {"web_results": 5, "enable_crawling": False, "enable_vector_search": True}
    )


async def deep_search(query: str) -> AggregatedResult:
    """Recherche approfondie avec crawling."""
    workflow = AdvancedEvaluationWorkflow()
    return await workflow.run(
        query, {"web_results": 10, "enable_crawling": True, "enable_vector_search": True}
    )
