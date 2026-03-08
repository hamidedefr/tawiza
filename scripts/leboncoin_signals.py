#!/usr/bin/env python3
"""
LeBonCoin Signal Detector - MPtoO-V2
Détecte les signaux de cessation d'activité via les annonces LeBonCoin.

Utilise Playwright pour contourner le 403 anti-bot.

Usage:
    python scripts/leboncoin_signals.py --keywords "cessation activité"
    python scripts/leboncoin_signals.py --department 75 --limit 50
    python scripts/leboncoin_signals.py --all-signals
"""

import argparse
import json
import random
import time
from datetime import datetime

from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth

# Mots-clés signaux de fermeture
DEFAULT_KEYWORDS = [
    "cessation activité",
    "cessation d'activité",
    "liquidation",
    "cause fermeture",
    "fermeture commerce",
    "fin d'activité",
    "déstockage fermeture",
    "urgent cause départ",
]


class LeBonCoinPlaywrightCrawler:
    """Crawler Playwright pour LeBonCoin - contourne l'anti-bot."""

    BASE_URL = "https://www.leboncoin.fr"

    def __init__(self, headless: bool = True, delay_range: tuple[float, float] = (1.0, 3.0)):
        self.headless = headless
        self.delay_range = delay_range
        self.playwright = None
        self.browser = None
        self.page = None

    def __enter__(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox",
            ],
        )
        self.context = self.browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="fr-FR",
        )
        # Apply stealth mode to avoid detection
        stealth = Stealth()
        self.page = stealth.use_sync(self.context.new_page())
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def _delay(self):
        """Délai aléatoire entre actions."""
        time.sleep(random.uniform(*self.delay_range))

    def search(
        self,
        keywords: str,
        department: str | None = None,
        limit: int = 20,
    ) -> list[dict]:
        """
        Recherche des annonces sur LeBonCoin via Playwright.
        """
        results = []

        # Construction URL de recherche
        search_url = f"{self.BASE_URL}/recherche?text={keywords.replace(' ', '+')}"
        if department:
            search_url += f"&locations=d_{department}"

        try:
            print(f"🔍 Navigation vers: {search_url}")
            self.page.goto(search_url, wait_until="networkidle", timeout=30000)
            self._delay()

            # Accepter les cookies si popup présente
            try:
                cookie_btn = self.page.locator('button:has-text("Accepter")')
                if cookie_btn.is_visible(timeout=3000):
                    cookie_btn.click()
                    self._delay()
            except:
                pass

            # Attendre le chargement des résultats
            self.page.wait_for_selector('[data-qa-id="aditem_container"]', timeout=10000)

            # Extraire les annonces
            ads = self.page.locator('[data-qa-id="aditem_container"]').all()
            print(f"📊 {len(ads)} annonces trouvées")

            for i, ad in enumerate(ads[:limit]):
                try:
                    # Titre
                    title_el = ad.locator('[data-qa-id="aditem_title"]')
                    title = title_el.text_content() if title_el.count() > 0 else "Sans titre"

                    # Prix
                    price_el = ad.locator('[data-qa-id="aditem_price"]')
                    price_text = price_el.text_content() if price_el.count() > 0 else ""
                    price = None
                    if price_text:
                        # Extraire le nombre du prix
                        import re

                        price_match = re.search(r"[\d\s]+", price_text.replace("\xa0", " "))
                        if price_match:
                            price = int(price_match.group().replace(" ", ""))

                    # Localisation
                    location_el = ad.locator('[data-qa-id="aditem_location"]')
                    location = location_el.text_content() if location_el.count() > 0 else "Inconnue"

                    # URL
                    link_el = ad.locator("a").first
                    href = link_el.get_attribute("href") if link_el.count() > 0 else ""
                    url = f"{self.BASE_URL}{href}" if href and not href.startswith("http") else href

                    # Catégorie
                    category_el = ad.locator('[data-qa-id="aditem_category"]')
                    category = category_el.text_content() if category_el.count() > 0 else ""

                    results.append(
                        {
                            "id": i,
                            "title": title.strip() if title else "Sans titre",
                            "price": price,
                            "location": location.strip() if location else "Inconnue",
                            "category": category.strip() if category else "",
                            "url": url,
                            "matched_keyword": keywords,
                            "scraped_at": datetime.now().isoformat(),
                        }
                    )
                except Exception as e:
                    print(f"⚠️ Erreur extraction annonce {i}: {e}")
                    continue

        except Exception as e:
            print(f"❌ Erreur navigation: {e}")

        return results

    def search_cessation_signals(
        self,
        department: str | None = None,
        limit: int = 30,
    ) -> list[dict]:
        """
        Recherche multi-mots-clés pour signaux de cessation.
        """
        all_results = []
        seen_titles = set()

        for keyword in DEFAULT_KEYWORDS:
            print(f"\n🔍 Recherche: {keyword}")
            results = self.search(keyword, department, limit=limit // len(DEFAULT_KEYWORDS))

            for r in results:
                # Dédupliquer par titre
                if r["title"] not in seen_titles:
                    seen_titles.add(r["title"])
                    all_results.append(r)

            self._delay()

        return all_results


def format_results(results: list[dict]) -> str:
    """Formate les résultats pour affichage."""
    if not results:
        return "❌ Aucun résultat trouvé."

    lines = [f"📊 {len(results)} annonces trouvées:\n"]

    for r in results:
        price = f"{r['price']}€" if r.get("price") else "Prix non indiqué"
        category = f"🏷️ {r.get('category', '')}" if r.get("category") else ""

        lines.append(
            f"{category}\n"
            f"   📦 {r['title'][:60]}\n"
            f"   💰 {price} | 📍 {r.get('location', 'N/A')}\n"
            f"   🔗 {r.get('url', 'N/A')[:70]}...\n"
        )

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="LeBonCoin Signal Detector (Playwright)")
    parser.add_argument("--keywords", "-k", help="Mots-clés de recherche")
    parser.add_argument("--department", "-d", help="Code département (ex: 75)")
    parser.add_argument("--limit", "-l", type=int, default=20, help="Nombre max de résultats")
    parser.add_argument("--json", action="store_true", help="Sortie JSON")
    parser.add_argument(
        "--all-signals", action="store_true", help="Recherche tous les signaux cessation"
    )
    parser.add_argument("--visible", action="store_true", help="Mode visible (non headless)")

    args = parser.parse_args()

    with LeBonCoinPlaywrightCrawler(headless=not args.visible) as crawler:
        if args.all_signals:
            results = crawler.search_cessation_signals(args.department, args.limit)
        elif args.keywords:
            results = crawler.search(args.keywords, args.department, args.limit)
        else:
            # Défaut: recherche signaux cessation
            results = crawler.search_cessation_signals(args.department, args.limit)

        if args.json:
            print(json.dumps(results, indent=2, ensure_ascii=False))
        else:
            print(format_results(results))


if __name__ == "__main__":
    main()
