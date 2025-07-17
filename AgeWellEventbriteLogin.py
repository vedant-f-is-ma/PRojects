from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

# Set up the driver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# Go to an Eventbrite event page (replace with actual event URL)
driver.get('https://www.eventbrite.com/e/22nd-annual-healthy-living-festival-free-senior-festival-w-lunch-at-zoo-tickets-1388575319159')

time.sleep(3)  # Wait for the page to load

# Find the "Get Tickets" button and click it
# You may need to adjust this selector based on the actual page HTML
get_tickets_button = driver.find_element(By.ID, "eventbrite-widget-modal-trigger-1388575319159-9qbe7")
get_tickets_button.click()

# Wait to see the result
time.sleep(5)

# Close the browser
driver.quit()
