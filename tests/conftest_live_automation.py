"""
Shared fixtures for LIVE automation test suite.

Provides:
- Mock HTTP clients
- Mock Ollama responses
- Browser mocks
- Test data generators
- Fixture helpers
"""

import asyncio
import json
from collections.abc import AsyncIterator
from io import BytesIO
from pathlib import Path
from typing import Any, Dict
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
import pytest_asyncio
from PIL import Image

# ============================================================================
# OLLAMA MOCKS
# ============================================================================


class MockOllamaResponse:
    """Mock Ollama API response."""

    def __init__(self, response_text: str, stream: bool = False):
        self.response_text = response_text
        self.stream = stream
        self.status_code = 200

    def json(self):
        """Return JSON response."""
        if self.stream:
            return {"response": self.response_text}
        return {"response": self.response_text}

    async def raise_for_status(self):
        """Simulate raise_for_status."""
        if self.status_code >= 400:
            raise httpx.HTTPStatusError(
                f"{self.status_code}", request=MagicMock(), response=MagicMock()
            )

    async def aiter_lines(self) -> AsyncIterator[str]:
        """Stream lines of response."""
        words = self.response_text.split()
        for word in words:
            yield json.dumps({"response": word + " "})


class MockOllamaChatResponse:
    """Mock Ollama chat API response."""

    def __init__(self, message: str):
        self.message = message
        self.status_code = 200

    def json(self):
        """Return JSON response."""
        return {"message": {"content": self.message}}

    async def raise_for_status(self):
        """Simulate raise_for_status."""
        if self.status_code >= 400:
            raise httpx.HTTPStatusError(
                f"{self.status_code}", request=MagicMock(), response=MagicMock()
            )

    async def aiter_lines(self) -> AsyncIterator[str]:
        """Stream lines of response."""
        words = self.message.split()
        for word in words:
            yield json.dumps({"message": {"content": word + " "}})


class MockOllamaHealthResponse:
    """Mock Ollama health check response."""

    def __init__(self, models: list = None):
        self.models = models or [{"name": "qwen3-coder:30b"}, {"name": "llava:13b"}]
        self.status_code = 200

    def json(self):
        """Return JSON response."""
        return {"models": self.models}

    async def raise_for_status(self):
        """Simulate raise_for_status."""
        pass


@pytest.fixture
def mock_ollama_generate_response():
    """Mock response for text generation."""
    return MockOllamaResponse("The capital of France is Paris.")


@pytest.fixture
def mock_ollama_chat_response():
    """Mock response for chat completion."""
    return MockOllamaChatResponse("Hello! How can I help you today?")


@pytest.fixture
def mock_ollama_health_response():
    """Mock response for health check."""
    return MockOllamaHealthResponse()


@pytest.fixture
def mock_ollama_extraction_response():
    """Mock response for data extraction."""
    response_data = {"items": ["Item 1", "Item 2", "Item 3"], "count": 3, "confidence": 0.95}
    return MockOllamaResponse(json.dumps(response_data))


@pytest.fixture
def mock_ollama_action_response():
    """Mock response for web action guidance."""
    action_data = {
        "action": "click",
        "selector": "button.submit",
        "reasoning": "Click the submit button",
        "confidence": 0.92,
    }
    return MockOllamaResponse(json.dumps(action_data))


# ============================================================================
# SCREENSHOT FIXTURES
# ============================================================================


@pytest.fixture
def sample_screenshot_data():
    """Generate sample screenshot as bytes."""
    img = Image.new("RGB", (1280, 720), color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()


@pytest.fixture
def sample_screenshot_file(tmp_path, sample_screenshot_data):
    """Create temporary screenshot file."""
    path = tmp_path / "test_screenshot.png"
    path.write_bytes(sample_screenshot_data)
    return str(path)


@pytest.fixture
def screenshot_with_content(tmp_path):
    """Create screenshot with visible content."""
    img = Image.new("RGB", (1280, 720), color="white")
    from PIL import ImageDraw

    draw = ImageDraw.Draw(img)
    # Draw some visible elements
    draw.rectangle([100, 100, 300, 150], fill="blue")  # Blue box
    draw.text((110, 110), "Submit Button", fill="white")

    path = tmp_path / "content_screenshot.png"
    img.save(path)
    return str(path)


# ============================================================================
# HTML FIXTURES
# ============================================================================


@pytest.fixture
def sample_html_simple():
    """Simple HTML for testing."""
    return """
    <html>
        <head><title>Test Page</title></head>
        <body>
            <h1>Welcome</h1>
            <p>This is test content.</p>
        </body>
    </html>
    """


@pytest.fixture
def sample_html_form():
    """HTML with form elements."""
    return """
    <html>
        <head><title>Form</title></head>
        <body>
            <form id="test-form">
                <input id="name" type="text" placeholder="Name">
                <input id="email" type="email" placeholder="Email">
                <textarea id="message">Message</textarea>
                <button type="submit">Submit</button>
            </form>
        </body>
    </html>
    """


@pytest.fixture
def sample_html_complex():
    """Complex HTML with various elements."""
    return """
    <html>
        <head>
            <title>E-Commerce Site</title>
        </head>
        <body>
            <nav>
                <a href="/">Home</a>
                <a href="/products">Products</a>
                <a href="/cart">Cart</a>
            </nav>
            <div class="products">
                <div class="product">
                    <h3>Product 1</h3>
                    <p class="price">$99.99</p>
                    <button class="add-to-cart">Add to Cart</button>
                </div>
                <div class="product">
                    <h3>Product 2</h3>
                    <p class="price">$149.99</p>
                    <button class="add-to-cart">Add to Cart</button>
                </div>
            </div>
        </body>
    </html>
    """


@pytest.fixture
def sample_html_with_api_elements():
    """HTML with data attributes for API testing."""
    return """
    <html>
        <body>
            <div data-api="users" data-endpoint="/api/users">
                <span data-field="id">123</span>
                <span data-field="name">John Doe</span>
                <span data-field="email">john@example.com</span>
            </div>
        </body>
    </html>
    """


# ============================================================================
# TASK CONFIGURATION FIXTURES
# ============================================================================


@pytest.fixture
def task_navigate():
    """Task configuration for navigation."""
    return {"url": "https://example.com", "action": "navigate"}


@pytest.fixture
def task_extract():
    """Task configuration for data extraction."""
    return {
        "url": "https://example.com",
        "action": "extract",
        "selectors": {"title": "h1", "text": "p"},
    }


@pytest.fixture
def task_fill_form():
    """Task configuration for form filling."""
    return {
        "url": "https://example.com/form",
        "action": "fill_form",
        "selectors": {"name": "#name-input", "email": "#email-input"},
        "data": {"name": "Test User", "email": "test@example.com"},
    }


@pytest.fixture
def task_click():
    """Task configuration for element clicking."""
    return {"url": "https://example.com", "action": "click", "selector": "button.submit"}


# ============================================================================
# MOCK CLIENT FIXTURES
# ============================================================================


@pytest_asyncio.fixture
async def mock_httpx_client():
    """Create mock httpx AsyncClient."""
    client = AsyncMock()
    return client


@pytest_asyncio.fixture
async def mock_browser_page():
    """Create mock Playwright Page."""
    page = AsyncMock()
    page.url = "https://example.com"
    page.title = AsyncMock(return_value="Test Page")
    page.content = AsyncMock(return_value="<html><body>Test</body></html>")
    page.goto = AsyncMock()
    page.fill = AsyncMock()
    page.click = AsyncMock()
    page.screenshot = AsyncMock()
    page.wait_for_load_state = AsyncMock()
    page.close = AsyncMock()
    return page


@pytest_asyncio.fixture
async def mock_browser():
    """Create mock Playwright Browser."""
    browser = AsyncMock()
    page = AsyncMock()
    page.url = "https://example.com"
    page.title = AsyncMock(return_value="Test Page")
    page.content = AsyncMock(return_value="<html></html>")
    page.goto = AsyncMock()
    page.close = AsyncMock()

    browser.new_page = AsyncMock(return_value=page)
    browser.close = AsyncMock()
    return browser


# ============================================================================
# TEST DATA GENERATORS
# ============================================================================


@pytest.fixture
def test_prompts():
    """Collection of test prompts."""
    return {
        "simple": "What is 2+2?",
        "code": "Write a Python function to reverse a string",
        "longform": "Explain the concept of machine learning in detail, covering supervised and unsupervised learning, and provide examples of real-world applications.",
        "special_chars": "How do you escape special chars in Python? (e.g., \\n, \\t)",
        "empty": "",
    }


@pytest.fixture
def test_urls():
    """Collection of test URLs."""
    return {
        "valid_https": "https://api.example.com/data",
        "valid_http": "http://example.com",
        "with_port": "https://localhost.example.com:8443",
        "with_path": "https://example.com/api/v1/users",
        "with_query": "https://example.com/search?q=test&lang=en",
    }


@pytest.fixture
def test_model_names():
    """Collection of test model names."""
    return {
        "simple": "llama2",
        "with_version": "qwen3-coder:30b",
        "with_namespace": "meta-llama/Llama-2-7b-chat",
        "with_underscores": "my_custom_model_v1",
        "with_dots": "model.v1.2.3",
    }


@pytest.fixture
def test_paths():
    """Collection of test file paths."""
    return {
        "simple": "models/model.bin",
        "nested": "data/training/dataset/train.json",
        "with_extension": "output/results.tar.gz",
        "relative": "./local_model",
        "absolute": "/opt/models/model.bin",
    }


# ============================================================================
# ASYNC UTILITIES
# ============================================================================


@pytest.fixture
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ============================================================================
# CONTEXT MANAGERS FOR TESTING
# ============================================================================


@pytest.fixture
def mock_ollama_environment(monkeypatch):
    """Mock Ollama environment variables."""
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://localhost:11434")
    monkeypatch.setenv("OLLAMA_MODEL", "qwen3-coder:30b")
    monkeypatch.setenv("OLLAMA_VISION_MODEL", "llava:13b")


@pytest.fixture
def mock_browser_environment(monkeypatch, tmp_path):
    """Mock browser environment."""
    screenshots_dir = tmp_path / "screenshots"
    screenshots_dir.mkdir()
    monkeypatch.setenv("BROWSER_HEADLESS", "true")
    monkeypatch.setenv("SCREENSHOTS_DIR", str(screenshots_dir))
    return screenshots_dir


# ============================================================================
# PERFORMANCE TESTING UTILITIES
# ============================================================================


@pytest.fixture
def timing_context():
    """Context manager for timing operations."""

    class TimingContext:
        def __init__(self):
            self.start_time = None
            self.end_time = None

        def __enter__(self):
            import time

            self.start_time = time.time()
            return self

        def __exit__(self, *args):
            import time

            self.end_time = time.time()

        @property
        def elapsed(self):
            if self.start_time and self.end_time:
                return self.end_time - self.start_time
            return None

    return TimingContext()


@pytest.fixture
def performance_threshold():
    """Performance thresholds for testing."""
    return {
        "ollama_generate": 2.0,  # seconds
        "ollama_chat": 2.0,
        "browser_navigate": 5.0,
        "browser_extract": 3.0,
        "page_load": 10.0,
    }


# ============================================================================
# ASSERTION HELPERS
# ============================================================================


@pytest.fixture
def assert_valid_response():
    """Helper to assert valid response structure."""

    def _assert(response: dict[str, Any], expected_keys: list = None):
        assert isinstance(response, dict)
        if expected_keys:
            for key in expected_keys:
                assert key in response, f"Missing key: {key}"

    return _assert


@pytest.fixture
def assert_valid_task_result():
    """Helper to assert valid task result."""

    def _assert(result: dict[str, Any]):
        required_keys = ["task_id", "status", "result"]
        for key in required_keys:
            assert key in result, f"Missing key: {key}"
        assert result["status"] in ["PENDING", "RUNNING", "COMPLETED", "FAILED"]

    return _assert


@pytest.fixture
def assert_screenshot_valid():
    """Helper to assert screenshot validity."""

    def _assert(screenshot_path: str):
        path = Path(screenshot_path)
        assert path.exists(), f"Screenshot not found: {screenshot_path}"
        assert path.suffix in [".png", ".jpg", ".jpeg"], f"Invalid image format: {path.suffix}"
        assert path.stat().st_size > 0, "Screenshot is empty"

    return _assert
