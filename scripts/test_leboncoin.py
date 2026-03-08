#!/usr/bin/env python3
"""Test simple LeBonCoin avec screenshot debug."""

import time

from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--disable-dev-shm-usage",
            "--no-sandbox",
        ],
    )
    context = browser.new_context(
        viewport={"width": 1920, "height": 1080},
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        locale="fr-FR",
    )
    page = context.new_page()

    # Aller sur LeBonCoin
    print("🔍 Navigation vers LeBonCoin...")
    page.goto(
        "https://www.leboncoin.fr/recherche?text=liquidation",
        wait_until="domcontentloaded",
        timeout=30000,
    )
    time.sleep(5)  # Attendre le rendu

    # Screenshot
    page.screenshot(path="/tmp/leboncoin_debug.png")
    print("📸 Screenshot sauvé: /tmp/leboncoin_debug.png")

    # Voir le HTML
    html = page.content()
    print(f"📄 HTML length: {len(html)}")

    # Chercher les patterns
    if "captcha" in html.lower():
        print("⚠️ CAPTCHA détecté!")
    if "robot" in html.lower():
        print("⚠️ Détection robot!")
    if "aditem" in html.lower():
        print("✅ Annonces présentes!")

    browser.close()
