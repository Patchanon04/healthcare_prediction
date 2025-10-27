"""
Pytest configuration for E2E tests.
"""
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions


@pytest.fixture(scope='session')
def browser_type(request):
    """Get browser type from command line option."""
    return request.config.getoption('--browser', default='chrome')


@pytest.fixture(scope='function')
def driver(browser_type):
    """Create WebDriver instance."""
    if browser_type == 'chrome':
        options = ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')
        driver = webdriver.Chrome(options=options)
    elif browser_type == 'firefox':
        options = FirefoxOptions()
        options.add_argument('--headless')
        driver = webdriver.Firefox(options=options)
    else:
        raise ValueError(f'Unsupported browser: {browser_type}')
    
    driver.implicitly_wait(10)
    yield driver
    driver.quit()


@pytest.fixture(scope='session')
def base_url():
    """Base URL for the application."""
    return 'http://localhost:8080'


@pytest.fixture(scope='function')
def authenticated_driver(driver, base_url):
    """Create authenticated WebDriver instance."""
    # Login
    driver.get(f'{base_url}/login')
    
    from selenium.webdriver.common.by import By
    username_input = driver.find_element(By.NAME, 'username')
    password_input = driver.find_element(By.NAME, 'password')
    
    username_input.send_keys('testuser')
    password_input.send_keys('testpass123')
    
    login_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
    login_button.click()
    
    # Wait for dashboard
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    WebDriverWait(driver, 10).until(
        EC.url_contains('/dashboard')
    )
    
    yield driver


def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        '--browser',
        action='store',
        default='chrome',
        help='Browser to use for testing: chrome or firefox'
    )
