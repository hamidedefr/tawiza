#!/usr/bin/env python3
"""Test script for LLM integration in MPtoO.

Usage:
    python scripts/test_llm_integration.py
    python scripts/test_llm_integration.py --quick     # Skip vision test
    python scripts/test_llm_integration.py --vision    # Vision test only
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


async def test_ollama_connection():
    """Test 1: Verify Ollama is reachable."""
    print("\n" + "=" * 60)
    print("TEST 1: Connexion Ollama")
    print("=" * 60)

    from src.infrastructure.llm import OllamaClient

    client = OllamaClient(base_url="http://localhost:11434")

    try:
        # Simple generation test
        response = await client.generate(
            prompt="Dis 'Bonjour MPtoO!' en une phrase.",
            model="qwen3:14b",
        )
        print(f"✅ Ollama répond: {response[:100]}...")
        return True
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


async def test_adaptive_provider():
    """Test 2: AdaptiveLLMProvider text mode."""
    print("\n" + "=" * 60)
    print("TEST 2: AdaptiveLLMProvider (mode texte)")
    print("=" * 60)

    from src.infrastructure.llm import AdaptiveLLMProvider, OllamaClient

    client = OllamaClient(
        base_url="http://localhost:11434",
        model="qwen3:14b",
    )

    provider = AdaptiveLLMProvider(
        client=client,
        text_model="qwen3:14b",
        vision_model="qwen3-vl:32b",
    )

    try:
        response = await provider.generate(
            prompt="Qu'est-ce qu'un SIRET en France? Réponds en 2 phrases.",
            system="Tu es un expert en données d'entreprises françaises.",
        )
        print(f"✅ Provider répond:\n{response[:300]}...")
        return True
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


async def test_debate_system():
    """Test 3: Full debate system with LLM."""
    print("\n" + "=" * 60)
    print("TEST 3: Système de débat complet avec LLM")
    print("=" * 60)

    from src.domain.debate import DebateMode
    from src.infrastructure.llm import create_debate_system_with_llm

    try:
        debate = create_debate_system_with_llm(
            text_model="qwen3:14b",
            mode=DebateMode.STANDARD,  # 3 agents (plus rapide)
        )

        # Données de test simulant une recherche d'entreprise
        test_data = {
            "results": [
                {
                    "source": "sirene",
                    "siret": "44306184100047",
                    "name": "GOOGLE FRANCE",
                    "address": "8 RUE DE LONDRES 75009 PARIS",
                },
                {
                    "source": "bodacc",
                    "siret": "44306184100047",
                    "name": "GOOGLE FRANCE SARL",
                    "date": "2023-06-15",
                },
            ],
            "sources": ["sirene", "bodacc"],
        }

        print("🔄 Validation en cours (3 agents)...")
        result = await debate.validate("Google France", test_data)

        print("\n✅ Validation terminée!")
        print(f"   Confiance finale: {result.final_confidence}%")
        print(f"   Messages: {len(result.messages)}")

        print("\n📝 Résumé des agents:")
        for msg in result.messages:
            preview = msg.content[:100].replace("\n", " ")
            print(f"   • {msg.agent}: {preview}...")

        return True
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_vision_analyzer():
    """Test 4: Vision analysis (requires image)."""
    print("\n" + "=" * 60)
    print("TEST 4: VisionAnalyzer (analyse d'image)")
    print("=" * 60)

    from src.infrastructure.llm import AdaptiveLLMProvider, OllamaClient, VisionAnalyzer

    client = OllamaClient(
        base_url="http://localhost:11434",
        vision_model="qwen3-vl:32b",
    )

    provider = AdaptiveLLMProvider(
        client=client,
        text_model="qwen3-vl:32b",
        vision_model="qwen3-vl:32b",
    )

    analyzer = VisionAnalyzer(provider=provider)

    # Create a simple test image (1x1 red pixel PNG)
    # This is a minimal valid PNG to test the pipeline
    test_image = bytes(
        [
            0x89,
            0x50,
            0x4E,
            0x47,
            0x0D,
            0x0A,
            0x1A,
            0x0A,  # PNG signature
            0x00,
            0x00,
            0x00,
            0x0D,
            0x49,
            0x48,
            0x44,
            0x52,  # IHDR chunk
            0x00,
            0x00,
            0x00,
            0x01,
            0x00,
            0x00,
            0x00,
            0x01,  # 1x1
            0x08,
            0x02,
            0x00,
            0x00,
            0x00,
            0x90,
            0x77,
            0x53,
            0xDE,
            0x00,
            0x00,
            0x00,
            0x0C,
            0x49,
            0x44,
            0x41,
            0x54,
            0x08,
            0xD7,
            0x63,
            0xF8,
            0xFF,
            0xFF,
            0x3F,
            0x00,
            0x05,
            0xFE,
            0x02,
            0xFE,
            0xDC,
            0xCC,
            0x59,
            0xE7,
            0x00,
            0x00,
            0x00,
            0x00,
            0x49,
            0x45,
            0x4E,
            0x44,
            0xAE,
            0x42,
            0x60,
            0x82,
        ]
    )

    try:
        print("🔄 Analyse d'image de test...")
        result = await analyzer.analyze_screenshot(
            image_bytes=test_image,
            prompt="Décris cette image en une phrase.",
        )
        print(f"✅ Vision répond: {result[:200]}...")
        return True
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


async def main():
    """Run all tests."""
    print("\n" + "🚀 " + "=" * 56 + " 🚀")
    print("     TEST D'INTÉGRATION LLM - MPtoO")
    print("🚀 " + "=" * 56 + " 🚀")

    quick_mode = "--quick" in sys.argv
    vision_only = "--vision" in sys.argv

    results = {}

    if vision_only:
        results["Vision"] = await test_vision_analyzer()
    else:
        results["Ollama"] = await test_ollama_connection()
        results["Provider"] = await test_adaptive_provider()
        results["Debate"] = await test_debate_system()

        if not quick_mode:
            results["Vision"] = await test_vision_analyzer()

    # Summary
    print("\n" + "=" * 60)
    print("RÉSUMÉ")
    print("=" * 60)

    all_passed = True
    for name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {name}: {status}")
        if not passed:
            all_passed = False

    print("\n" + ("🎉 Tous les tests passent!" if all_passed else "⚠️ Certains tests ont échoué"))

    return 0 if all_passed else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
