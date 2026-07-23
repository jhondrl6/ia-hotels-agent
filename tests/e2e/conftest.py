"""E2E test configuration - mocks external dependencies to allow handler imports."""
import sys
import types
from pathlib import Path

# Add project root to Python path (inherits from tests/conftest.py via pytest)
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def _ensure_module(name: str, is_package: bool = False, **attrs):
    """Create a mock module in sys.modules if it doesn't exist."""
    if name in sys.modules:
        return sys.modules[name]
    mod = types.ModuleType(name)
    if is_package:
        mod.__path__ = []
    for k, v in attrs.items():
        setattr(mod, k, v)
    sys.modules[name] = mod
    return mod


def _setup_dependency_mocks():
    """Mock external dependencies (bs4, selenium, urllib3) so the handler can be imported."""

    # --- bs4 ---
    if 'bs4' not in sys.modules:
        bs4 = types.ModuleType('bs4')
        bs4.BeautifulSoup = type('BeautifulSoup', (), {})
        sys.modules['bs4'] = bs4

    # --- selenium (full mock tree) ---
    _ensure_module('selenium', is_package=True)
    _ensure_module('selenium.webdriver', is_package=True)

    for sub in ['remote', 'chrome', 'common', 'support', 'firefox', 'edge', 'safari']:
        _ensure_module(f'selenium.webdriver.{sub}', is_package=True)

    # selenium.webdriver.remote sub-modules
    for sub in ['remote', 'webdriver', 'webelement', 'command', 'switch_to', 'errorhandler']:
        _ensure_module(f'selenium.webdriver.remote.{sub}')

    # Add commonly imported names to remote.webdriver
    wd_mod = sys.modules.get('selenium.webdriver.remote.webdriver')
    if wd_mod:
        wd_mod.WebDriver = type('WebDriver', (), {})

    # selenium.webdriver.chrome sub-modules
    _ensure_module('selenium.webdriver.chrome.options',
                   Options=type('Options', (), {'add_argument': lambda *a: None}))
    _ensure_module('selenium.webdriver.chrome.service',
                   Service=type('Service', (), {}))

    # selenium.webdriver.common sub-modules
    _ensure_module('selenium.webdriver.common.by',
                   By=type('By', (), {'CSS_SELECTOR': 'css', 'XPATH': 'xpath', 'CLASS_NAME': 'class'}))
    _ensure_module('selenium.webdriver.common.keys',
                   Keys=type('Keys', (), {'RETURN': '\n', 'ENTER': '\n'}))
    _ensure_module('selenium.webdriver.common.action_chains',
                   ActionChains=type('ActionChains', (), {}))

    # selenium.webdriver.support sub-modules
    _ensure_module('selenium.webdriver.support.ui',
                   WebDriverWait=type('WebDriverWait', (), {}))
    _ensure_module('selenium.webdriver.support.expected_conditions')

    # selenium.common
    _ensure_module('selenium.common', is_package=True)
    Exc = type('TimeoutException', (Exception,), {})
    _ensure_module('selenium.common.exceptions',
                   TimeoutException=Exc,
                   NoSuchElementException=type('NoSuchElementException', (Exception,), {}),
                   WebDriverException=type('WebDriverException', (Exception,), {}),
                   StaleElementReferenceException=type('StaleElementReferenceException', (Exception,), {}),
                   InvalidArgumentException=type('InvalidArgumentException', (Exception,), {}),
                   )

    # --- urllib3 (ensure sub-packages exist) ---
    try:
        import urllib3  # noqa: F401
    except ImportError:
        _ensure_module('urllib3', is_package=True)

    try:
        import urllib3.exceptions  # noqa: F401
    except ImportError:
        _ensure_module('urllib3.exceptions',
                       HTTPError=type('HTTPError', (Exception,), {}),
                       )


_setup_dependency_mocks()
