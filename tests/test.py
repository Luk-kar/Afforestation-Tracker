import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import subprocess
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# https://blog.streamlit.io/testing-streamlit-apps-using-seleniumbase/


class TestStreamlitApp(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Start the Streamlit app
        cls.streamlit_process = subprocess.Popen(
            ["streamlit", "run", "app_test.py", "--server.headless", "true"]
        )
        # Allow some time for the app to start
        time.sleep(5)

        # Set up the Selenium WebDriver (assuming you have Chrome installed)
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        cls.driver = webdriver.Chrome(options=options)

        cls.driver.get("http://localhost:8501")

    @classmethod
    def tearDownClass(cls):
        # Close the browser and terminate the Streamlit app process
        cls.driver.quit()
        cls.streamlit_process.terminate()

    def test_button_click(self):
        # Interact with the button
        print("Testing button click")

        # print html content
        # print("START---------------------------------")
        # print(self.driver.page_source)
        # print("END-----------------------------------")

        wait = WebDriverWait(self.driver, 10)
        button = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "button[data-testid='baseButton-secondary']")
            )
        )

        button.click()
        print("Button clicked")

        # Wait for the content to update
        time.sleep(1)

        # Check the updated content
        updated_content = self.driver.find_elements(By.CLASS_NAME, "stMarkdown")[-1]
        self.assertIn("Button was clicked!", updated_content.text)

    def test_initial_state(self):
        """Verify that the initial content of the app is loaded as expected."""
        initial_content = self.driver.find_element(By.CLASS_NAME, "stMarkdown").text
        self.assertIn("This is a simple test application.", initial_content)

    def test_multiple_button_clicks(self):
        """Test that clicking the button multiple times updates the content accordingly."""
        button = self.driver.find_element(
            By.CSS_SELECTOR, "button[data-testid='baseButton-secondary']"
        )
        for _ in range(3):
            button.click()
            time.sleep(1)  # Wait a moment for the content to update

        # After multiple clicks, verify the content
        updated_content = self.driver.find_elements(By.CLASS_NAME, "stMarkdown")[
            -1
        ].text
        self.assertEqual(updated_content.count("Button was clicked!"), 3)

    def test_navigation(self):
        """Test navigation between different sections of the app, if applicable."""
        # Example: Navigate to a different page or section
        nav_button = self.driver.find_element(
            By.CSS_SELECTOR, "button[data-testid='navButton']"
        )
        nav_button.click()
        time.sleep(1)
        # Check that navigation has occurred
        page_title = self.driver.find_element(By.CSS_SELECTOR, "h1").text
        self.assertEqual(page_title, "New Page Title")

    def test_dynamic_content(self):
        """Test the generation of dynamic content based on user input."""
        input_field = self.driver.find_element(
            By.CSS_SELECTOR, "input[data-testid='inputField']"
        )
        input_field.send_keys("test input")
        submit_button = self.driver.find_element(
            By.CSS_SELECTOR, "button[data-testid='submitButton']"
        )
        submit_button.click()
        time.sleep(1)
        # Verify response to the input
        response = self.driver.find_element(By.CLASS_NAME, "stMarkdown").text
        self.assertIn("Expected output for 'test input'", response)


if __name__ == "__main__":
    unittest.main()
