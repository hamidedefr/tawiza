"""Agents d'évaluation autonomes pour Streamlit."""

import json
import os
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional

import httpx

# Configuration
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://host.docker.internal:11434")
DEFAULT_MODEL = os.getenv("LLM_MODEL", "qwen2.5:14b")


@dataclass
class EvaluationFrame:
    """Structured evaluation framework."""

    original_question: str
    sub_questions: list[str] = field(default_factory=list)
    indicators: list[str] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)
    territory: str | None = None
    period: dict[str, str] | None = None


@dataclass
class CollectionResult:
    """Result of data collection."""

    evaluation_id: str
    documents: list[dict[str, Any]] = field(default_factory=list)
    document_count: int = 0
    sources_used: list[str] = field(default_factory=list)
    errors: list[dict[str, str]] = field(default_factory=list)


@dataclass
class AnalysisResult:
    """Result of analysis."""

    statistics: dict[str, Any] = field(default_factory=dict)
    insights: list[str] = field(default_factory=list)
    trends: list[dict[str, Any]] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)


@dataclass
class Report:
    """Generated evaluation report."""

    title: str
    summary: str
    markdown: str
    sections: list[dict[str, str]] = field(default_factory=list)
    generated_at: datetime = field(default_factory=datetime.now)


class WorkflowStatus(str, Enum):
    """Workflow status."""

    PENDING = "pending"
    FRAMING = "framing"
    COLLECTING = "collecting"
    ANALYZING = "analyzing"
    GENERATING = "generating"
    AWAITING_VALIDATION = "awaiting_validation"
    VALIDATED = "validated"
    EXPORTED = "exported"
    FAILED = "failed"


@dataclass
class WorkflowResult:
    """Complete workflow result."""

    evaluation_id: str
    question: str
    frame: EvaluationFrame | None = None
    collection: CollectionResult | None = None
    analysis: AnalysisResult | None = None
    report: Report | None = None
    status: WorkflowStatus = WorkflowStatus.PENDING
    started_at: datetime | None = None
    completed_at: datetime | None = None
    errors: list[str] = field(default_factory=list)


async def call_ollama(prompt: str, system: str = "", format_json: bool = True) -> dict | str:
    """Call Ollama LLM API."""
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
            return json.loads(content)
        return content


class CadreurAgent:
    """Agent for framing evaluation questions."""

    SYSTEM_PROMPT = """Tu es un expert en évaluation des politiques publiques territoriales.
Tu décomposes les questions d'évaluation en sous-questions, identifies les indicateurs pertinents
et les sources de données à mobiliser.

Réponds TOUJOURS en JSON valide avec cette structure exacte:
{
    "sub_questions": ["liste des sous-questions"],
    "indicators": ["liste des indicateurs quantitatifs/qualitatifs"],
    "sources": ["sirene", "bodacc", "datasubvention", "insee"],
    "territory": "région ou département concerné",
    "period": {"start": "2020", "end": "2024"}
}"""

    async def frame(self, question: str) -> EvaluationFrame:
        """Frame an evaluation question into structured components."""
        prompt = f"""Analyse cette question d'évaluation territoriale:

Question: {question}

Identifie:
1. Les sous-questions à investiguer
2. Les indicateurs mesurables
3. Les sources de données publiques pertinentes (sirene, bodacc, datasubvention, insee, france2030)
4. Le territoire concerné
5. La période d'analyse"""

        result = await call_ollama(prompt, self.SYSTEM_PROMPT)

        return EvaluationFrame(
            original_question=question,
            sub_questions=result.get("sub_questions", []),
            indicators=result.get("indicators", []),
            sources=result.get("sources", ["sirene", "insee"]),
            territory=result.get("territory"),
            period=result.get("period", {"start": "2020", "end": "2024"}),
        )


class CollecteurAgent:
    """Agent for collecting data from public APIs."""

    API_ENDPOINTS = {
        "sirene": "https://api.insee.fr/entreprises/sirene/V3.11/siret",
        "bodacc": "https://bodacc-datadila.opendatasoft.com/api/explore/v2.1/catalog/datasets/annonces-commerciales/records",
        "datasubvention": "https://api.datasubvention.beta.gouv.fr/association",
    }

    async def _fetch_sirene_sample(self, territory: str) -> list[dict]:
        """Fetch sample data from Sirene (public endpoint)."""
        # Use public SIRENE dataset from data.gouv.fr API
        dept_codes = {
            "hauts-de-france": "59",
            "ile-de-france": "75",
            "auvergne-rhone-alpes": "69",
            "occitanie": "31",
        }
        dept = dept_codes.get(territory, "59")

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Use alternative public API - Sirene Light
                url = f"https://entreprise.data.gouv.fr/api/sirene/v1/full_text/{dept}"
                response = await client.get(url, params={"per_page": 20})
                if response.status_code == 200:
                    data = response.json()
                    return data.get("etablissement", [])[:10]
        except Exception:
            pass

        # Return mock data if API unavailable
        return [
            {
                "siren": f"12345678{i}",
                "denomination": f"Entreprise Test {i}",
                "activite": "Commerce",
                "effectif": 10 + i * 5,
            }
            for i in range(5)
        ]

    async def _fetch_bodacc(self, territory: str) -> list[dict]:
        """Fetch BODACC announcements."""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    self.API_ENDPOINTS["bodacc"],
                    params={
                        "limit": 20,
                        "refine": f"departement:{territory[:2] if territory else '59'}",
                    },
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("results", [])[:10]
        except Exception:
            pass
        return []

    async def collect(self, frame: EvaluationFrame, evaluation_id: str = None) -> CollectionResult:
        """Collect data based on evaluation frame."""
        eval_id = evaluation_id or str(uuid.uuid4())
        result = CollectionResult(evaluation_id=eval_id)

        all_documents = []

        for source in frame.sources:
            try:
                if source == "sirene":
                    docs = await self._fetch_sirene_sample(frame.territory or "hauts-de-france")
                    all_documents.extend([{"source": "sirene", "data": d} for d in docs])
                    result.sources_used.append("sirene")
                elif source == "bodacc":
                    docs = await self._fetch_bodacc(frame.territory or "59")
                    all_documents.extend([{"source": "bodacc", "data": d} for d in docs])
                    result.sources_used.append("bodacc")
                elif source in ["insee", "datasubvention", "france2030"]:
                    # These require specific API keys, mark as unavailable
                    result.errors.append({"source": source, "error": "API key required"})
            except Exception as e:
                result.errors.append({"source": source, "error": str(e)})

        result.documents = all_documents
        result.document_count = len(all_documents)
        return result


class AnalysteAgent:
    """Agent for analyzing collected data."""

    SYSTEM_PROMPT = """Tu es un analyste de données expert en politiques publiques.
Tu analyses les données collectées et produis des insights pertinents.

Réponds TOUJOURS en JSON avec cette structure:
{
    "statistics": {"entreprises_count": 0, "tendance": "positive/negative/stable"},
    "insights": ["insight 1", "insight 2"],
    "trends": [{"name": "...", "direction": "up/down", "value": 0}],
    "recommendations": ["recommendation 1"]
}"""

    async def analyze(self, collection: CollectionResult, question: str) -> AnalysisResult:
        """Analyze collected data."""
        # Prepare summary of collected data
        data_summary = f"""
Données collectées:
- {collection.document_count} documents
- Sources: {", ".join(collection.sources_used)}
- Échantillon: {json.dumps(collection.documents[:3], default=str, ensure_ascii=False) if collection.documents else "Aucun"}
"""

        prompt = f"""Analyse ces données pour répondre à la question:

Question: {question}

{data_summary}

Produis une analyse avec statistiques, insights et recommandations."""

        result = await call_ollama(prompt, self.SYSTEM_PROMPT)

        return AnalysisResult(
            statistics=result.get("statistics", {"documents_analysés": collection.document_count}),
            insights=result.get("insights", ["Analyse en cours"]),
            trends=result.get("trends", []),
            recommendations=result.get("recommendations", []),
        )


class RedacteurAgent:
    """Agent for generating evaluation reports."""

    SYSTEM_PROMPT = """Tu es un rédacteur expert en rapports d'évaluation de politiques publiques.
Tu produis des rapports structurés, clairs et professionnels en français.

Le rapport doit inclure:
1. Résumé exécutif
2. Contexte et méthodologie
3. Analyse des données
4. Conclusions et recommandations"""

    async def generate(self, frame: EvaluationFrame, analysis: AnalysisResult) -> Report:
        """Generate evaluation report."""
        prompt = f"""Génère un rapport d'évaluation complet basé sur:

Question d'évaluation: {frame.original_question}

Sous-questions analysées:
{chr(10).join(f"- {q}" for q in frame.sub_questions)}

Résultats d'analyse:
- Statistiques: {json.dumps(analysis.statistics, ensure_ascii=False)}
- Insights: {chr(10).join(f"- {i}" for i in analysis.insights)}
- Recommandations: {chr(10).join(f"- {r}" for r in analysis.recommendations)}

Génère un rapport en Markdown avec:
1. Titre
2. Résumé exécutif (3-4 phrases)
3. Méthodologie
4. Analyse détaillée
5. Conclusions et recommandations"""

        content = await call_ollama(prompt, self.SYSTEM_PROMPT, format_json=False)

        # Extract title from first line if it's a heading
        lines = content.strip().split("\n")
        title = lines[0].replace("#", "").strip() if lines else "Rapport d'évaluation"

        return Report(
            title=title,
            summary=analysis.insights[0] if analysis.insights else "Rapport en cours",
            markdown=content,
            sections=[],
            generated_at=datetime.now(),
        )


class EvaluationWorkflow:
    """Orchestrates the complete evaluation workflow."""

    def __init__(
        self, on_status_change: Callable[[WorkflowStatus, str], None] | None = None
    ) -> None:
        self.cadreur = CadreurAgent()
        self.collecteur = CollecteurAgent()
        self.analyste = AnalysteAgent()
        self.redacteur = RedacteurAgent()

        self.status = WorkflowStatus.PENDING
        self._on_status_change = on_status_change
        self._evaluation_id: str | None = None

    def _update_status(self, status: WorkflowStatus, message: str = "") -> None:
        """Update workflow status and notify."""
        self.status = status
        if self._on_status_change:
            self._on_status_change(status, message)

    async def run(self, question: str, evaluation_id: str | None = None) -> WorkflowResult:
        """Execute complete evaluation workflow."""
        self._evaluation_id = evaluation_id or str(uuid.uuid4())

        result = WorkflowResult(
            evaluation_id=self._evaluation_id, question=question, started_at=datetime.now()
        )

        try:
            # Phase 1: Framing
            self._update_status(WorkflowStatus.FRAMING, "Décomposition de la question...")
            frame = await self.cadreur.frame(question)
            result.frame = frame

            # Phase 2: Collection
            self._update_status(
                WorkflowStatus.COLLECTING, f"Collecte depuis {len(frame.sources)} sources..."
            )
            collection = await self.collecteur.collect(frame, self._evaluation_id)
            result.collection = collection

            # Phase 3: Analysis
            self._update_status(WorkflowStatus.ANALYZING, "Analyse statistique en cours...")
            analysis = await self.analyste.analyze(collection, question)
            result.analysis = analysis

            # Phase 4: Report generation
            self._update_status(WorkflowStatus.GENERATING, "Génération du rapport...")
            report = await self.redacteur.generate(frame, analysis)
            result.report = report

            # Await human validation
            self._update_status(WorkflowStatus.AWAITING_VALIDATION, "Rapport prêt pour validation")
            result.status = WorkflowStatus.AWAITING_VALIDATION

        except Exception as e:
            self._update_status(WorkflowStatus.FAILED, str(e))
            result.status = WorkflowStatus.FAILED
            result.errors.append(str(e))

        result.completed_at = datetime.now()
        return result
