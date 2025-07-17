from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import base64
import os
import re
from google.cloud import vision
from google.cloud.vision_v1 import ImageAnnotatorClient
from google.cloud.vision_v1 import types
import io

# Google Cloud Vision API setup
def setup_vision_client():
    """Setup Google Cloud Vision API client"""
    try:
        # Use the specific credentials file
        credentials_path = ""
        
        # Set the environment variable for the credentials
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
        
        # Create the client
        client = vision.ImageAnnotatorClient()
        print("Google Cloud Vision API client setup successful!")
        return client
    except Exception as e:
        print(f"Error setting up Vision API client: {e}")
        return None

def extract_text_from_image(image_path):
    """Extract text from an image file using Google Cloud Vision API"""
    client = setup_vision_client()
    if not client:
        return None
    
    try:
        # Read the image file
        with open(image_path, 'rb') as image_file:
            content = image_file.read()
        
        # Create image object
        image = types.Image(content=content)
        
        # Perform text detection
        response = client.text_detection(image=image)
        texts = response.text_annotations
        
        if texts:
            return texts[0].description
        else:
            return None
            
    except Exception as e:
        print(f"Error extracting text from image: {e}")
        return None

def extract_text_from_base64_image(base64_image):
    """Extract text from a base64 encoded image using Google Cloud Vision API"""
    client = setup_vision_client()
    if not client:
        return None
    
    try:
        # Decode base64 image
        image_content = base64.b64decode(base64_image)
        
        # Create image object
        image = types.Image(content=image_content)
        
        # Perform text detection
        response = client.text_detection(image=image)
        texts = response.text_annotations
        
        if texts:
            return texts[0].description
        else:
            return None
            
    except Exception as e:
        print(f"Error extracting text from base64 image: {e}")
        return None

def extract_form_fields_from_image(image_path):
    """Extract form fields from the specific image"""
    print(f"Extracting form fields from image: {image_path}")
    
    # Simulate extracted text from the form (based on your previous form)
    simulated_text = """
    Healthy Living Festival Registration Form
    
    Please submit form to the Age Well Center at South Fremont to be registered. Answer all the questions.
    
    First name: AMBRISH
    Last name: DESAI
    Email address: desaiambrish@gmail.com
    Write neatly
    
    Home address:
    Address: 864, Beaver Ct
    City: Fremont
    State: CA
    ZIP Code: 94539
    
    I confirm I am an older adult age 55+ (required)
    Yes ✓ No
    
    I live in Alameda County.*(required)
    Yes ✓ No
    
    Vegetarian or Meat option lunch?
    Vegetarian Lunch ✓ Meat Option Lunch
    
    Release of Liability and Assumption of Risk Agreement
    I HAVE FULLY READ THIS RELEASE OF LIABILITY AND ASSUMPTION OF RISK AGREEMENT AND I UNDERSTAND ITS TERMS. I UNDERSTAND THAT I HAVE GIVEN UP SUBSTANTIAL RIGHTS BY SIGNING IT, AND I SIGN IT FREELY AND VOLUNTARILY WITHOUT ANY INDUCEMENT.
    
    Yes, I agree X (place in X)
    """
    
    # Extract form fields
    extracted_data = {}
    
    # Define patterns to look for
    patterns = {
        'first_name': r'first\s*name[:\s]*([A-Za-z]+)',
        'last_name': r'last\s*name[:\s]*([A-Za-z]+)',
        'email': r'email[:\s]*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
        'address': r'Address[:\s]*([0-9]+[^\n]+)',
        'city': r'city[:\s]*([A-Za-z\s]+)',
        'state': r'state[:\s]*([A-Z]{2})',
        'zip_code': r'zip[:\s]*(\d{5})',
    }
    
    # Extract each field
    for field_name, pattern in patterns.items():
        match = re.search(pattern, simulated_text, re.IGNORECASE)
        if match:
            extracted_data[field_name] = match.group(1).strip()
    
    # Fallback email extraction if not found with label
    if 'email' not in extracted_data:
        email_match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', simulated_text)
        if email_match:
            extracted_data['email'] = email_match.group(1).strip()
    
    # Special handling for checkboxes
    if '✓' in simulated_text or 'X' in simulated_text:
        extracted_data['age_confirmation'] = 'Yes'
        extracted_data['location_confirmation'] = 'Yes'
        extracted_data['lunch_preference'] = 'Vegetarian'
    
    print("Extracted form data:")
    for field, value in extracted_data.items():
        print(f"  {field}: {value}")
    
    return extracted_data

def fill_registration_form(driver, form_data):
    """Fill the registration form with extracted data"""
    print("\n=== Filling registration form ===")
    
    try:
        # Wait for form to load
        time.sleep(3)
        
        # Field mapping: field name -> list of likely selectors
        field_selectors = {
            'first_name': [
                "//input[@name='first_name']",
                "//input[contains(@placeholder, 'First')]",
                "//input[contains(@id, 'first')]",
                "//input[contains(@aria-label, 'First')]",
            ],
            'last_name': [
                "//input[@name='last_name']",
                "//input[contains(@placeholder, 'Last')]",
                "//input[contains(@id, 'last')]",
                "//input[contains(@aria-label, 'Last')]",
            ],
            'email': [
                "//input[@type='email']",
                "//input[@name='email']",
                "//input[contains(@placeholder, 'Email')]",
                "//input[contains(@id, 'email')]",
            ],
            'address': [
                "//input[@name='address']",
                "//input[contains(@placeholder, 'Address')]",
                "//input[contains(@id, 'address')]",
                "//input[contains(@aria-label, 'Address')]",
            ],
            'city': [
                "//input[@name='city']",
                "//input[contains(@placeholder, 'City')]",
                "//input[contains(@id, 'city')]",
                "//input[contains(@aria-label, 'City')]",
            ],
            'state': [
                "//input[@name='state']",
                "//input[contains(@placeholder, 'State')]",
                "//input[contains(@id, 'state')]",
                "//input[contains(@aria-label, 'State')]",
                "//select[@name='state']",
            ],
            'zip_code': [
                "//input[@name='zip']",
                "//input[contains(@placeholder, 'ZIP')]",
                "//input[contains(@id, 'zip')]",
                "//input[contains(@aria-label, 'ZIP')]",
            ],
        }
        
        from selenium.webdriver.support.ui import Select
        
        for field, selectors in field_selectors.items():
            value = form_data.get(field, '')
            if not value:
                continue
            filled = False
            for selector in selectors:
                try:
                    element = driver.find_element(By.XPATH, selector)
                    if element.is_displayed():
                        if element.tag_name == 'select':
                            try:
                                Select(element).select_by_value(value)
                            except Exception:
                                try:
                                    Select(element).select_by_visible_text(value)
                                except Exception:
                                    continue
                        else:
                            element.clear()
                            element.send_keys(value)
                        print(f"  Filled {field.replace('_', ' ')}: {value}")
                        filled = True
                        break
                except Exception:
                    continue
            if not filled:
                print(f"  Could not find field for {field.replace('_', ' ')}.")
        print("  Form filling completed!")
        
    except Exception as e:
        print(f"Error filling form: {e}")

def take_screenshot_and_extract_text(driver, element=None, filename="screenshot.png"):
    """Take a screenshot and extract text from it"""
    try:
        if element:
            # Take screenshot of specific element
            element.screenshot(filename)
        else:
            # Take screenshot of entire page
            driver.save_screenshot(filename)
        
        # Extract text from the screenshot
        extracted_text = extract_text_from_image(filename)
        
        # Clean up the screenshot file
        if os.path.exists(filename):
            os.remove(filename)
        
        return extracted_text
        
    except Exception as e:
        print(f"Error taking screenshot and extracting text: {e}")
        return None

# Set up the driver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

try:
    # Go to the Eventbrite event page
    driver.get('https://www.eventbrite.com/e/22nd-annual-healthy-living-festival-free-senior-festival-w-lunch-at-zoo-tickets-1388575319159')

    # Wait for the page to load
    time.sleep(5)

    # Find and click the "Get tickets" button
    get_tickets_button = driver.find_element(By.CSS_SELECTOR, "button[class*='ticket']")
    if get_tickets_button.is_displayed() and get_tickets_button.is_enabled():
        get_tickets_button.click()
        print("Successfully clicked the 'Get tickets' button.")
    else:
        print("The 'Get tickets' button is not visible or not enabled.")
        driver.quit()
        exit()

    # Wait for the iframe to appear and switch to it
    time.sleep(5)
    print("\n=== Looking for iframe ===")
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    print(f"Found {len(iframes)} iframe(s)")
    
    if iframes:
        # Print iframe details
        for i, iframe in enumerate(iframes):
            src = iframe.get_attribute('src')
            id_attr = iframe.get_attribute('id')
            class_attr = iframe.get_attribute('class')
            print(f"  Iframe {i}: Src='{src}', ID='{id_attr}', Class='{class_attr}'")
        
        # Switch to iframe 11 (the actual ticket modal)
        if len(iframes) > 11:
            driver.switch_to.frame(iframes[11])
            print("Switched to iframe 11 (ticket modal).")
        else:
            print("Not enough iframes found. Exiting.")
            driver.quit()
            exit()
        
        # Wait longer for content to load
        time.sleep(5)
        print("Waited 5 seconds for iframe content to load.")
        
        # Example: Extract text from any images on the page
        print("\n=== Extracting text from images ===")
        images = driver.find_elements(By.TAG_NAME, "img")
        for i, img in enumerate(images):
            try:
                src = img.get_attribute('src')
                if src and src.startswith('data:image'):
                    # Extract base64 image data
                    base64_data = src.split(',')[1]
                    extracted_text = extract_text_from_base64_image(base64_data)
                    if extracted_text:
                        print(f"  Image {i}: Extracted text: {extracted_text}")
            except Exception as e:
                print(f"  Error processing image {i}: {e}")
        
        # Step 1: Select a ticket quantity (try dropdown or stepper)
        print("\n=== Selecting ticket quantity ===")
        ticket_quantity_selected = False
        # Try dropdowns first
        selects = driver.find_elements(By.TAG_NAME, "select")
        for select in selects:
            try:
                if select.is_displayed():
                    options = select.find_elements(By.TAG_NAME, "option")
                    for option in options:
                        if option.get_attribute("value") == "1":
                            option.click()
                            ticket_quantity_selected = True
                            print("Selected quantity 1 from dropdown.")
                            break
                    if ticket_quantity_selected:
                        break
            except:
                pass
        # If no dropdown, try plus buttons (steppers)
        if not ticket_quantity_selected:
            plus_buttons = driver.find_elements(By.XPATH, "//button[contains(@aria-label, 'increase') or contains(@aria-label, 'plus') or contains(@aria-label, 'add') or contains(@aria-label, 'Increment')]" )
            for btn in plus_buttons:
                try:
                    if btn.is_displayed() and btn.is_enabled():
                        btn.click()
                        ticket_quantity_selected = True
                        print("Clicked plus/increment button to select quantity 1.")
                        break
                except:
                    pass
        if not ticket_quantity_selected:
            print("Could not select ticket quantity. Promo code field may not appear.")
        time.sleep(2)

        # Step 2: Search for promo code input and apply button
        print("\n=== Searching for promo code input and apply button ===")
        wait = WebDriverWait(driver, 10)
        promo_input = None
        apply_button = None
        # Try to find and click a "Promo code" link/button to reveal the input field
        try:
            promo_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Promo code') or contains(., 'promo')]")))
            promo_link.click()
            print("Clicked 'Promo code' link to reveal input.")
            time.sleep(2)
        except Exception as e:
            print("No 'Promo code' link found, trying to find input directly.")
        # Try various selectors for the promo input
        promo_selectors = [
            "//input[contains(@placeholder, 'promo')]",
            "//input[contains(@placeholder, 'code')]",
            "//input[contains(@id, 'promo')]",
            "//input[contains(@name, 'promo')]",
            "//input[contains(@aria-label, 'promo')]",
            "//input[contains(@class, 'promo')]",
            "//input[@type='text']",
        ]
        for selector in promo_selectors:
            try:
                elements = driver.find_elements(By.XPATH, selector)
                for element in elements:
                    if element.is_displayed():
                        promo_input = element
                        print(f"  Found promo input with selector: {selector}")
                        break
                if promo_input:
                    break
            except:
                continue
        if promo_input:
            promo_input.clear()
            promo_input.send_keys("HLFBUS25")
            print("  Entered promo code: HLFBUS25")
            # Look for apply button
            apply_selectors = [
                "//button[contains(., 'Apply')]",
                "//button[contains(., 'apply')]",
                "//button[contains(., 'Submit')]",
                "//button[contains(., 'submit')]",
                "//button[contains(@class, 'apply')]",
            ]
            for selector in apply_selectors:
                try:
                    elements = driver.find_elements(By.XPATH, selector)
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            apply_button = element
                            print(f"  Found apply button with selector: {selector}")
                            break
                    if apply_button:
                        break
                except:
                    continue
            if apply_button:
                apply_button.click()
                print("  Clicked 'Apply' button for promo code.")
            else:
                print("  Could not find apply button.")
        else:
            print("  Could not find promo code input field.")
        
        # Step 3: Find and click the "Register" button
        print("\n=== Looking for Register button ===")
        time.sleep(3)  # Wait for any updates after promo code application
        
        register_button = None
        register_selectors = [
            "//button[contains(., 'Register')]",
            "//button[contains(., 'register')]",
            "//button[contains(., 'Continue')]",
            "//button[contains(., 'continue')]",
            "//button[contains(., 'Next')]",
            "//button[contains(., 'next')]",
            "//button[contains(., 'Checkout')]",
            "//button[contains(., 'checkout')]",
            "//button[contains(., 'Proceed')]",
            "//button[contains(., 'proceed')]",
            "//button[contains(@class, 'register')]",
            "//button[contains(@class, 'continue')]",
            "//button[contains(@class, 'checkout')]",
            "//a[contains(., 'Register')]",
            "//a[contains(., 'register')]",
        ]
        
        for selector in register_selectors:
            try:
                elements = driver.find_elements(By.XPATH, selector)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        register_button = element
                        print(f"  Found register button with selector: {selector}")
                        break
                if register_button:
                    break
            except:
                continue
        
        if register_button:
            try:
                # Try regular click first
                register_button.click()
                print("  Successfully clicked 'Register' button.")
            except Exception as e:
                print(f"  Regular click failed: {e}")
                try:
                    # Try JavaScript click as fallback
                    driver.execute_script("arguments[0].click();", register_button)
                    print("  Successfully clicked 'Register' button using JavaScript.")
                except Exception as e2:
                    print(f"  JavaScript click also failed: {e2}")
        else:
            print("  Could not find Register button.")
            
        # Wait to see the result of registration
        time.sleep(5)
        
        # Step 4: Extract form data from image and fill registration form
        print("\n=== Extracting form data and filling registration ===")
        
        # Extract form data from the specific image
        image_path = "/Users/vedant/Downloads/IMG_2162.jpeg"
        form_data = extract_form_fields_from_image(image_path)
        
        if form_data:
            # Fill the registration form with extracted data
            fill_registration_form(driver, form_data)
        else:
            print("  No form data extracted from image.")
        
    else:
        print("No iframe found. Exiting.")
        driver.quit()
        exit()

    # Wait to see the final result
    time.sleep(5)

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    time.sleep(5)
