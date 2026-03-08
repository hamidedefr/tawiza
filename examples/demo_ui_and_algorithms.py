#!/usr/bin/env python3
"""
Demo: Beautiful CLI UI and Algorithmic Backend

Demonstrates:
1. Themed CLI output with all 8 themes
2. Table, Tree, and Chart formatters
3. LRU, LFU, and Multi-level caching
4. Token Bucket rate limiting
5. Interactive components

Run: python examples/demo_ui_and_algorithms.py
"""

import time

from rich.console import Console

# UI Components
from src.cli.ui.themes import get_theme, list_themes

from src.cli.ui.components import Panel, Progress, Spinner
from src.cli.ui.formatters import (
    ChartFormatter,
    TableFormatter,
    TreeFormatter,
    create_stars,
    format_number,
)
from src.cli.ui.interactive import Confirm, Menu, Prompt

# Algorithms
from src.infrastructure.caching import LFUCache, LRUCache, MultiLevelCache
from src.infrastructure.rate_limiting import RateLimiter, TokenBucket


def demo_themes():
    """Demonstrate all themes"""
    print("\n" + "=" * 70)
    print("🎨 THEME SHOWCASE")
    print("=" * 70 + "\n")

    for theme_name in list_themes():
        theme = get_theme(theme_name)
        console = Console(theme=theme.to_rich_theme())

        console.print(f"\n[{theme.primary}]╔═══ Theme: {theme_name.upper()} ═══╗[/]")
        console.print(
            f"[{theme.primary}]Primary[/] • [{theme.secondary}]Secondary[/] • [{theme.success}]Success[/] • [{theme.warning}]Warning[/] • [{theme.error}]Error[/] • [{theme.accent}]Accent[/]"
        )
        console.print(f"[{theme.primary}]╚{'═' * 30}╝[/]")


def demo_table_formatter():
    """Demonstrate table formatting"""
    print("\n" + "=" * 70)
    print("📊 TABLE FORMATTER - Prompt Templates")
    print("=" * 70 + "\n")

    # Create table with cyberpunk theme
    formatter = TableFormatter(
        theme="cyberpunk",
        title="🎨 PROMPT TEMPLATES",
        show_lines=True,
    )

    # Add columns
    formatter.add_column("Category", style="bold")
    formatter.add_column("Template", style="cyan")
    formatter.add_column("Usage", justify="right")
    formatter.add_column("Rating")

    # Add rows with real data
    formatter.add_row(
        "🤖 ML",
        "text_classification",
        format_number(3500),
        create_stars(3500),
    )
    formatter.add_row(
        "🤖 ML",
        "sentiment_analysis",
        format_number(1800),
        create_stars(1800),
    )
    formatter.add_row(
        "📱 Browser",
        "browser_navigation",
        format_number(1200),
        create_stars(1200),
    )
    formatter.add_row(
        "💻 Code",
        "code_review",
        format_number(756),
        create_stars(756),
    )

    # Render
    formatter.render()


def demo_tree_formatter():
    """Demonstrate tree formatting"""
    print("\n" + "=" * 70)
    print("🌳 TREE FORMATTER - Hierarchical View")
    print("=" * 70 + "\n")

    # Create tree with ocean theme
    formatter = TreeFormatter("📦 Prompt Templates", theme="ocean")

    # Add ML branch
    ml = formatter.add("🤖 Machine Learning")
    ml.add("📊 text_classification (3.5K uses)")
    ml.add("💭 sentiment_analysis (1.8K uses)")
    ml.add("❓ question_answering (1.5K uses)")

    # Add Browser branch
    browser = formatter.add("📱 Browser Automation")
    browser.add("🌐 browser_navigation (1.2K uses)")
    browser.add("🎯 browser_task_detailed (856 uses)")

    # Add Code branch
    code = formatter.add("💻 Code & Dev")
    code.add("⚙️ code_generation (987 uses)")
    code.add("🔍 code_review (756 uses)")

    # Render
    formatter.render()


def demo_chart_formatter():
    """Demonstrate chart formatting"""
    print("\n" + "=" * 70)
    print("📈 CHART FORMATTER - Usage Statistics")
    print("=" * 70 + "\n")

    formatter = ChartFormatter(theme="sunset")

    # Bar chart
    print("Bar Chart - Template Usage:\n")
    data = {
        "text_classification": 3500,
        "sentiment_analysis": 1800,
        "summarization": 2300,
        "question_answering": 1500,
        "code_review": 756,
    }
    print(formatter.bar_chart(data, max_width=40))

    # Sparkline
    print("\n\nSparkline - Requests per hour (24h):\n")
    hourly_requests = [
        45,
        52,
        48,
        55,
        62,
        71,
        85,
        92,
        88,
        95,
        102,
        108,
        115,
        122,
        118,
        125,
        132,
        128,
        135,
        142,
        138,
        145,
        148,
        142,
    ]
    print(formatter.sparkline(hourly_requests))

    # Percentage bars
    print("\n\nPercentage Bars - Cache Hit Rates:\n")
    print(f"L1 Cache: {formatter.percentage_bar(85, width=30)}")
    print(f"L2 Cache: {formatter.percentage_bar(65, width=30)}")
    print(f"L3 Cache: {formatter.percentage_bar(45, width=30)}")


def demo_lru_cache():
    """Demonstrate LRU cache"""
    print("\n" + "=" * 70)
    print("💾 LRU CACHE - Least Recently Used (O(1))")
    print("=" * 70 + "\n")

    # Create LRU cache
    cache = LRUCache(capacity=3, ttl_seconds=None)

    # Add items
    print("Adding items to cache (capacity=3):")
    cache.put("a", "value_a")
    print(f"  put('a') → {cache}")
    cache.put("b", "value_b")
    print(f"  put('b') → {cache}")
    cache.put("c", "value_c")
    print(f"  put('c') → {cache}")

    # Access item (moves to end)
    print("\nAccessing 'a' (marks as recently used):")
    value = cache.get("a")
    print(f"  get('a') → {value}")
    print("  Order now: a (most recent) → c → b")

    # Add new item (evicts LRU)
    print("\nAdding 'd' (cache full, will evict LRU):")
    cache.put("d", "value_d")
    print("  put('d') → Evicted 'b' (least recently used)")
    print(f"  {cache}")

    # Show stats
    print("\nCache Statistics:")
    stats = cache.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")


def demo_lfu_cache():
    """Demonstrate LFU cache"""
    print("\n" + "=" * 70)
    print("📊 LFU CACHE - Least Frequently Used (O(1))")
    print("=" * 70 + "\n")

    # Create LFU cache
    cache = LFUCache(capacity=3)

    # Add items
    print("Adding items to cache (capacity=3):")
    cache.put("a", "value_a")
    print("  put('a') → freq=1")
    cache.put("b", "value_b")
    print("  put('b') → freq=1")
    cache.put("c", "value_c")
    print("  put('c') → freq=1")

    # Access items (increase frequency)
    print("\nAccessing items (increases frequency):")
    cache.get("a")
    cache.get("a")
    print("  get('a') x2 → freq=3")
    cache.get("b")
    print("  get('b') x1 → freq=2")
    # c stays at freq=1

    # Add new item (evicts LFU)
    print("\nAdding 'd' (cache full, will evict LFU):")
    cache.put("d", "value_d")
    print("  put('d') → Evicted 'c' (freq=1, least frequently used)")
    print(f"  {cache}")

    # Show stats
    print("\nCache Statistics:")
    stats = cache.get_stats()
    print(f"  Frequency distribution: {stats['frequency_distribution']}")
    print(f"  Hit rate: {stats['hit_rate']:.1f}%")


def demo_multi_level_cache():
    """Demonstrate multi-level cache"""
    print("\n" + "=" * 70)
    print("🎯 MULTI-LEVEL CACHE - Cascading L1 → L2 → L3")
    print("=" * 70 + "\n")

    # Create multi-level cache
    cache = MultiLevelCache(
        l1_capacity=2,  # Small L1 for demo
        l2_capacity=4,  # Medium L2
        l1_ttl=None,
        l2_ttl=None,
        write_through=True,
    )

    print("Architecture:")
    print("  L1 (LRU, 2 items) → L2 (LFU, 4 items) → L3 (Redis)")
    print("  ↓ hit               ↓ hit              ↓ hit")
    print("  Return           Promote to L1      Promote to L1+L2\n")

    # Add items
    print("Adding items:")
    for i in range(1, 6):
        cache.put(f"key{i}", f"value{i}")
        print(f"  put('key{i}')")

    # Access pattern
    print("\nAccess pattern:")
    cache.get("key2")
    print("  get('key2') → L2 hit, promoted to L1")
    cache.get("key3")
    print("  get('key3') → L2 hit, promoted to L1")
    cache.get("key1")
    print("  get('key1') → L2 hit, promoted to L1")

    # Show stats
    print("\nMulti-Level Cache Statistics:")
    stats = cache.get_stats()
    print("\n  Overall:")
    print(f"    Total requests: {stats['overall']['total_requests']}")
    print(f"    Hit rate: {stats['overall']['hit_rate']:.1f}%")
    print("\n  L1 (LRU):")
    print(f"    Hits: {stats['l1']['hits']} ({stats['l1']['hit_percentage']:.1f}%)")
    print(f"    Size: {stats['l1']['size']}/{stats['l1']['capacity']}")
    print("\n  L2 (LFU):")
    print(f"    Hits: {stats['l2']['hits']} ({stats['l2']['hit_percentage']:.1f}%)")
    print(f"    Size: {stats['l2']['size']}/{stats['l2']['capacity']}")


def demo_token_bucket():
    """Demonstrate token bucket rate limiting"""
    print("\n" + "=" * 70)
    print("🚦 TOKEN BUCKET - Rate Limiting (O(1))")
    print("=" * 70 + "\n")

    # Create token bucket
    bucket = TokenBucket(capacity=10, refill_rate=2)  # 2 tokens/sec, burst 10

    print("Configuration:")
    print(f"  Capacity: {bucket.capacity} tokens (max burst)")
    print(f"  Refill rate: {bucket.refill_rate} tokens/second")
    print(f"  Current tokens: {bucket.tokens:.1f}\n")

    # Consume tokens
    print("Consuming tokens:")
    for i in range(1, 6):
        consumed = bucket.consume(2)
        status = "✅ ALLOWED" if consumed else "❌ REJECTED"
        print(f"  Request {i}: consume(2) → {status} (tokens: {bucket.tokens:.1f})")

    # Wait for refill
    print("\n⏳ Waiting 2 seconds for refill...")
    time.sleep(2)
    bucket._refill()
    print(f"  Tokens after refill: {bucket.tokens:.1f}")

    # Try again
    print("\nAfter refill:")
    consumed = bucket.consume(4)
    status = "✅ ALLOWED" if consumed else "❌ REJECTED"
    print(f"  Request: consume(4) → {status} (tokens: {bucket.tokens:.1f})")


def demo_rate_limiter():
    """Demonstrate multi-key rate limiter"""
    print("\n" + "=" * 70)
    print("🎛️  RATE LIMITER - Multi-key Rate Limiting")
    print("=" * 70 + "\n")

    # Create rate limiter
    limiter = RateLimiter(capacity=5, refill_rate=1)  # 1 req/s, burst 5

    print("Configuration: 5 requests burst, 1 req/sec sustained\n")

    # Different users
    users = ["user_alice", "user_bob", "user_charlie"]

    print("Simulating requests from 3 users:")
    for i in range(8):
        user = users[i % 3]
        allowed = limiter.allow(user)
        status = "✅" if allowed else "❌"
        wait = limiter.wait_time(user)
        print(f"  {status} {user}: {'ALLOWED' if allowed else f'REJECTED (wait {wait:.1f}s)'}")

    # Show stats
    print("\nRate Limiter Statistics:")
    stats = limiter.get_stats()
    for key, value in stats.items():
        if key != "capacity" and key != "refill_rate":
            print(f"  {key}: {value}")


def demo_progress():
    """Demonstrate progress bar"""
    print("\n" + "=" * 70)
    print("⏳ PROGRESS BAR - Task Tracking")
    print("=" * 70 + "\n")

    with Progress(theme="matrix", show_time_remaining=True) as progress:
        task = progress.add_task("Processing templates", total=100)

        for i in range(100):
            progress.update(task, advance=1)
            time.sleep(0.02)  # Simulate work


def main():
    """Run all demos"""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "🎨 CLI UI & ALGORITHMS DEMO" + " " * 25 + "║")
    print("╚" + "=" * 68 + "╝")

    # UI Demos
    demo_themes()
    demo_table_formatter()
    demo_tree_formatter()
    demo_chart_formatter()

    # Algorithm Demos
    demo_lru_cache()
    demo_lfu_cache()
    demo_multi_level_cache()
    demo_token_bucket()
    demo_rate_limiter()
    demo_progress()

    # Summary
    print("\n" + "=" * 70)
    print("✨ DEMO COMPLETE")
    print("=" * 70)
    print("\n📚 What you saw:")
    print("  • 8 beautiful themes")
    print("  • Table, Tree, Chart formatters")
    print("  • LRU Cache (O(1) get/put)")
    print("  • LFU Cache (O(1) operations)")
    print("  • Multi-level Cache (L1 → L2 → L3)")
    print("  • Token Bucket rate limiting")
    print("  • Progress bars and spinners")
    print("\n🚀 Ready for production!\n")


if __name__ == "__main__":
    main()
