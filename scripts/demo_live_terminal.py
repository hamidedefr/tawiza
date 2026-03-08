import asyncio
import time

import httpx


async def demo_terminal():
    print("🚀 Déclenchement d'une exécution de code avec streaming terminal...")

    # Le code Python qui va simuler une progression lente
    code = """
import time
import sys

print("Initializing system analysis...")
time.sleep(1)
print("Scanning directories...")
time.sleep(1)
for i in range(5):
    print(f"Processing chunk {i+1}/5...")
    time.sleep(0.8)

print("SUCCESS: Data processing complete.")
"""

    url = "http://localhost:8000/api/v1/code-execution/execute"

    async with httpx.AsyncClient(timeout=60.0) as client:
        print(f"📡 Envoi de la requête à {url}")
        try:
            response = await client.post(url, json={"code": code, "language": "python"})

            if response.status_code == 200:
                print("✅ Exécution terminée avec succès côté serveur.")
                print("Résultat final :", response.json().get("output"))
            else:
                print(f"❌ Erreur {response.status_code}: {response.text}")
        except Exception as e:
            print(f"❌ Erreur de connexion : {e}")


if __name__ == "__main__":
    asyncio.run(demo_terminal())
