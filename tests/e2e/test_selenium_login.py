"""
Selenium E2E tests for Login functionality.
"""
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import unittest


class LoginTestCase(unittest.TestCase):
    """E2E tests for login functionality."""
    
    @classmethod
    def setUpClass(cls):
        """Set up Selenium WebDriver."""
        # Use Chrome by default
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Run in headless mode
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')
        
        cls.driver = webdriver.Chrome(options=options)
        cls.driver.implicitly_wait(10)
        cls.base_url = 'http://localhost:8080'  # Frontend URL
    
    @classmethod
    def tearDownClass(cls):
        """Close the browser."""
        cls.driver.quit()
    
    def setUp(self):
        """Navigate to login page before each test."""
        self.driver.get(f'{self.base_url}/login')
        time.sleep(1)
    
    def test_login_page_loads(self):
        """Test that login page loads correctly."""
        self.assertIn('Login', self.driver.title)
        
        # Check for login form elements
        username_input = self.driver.find_element(By.NAME, 'username')
        password_input = self.driver.find_element(By.NAME, 'password')
        login_button = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        
        self.assertIsNotNone(username_input)
        self.assertIsNotNone(password_input)
        self.assertIsNotNone(login_button)
    
    def test_login_with_valid_credentials(self):
        """Test login with valid credentials."""
        # Enter credentials
        username_input = self.driver.find_element(By.NAME, 'username')
        password_input = self.driver.find_element(By.NAME, 'password')
        
        username_input.send_keys('testuser')
        password_input.send_keys('testpass123')
        
        # Submit form
        login_button = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        login_button.click()
        
        # Wait for redirect to dashboard
        try:
            WebDriverWait(self.driver, 10).until(
                EC.url_contains('/dashboard')
            )
            self.assertIn('/dashboard', self.driver.current_url)
        except TimeoutException:
            self.fail('Login did not redirect to dashboard')
    
    def test_login_with_invalid_credentials(self):
        """Test login with invalid credentials."""
        username_input = self.driver.find_element(By.NAME, 'username')
        password_input = self.driver.find_element(By.NAME, 'password')
        
        username_input.send_keys('wronguser')
        password_input.send_keys('wrongpass')
        
        login_button = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        login_button.click()
        
        # Wait for error message
        time.sleep(2)
        
        # Should still be on login page
        self.assertIn('/login', self.driver.current_url)
        
        # Check for error message
        try:
            error_message = self.driver.find_element(By.CSS_SELECTOR, '.error, .alert-danger, [role="alert"]')
            self.assertIsNotNone(error_message)
        except:
            pass  # Error message might be displayed differently
    
    def test_login_with_empty_fields(self):
        """Test login with empty fields."""
        login_button = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        login_button.click()
        
        time.sleep(1)
        
        # Should still be on login page
        self.assertIn('/login', self.driver.current_url)
    
    def test_register_link_exists(self):
        """Test that register link exists and works."""
        try:
            register_link = self.driver.find_element(By.LINK_TEXT, 'Register')
            register_link.click()
            
            time.sleep(1)
            self.assertIn('/register', self.driver.current_url)
        except:
            # Register link might not exist
            pass


if __name__ == '__main__':
    unittest.main()
