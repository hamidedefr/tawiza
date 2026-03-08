import asyncio
import time
from uuid import uuid4

from loguru import logger

from src.infrastructure.agents.tajine.tajine_agent import TAJINEAgent

# Désactiver les logs verbeux pour voir uniquement les erreurs
logger.remove()
logger.add(lambda msg: print(msg), level="ERROR")


async def run_scenario(agent, name, prompt, session_id):
    print(f"🚩 Lancement Scénario: {name}")
    start = time.time()
    try:
        # On force le mode complet pour maximiser la charge
        result = await agent.execute_task(
            {"prompt": prompt, "cognitive_depth": 5, "mode": "complete", "session_id": session_id}
        )
        duration = time.time() - start
        confidence = result.get("confidence", 0)
        print(f"  ✅ Terminé en {duration:.1f}s | Confiance: {confidence * 100:.1f}%")

        # Vérification de l'intelligence : Est-ce qu'il y a des sources ?
        sources = result.get("context", {}).get("sources", [])
        if not sources:
            print("  ⚠️ ALERTE : Analyse générée sans sources réelles (Hallucination possible)")
        else:
            print(f"  🔍 Sources trouvées: {len(sources)}")

    except Exception as e:
        print(f"  ❌ CRASH dans {name}: {str(e)}")


async def stress_test():
    agent = TAJINEAgent()
    session_id = f"stress-test-{uuid4().hex[:4]}"

    print("🔥 DÉMARRAGE DU STRESS-TEST TAJINE\n")

    scenarios = [
        (
            "AMBIGUÏTÉ",
            "Analyse le risque pour une boîte qui s'appelle 'Boulangerie' à Paris sans donner de SIREN",
            session_id,
        ),
        (
            "CONTRADICTION",
            "Vérifie si l'entreprise 552032534 est basée à Marseille (Indice: elle est à Roissy)",
            session_id,
        ),
        (
            "LIMITE",
            "Simule une inflation de 500% sur 10 ans dans le secteur du BTP en Creuse",
            session_id,
        ),
        (
            "COMPLEXITÉ",
            "Compare l'impact de la fermeture d'une usine automobile sur 3 départements limitrophes",
            session_id,
        ),
    ]

    # Lancement en parallèle pour tester la charge
    tasks = [run_scenario(agent, s[0], s[1], s[2]) for s in scenarios]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(stress_test())
