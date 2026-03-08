#!/usr/bin/env python3
"""Test script for MCP Server.

Tests the MCP tools without needing Cherry Studio.

Usage:
    python scripts/test_mcp_server.py
    python scripts/test_mcp_server.py --tool sirene_search --query "startup IA Lille"
"""

import asyncio
import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


async def test_tool(tool_name: str, **kwargs) -> dict:
    """Test a single MCP tool."""
    from src.infrastructure.mcp.server import mcp

    # Get the tool function
    tool_func = mcp._tool_manager._tools.get(tool_name)
    if not tool_func:
        return {"error": f"Tool '{tool_name}' not found"}

    # Call the tool
    result = await tool_func.fn(**kwargs)

    # Parse JSON result
    try:
        return json.loads(result)
    except json.JSONDecodeError:
        return {"raw": result}


async def run_tests():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("TEST MCP SERVER - MPtoO")
    print("=" * 60)

    # Test 1: List tools
    print("\n[TEST 1] Liste des outils MCP")
    print("-" * 40)

    from src.infrastructure.mcp.server import mcp

    tools = list(mcp._tool_manager._tools.keys())
    print(f"✓ {len(tools)} outils disponibles:")
    for t in sorted(tools):
        print(f"  - {t}")

    # Test 2: SIRENE search
    print("\n[TEST 2] Recherche SIRENE")
    print("-" * 40)

    result = await test_tool("sirene_search", query="startup IA Lille", limit=3)
    if result.get("success"):
        print(f"✓ {result.get('count', 0)} entreprises trouvées")
        for e in result.get("enterprises", [])[:3]:
            print(f"  - {e.get('nom', 'N/A')} ({e.get('siret', 'N/A')})")
    else:
        print(f"⚠ Erreur: {result.get('error', 'Unknown')}")

    # Test 3: Géocodage
    print("\n[TEST 3] Géocodage")
    print("-" * 40)

    result = await test_tool("geo_locate", address="10 rue de la Paix, Paris")
    if result.get("success"):
        print(f"✓ Adresse trouvée: {result.get('formatted_address')}")
        print(f"  Coordonnées: {result.get('lat')}, {result.get('lon')}")
    else:
        print(f"⚠ Erreur: {result.get('error', 'Unknown')}")

    # Test 4: Chat
    print("\n[TEST 4] Chat Assistant")
    print("-" * 40)

    result = await test_tool(
        "mptoo_chat",
        message="Quelles entreprises font de l'IA à Lille?",
        mode="data",
    )
    if result.get("success"):
        data = result.get("data", {})
        print(f"✓ {data.get('total', 0)} résultats trouvés")
        print(f"  Sources: {result.get('sources_used', [])}")
    else:
        print(f"⚠ Erreur: {result.get('error', 'Unknown')}")

    # Test 5: Resources
    print("\n[TEST 5] Resources MCP")
    print("-" * 40)

    from src.infrastructure.mcp.server import get_agents, get_sources

    sources = get_sources()
    agents = get_agents()
    print(f"✓ Resource 'mptoo://sources': {len(sources)} caractères")
    print(f"✓ Resource 'mptoo://agents': {len(agents)} caractères")

    print("\n" + "=" * 60)
    print("TESTS TERMINÉS")
    print("=" * 60)


async def test_single_tool(tool_name: str, query: str):
    """Test a single tool with query."""
    print(f"\nTest de '{tool_name}' avec query='{query}'")
    print("-" * 40)

    result = await test_tool(tool_name, query=query, limit=5)
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str)[:2000])


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Test MCP Server")
    parser.add_argument("--tool", help="Specific tool to test")
    parser.add_argument("--query", help="Query for the tool", default="startup IA Lille")
    args = parser.parse_args()

    if args.tool:
        asyncio.run(test_single_tool(args.tool, args.query))
    else:
        asyncio.run(run_tests())
