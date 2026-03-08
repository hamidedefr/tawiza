import asyncio
import json
from uuid import UUID

from src.infrastructure.agents.tajine.investigation.investigation_tool import (
    InvestigateEnterpriseTool,
)
from src.infrastructure.agents.tajine.tajine_agent import TAJINEAgent


async def test_power():
    print("🚀 DÉMARRAGE DU TEST DE PUISSANCE TAJINE\n")
    agent = TAJINEAgent()

    # --- TEST 1: INVESTIGATION RÉELLE ---
    print("🔍 TEST 1 : Enquête Bayésienne sur Air France (SIREN: 552032534)")
    investigator = InvestigateEnterpriseTool()
    report = await investigator.execute(siren="552032534", context="Test de puissance")
    report_data = report.to_dict()

    print(f"  ✅ Dénomination trouvée : {report_data['denomination']}")
    print(
        f"  📊 Probabilité de risque (Posterior) : {report_data['summary']['posterior'] * 100:.2f}%"
    )
    print(f"  🧠 Niveau de risque calculé : {report_data['summary']['risk_level']}")
    print(f"  📈 Confiance de l'enquête : {report_data['summary']['confidence'] * 100:.0f}%")
    print("\n")

    # --- TEST 2: SIMULATION MONTE CARLO ---
    print("🎲 TEST 2 : Simulation Mathématique (Département du Rhône - 69)")
    from src.application.services.territorial_stats import get_stats_service

    stats_service = get_stats_service()

    print("  ⏳ Génération de scénarios prédictifs...")
    sim_data = await stats_service.get_radar_data("69")

    if sim_data:
        print(f"  ✅ Données de simulation générées pour {len(sim_data)} indicateurs.")
        print(f"  🎯 Exemple d'indicateur réel : {sim_data[0].metric} = {sim_data[0].value}")

    # --- TEST 3 : CYCLE PPDSL ---
    print("\n🧠 TEST 3 : Vérification du Cycle Cognitif PPDSL")
    prompt = "Analyse le dynamisme de la tech à Paris"

    # On observe la perception
    perception = await agent.perceive(prompt)
    print(
        f"  👁️  Perception : Intent='{perception.get('intent')}', Territory='{perception.get('territory')}'"
    )

    # On observe la planification
    plan = await agent.plan(perception)
    print(f"  📋 Planification : {len(plan.get('subtasks', []))} étapes stratégiques prévues.")
    for i, step in enumerate(plan.get("subtasks", [])):
        print(
            f"     {i + 1}. {step.get('description', step.get('name', 'Action'))} (outil: {step['tool']})"
        )

    print("\n✅ TEST DE PUISSANCE TERMINÉ : L'ALGORITHME EST OPÉRATIONNEL")


if __name__ == "__main__":
    asyncio.run(test_power())
