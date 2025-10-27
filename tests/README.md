# Test Suite Documentation

This directory contains comprehensive tests for the Healthcare Prediction System.

## Test Structure

```
tests/
├── e2e/                    # End-to-end Selenium tests
│   ├── test_selenium_login.py
│   ├── test_selenium_patient.py
│   └── test_selenium_chat.py
├── conftest.py            # Pytest configuration
├── requirements.txt       # Test dependencies
└── README.md             # This file

backend/predictions/
├── tests.py              # Original prediction tests
├── test_patients.py      # Patient management tests
├── test_chat.py          # Chat/WebSocket tests
└── test_treatments.py    # Treatment management tests
```

## Test Categories

### 1. Unit Tests (Django)
Located in `backend/predictions/`:
- **test_patients.py**: Patient CRUD, search, diagnosis
- **test_chat.py**: Chat rooms, messages, WebSocket
- **test_treatments.py**: Treatment plans, medications, follow-ups
- **tests.py**: Original prediction/upload tests

### 2. E2E Tests (Selenium)
Located in `tests/e2e/`:
- **test_selenium_login.py**: Login/authentication flows
- **test_selenium_patient.py**: Patient management UI
- **test_selenium_chat.py**: Chat interface, notifications

## Setup

### 1. Install Test Dependencies

```bash
# Install Selenium and test tools
cd tests/
pip install -r requirements.txt

# Install ChromeDriver (for Chrome)
# macOS
brew install chromedriver

# Or use webdriver-manager (automatic)
pip install webdriver-manager
```

### 2. Install Backend Test Dependencies

```bash
cd backend/
pip install -r requirements.txt
```

## Running Tests

### Unit Tests (Django)

```bash
# Run all Django tests
cd backend/
python manage.py test

# Run specific test file
python manage.py test predictions.test_patients
python manage.py test predictions.test_chat
python manage.py test predictions.test_treatments

# Run with coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Generate HTML report
```

### E2E Tests (Selenium)

```bash
# Run all E2E tests
cd tests/
python -m pytest e2e/

# Run specific test file
python -m pytest e2e/test_selenium_login.py
python -m pytest e2e/test_selenium_patient.py
python -m pytest e2e/test_selenium_chat.py

# Run with verbose output
python -m pytest e2e/ -v

# Run with HTML report
python -m pytest e2e/ --html=report.html --self-contained-html

# Run in different browser
python -m pytest e2e/ --browser=firefox

# Run specific test
python -m pytest e2e/test_selenium_login.py::LoginTestCase::test_login_with_valid_credentials
```

### Using unittest (alternative)

```bash
# Run E2E tests with unittest
cd tests/e2e/
python test_selenium_login.py
python test_selenium_patient.py
python test_selenium_chat.py
```

## Test Configuration

### Environment Variables

Create `.env.test` file:

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/test_db

# Frontend URL
FRONTEND_URL=http://localhost:8080

# Test user credentials
TEST_USERNAME=testuser
TEST_PASSWORD=testpass123
```

### Browser Options

Edit `conftest.py` to customize browser settings:
- Headless mode (default: enabled)
- Window size
- Additional Chrome/Firefox options

## Writing New Tests

### Unit Test Example

```python
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

class MyFeatureTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Setup test data
    
    def test_my_feature(self):
        response = self.client.get('/api/v1/my-endpoint/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
```

### E2E Test Example

```python
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By

class MyE2ETestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.driver = webdriver.Chrome()
        cls.base_url = 'http://localhost:8080'
    
    def test_my_feature(self):
        self.driver.get(f'{self.base_url}/my-page')
        element = self.driver.find_element(By.ID, 'my-element')
        self.assertIsNotNone(element)
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      
      - name: Install dependencies
        run: |
          pip install -r backend/requirements.txt
          pip install -r tests/requirements.txt
      
      - name: Run Django tests
        run: |
          cd backend
          python manage.py test
      
      - name: Run E2E tests
        run: |
          cd tests
          pytest e2e/ --html=report.html
```

## Test Coverage Goals

- **Unit Tests**: > 80% code coverage
- **E2E Tests**: Cover critical user flows
- **API Tests**: All endpoints tested

## Best Practices

1. **Isolation**: Each test should be independent
2. **Cleanup**: Use setUp/tearDown properly
3. **Assertions**: Use descriptive assertion messages
4. **Data**: Use fixtures for test data
5. **Speed**: Keep tests fast (mock external services)
6. **Readability**: Clear test names and documentation

## Troubleshooting

### ChromeDriver Issues

```bash
# Update ChromeDriver
brew upgrade chromedriver

# Or use webdriver-manager
from webdriver_manager.chrome import ChromeDriverManager
driver = webdriver.Chrome(ChromeDriverManager().install())
```

### Timeout Issues

Increase wait times in tests:
```python
driver.implicitly_wait(20)  # Increase from 10 to 20 seconds
```

### Headless Mode Issues

Disable headless for debugging:
```python
options = ChromeOptions()
# options.add_argument('--headless')  # Comment out
```

## Resources

- [Django Testing Docs](https://docs.djangoproject.com/en/4.2/topics/testing/)
- [Selenium Documentation](https://www.selenium.dev/documentation/)
- [Pytest Documentation](https://docs.pytest.org/)
- [REST Framework Testing](https://www.django-rest-framework.org/api-guide/testing/)

## Contact

For questions about tests, contact the development team.
