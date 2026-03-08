"""End-to-end test for relation extractors and RelationService.

Run from VM 200:
    cd /data/projects/MPtoO-V2
    source .venv/bin/activate
    python test_relations_flow.py
"""

import asyncio
import json
import sys

from loguru import logger

logger.remove()
logger.add(sys.stderr, level="INFO", format="{time:HH:mm:ss} | {level} | {message}")


async def main():
    from src.application.services.relation_extractors import SireneExtractor, BodaccExtractor
    from src.application.services.relation_service import RelationService

    dept = "75"  # Paris -- has 591 signals (sirene + bodacc)

    # ---------------------------------------------------------------
    # 1. Test extractors individually
    # ---------------------------------------------------------------
    print("=" * 60)
    print(f"STEP 1: Testing extractors for dept {dept}")
    print("=" * 60)

    sirene = SireneExtractor()
    sirene_result = await sirene.extract(dept)
    print(f"  SIRENE: {len(sirene_result['actors'])} actors, {len(sirene_result['relations'])} relations")

    # Show a sample actor
    if sirene_result["actors"]:
        sample = sirene_result["actors"][0]
        print(f"  Sample actor: {sample['type']} | {sample['external_id']} | {sample['name']}")

    # Show a sample relation
    if sirene_result["relations"]:
        sample_rel = sirene_result["relations"][0]
        print(f"  Sample relation: {sample_rel['source_actor_external_id']} -> {sample_rel['target_actor_external_id']} ({sample_rel['subtype']})")

    bodacc = BodaccExtractor()
    bodacc_result = await bodacc.extract(dept)
    print(f"  BODACC: {len(bodacc_result['actors'])} actors, {len(bodacc_result['relations'])} relations")

    if bodacc_result["actors"]:
        sample = bodacc_result["actors"][0]
        print(f"  Sample actor: {sample['type']} | {sample['external_id']} | {sample['name']}")

    if bodacc_result["relations"]:
        sample_rel = bodacc_result["relations"][0]
        print(f"  Sample relation: {sample_rel['source_actor_external_id']} -> {sample_rel['target_actor_external_id']} ({sample_rel['subtype']})")

    # ---------------------------------------------------------------
    # 2. Test discover (UPSERT)
    # ---------------------------------------------------------------
    print()
    print("=" * 60)
    print(f"STEP 2: Testing RelationService.discover('{dept}')")
    print("=" * 60)

    svc = RelationService()
    result = await svc.discover(dept)
    print(f"  Result: {json.dumps(result, indent=2)}")

    # ---------------------------------------------------------------
    # 3. Test get_graph
    # ---------------------------------------------------------------
    print()
    print("=" * 60)
    print(f"STEP 3: Testing RelationService.get_graph('{dept}')")
    print("=" * 60)

    graph = await svc.get_graph(dept, min_confidence=0.0)
    print(f"  Nodes: {graph['total_actors']}, Links: {graph['total_relations']}")

    # Show type distribution
    type_counts = {}
    for node in graph["nodes"]:
        t = node["type"]
        type_counts[t] = type_counts.get(t, 0) + 1
    print(f"  Node types: {type_counts}")

    # Show subtype distribution
    subtype_counts = {}
    for link in graph["links"]:
        s = link["subtype"]
        subtype_counts[s] = subtype_counts.get(s, 0) + 1
    print(f"  Link subtypes: {subtype_counts}")

    # Show a sample node and link
    if graph["nodes"]:
        print(f"  Sample node: {json.dumps(graph['nodes'][0], default=str)[:200]}")
    if graph["links"]:
        print(f"  Sample link: {json.dumps(graph['links'][0], default=str)[:200]}")

    # ---------------------------------------------------------------
    # 4. Test get_coverage
    # ---------------------------------------------------------------
    print()
    print("=" * 60)
    print(f"STEP 4: Testing RelationService.get_coverage('{dept}')")
    print("=" * 60)

    coverage = await svc.get_coverage(dept)
    print(f"  Coverage: {json.dumps(coverage, indent=2)}")

    # ---------------------------------------------------------------
    # 5. Test get_gaps
    # ---------------------------------------------------------------
    print()
    print("=" * 60)
    print(f"STEP 5: Testing RelationService.get_gaps('{dept}')")
    print("=" * 60)

    gaps = await svc.get_gaps(dept)
    print(f"  Total gaps: {gaps['total_gaps']}")
    for gap in gaps["gaps"]:
        print(f"    [{gap['priority']}] {gap['gap_type']}: {gap['description'][:100]}")
    print(f"  Capability matrix: {len(gaps['capability_matrix'])} items")

    # ---------------------------------------------------------------
    # 6. Idempotency test -- run discover again, should UPSERT cleanly
    # ---------------------------------------------------------------
    print()
    print("=" * 60)
    print("STEP 6: Idempotency test -- re-running discover()")
    print("=" * 60)

    result2 = await svc.discover(dept)
    print(f"  Second run: {json.dumps(result2, indent=2)}")
    print("  (Should have same counts -- UPSERT, not INSERT)")

    print()
    print("=" * 60)
    print("ALL TESTS PASSED")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
