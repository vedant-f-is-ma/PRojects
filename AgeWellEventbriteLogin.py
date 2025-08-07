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
import google.generativeai as genai
import io

# ============================================================================
# CONFIGURATION VARIABLES - MODIFY THESE AS NEEDED
# ============================================================================

# Eventbrite Configuration
EVENTBRITE_URL = 'https://www.eventbrite.com/e/22nd-annual-healthy-living-festival-free-senior-festival-w-lunch-at-zoo-tickets-1388575319159'
PROMO_CODE = "HLFBUS25"

# Image Configuration
IMAGE_PATH = "/Users/vedant/Downloads/IMG_2166.jpeg"

# Form Data Configuration
COUNTRY = "United States"

# Site Coordinator Information (for HLF bus confirmation)
SITE_LOCATION = "City of Fremont, Age Well Center At South Fremont"
SITE_COORDINATOR_NAME = "Martha Torrez"
SITE_COORDINATOR_EMAIL = "mtorrez@fremont.gov"
SITE_COORDINATOR_PHONE = ""

# Checkbox Confirmations (set to True to check, False to leave unchecked)
CHECK_AGE_CONFIRMATION = True          # 55+ age confirmation
CHECK_LOCATION_CONFIRMATION = True     # Alameda County confirmation
CHECK_HLF_BUS = True                   # HLF Provided Bus option
CHECK_COORDINATOR_CONFIRMATION = True  # Site coordinator confirmation

# HLF Bus Configuration
HLF_BUS_OPTION = True                  # Set to True to select HLF bus option, False to skip

# Site Coordinator Bus Confirmation
SITE_COORDINATOR_BUS_CONFIRMATION = True  # Set to True to select "Yes" for site coordinator bus confirmation, False to skip

# Wait Times (in seconds)
PAGE_LOAD_WAIT = 0.5 #55351
IFRAME_WAIT = 1
FORM_FILL_WAIT = 0.5
FINAL_WAIT = 5
FIELD_FILL_RATE_LIMIT = 0.2  # Reduced from 5 to 1 second

# ============================================================================

# Gemini API setup
def setup_gemini():
    """Setup Gemini 1.5 Flash API"""
    try:
        # Put your API key here
        API_KEY = ""
        
        # Configure Gemini API
        genai.configure(api_key=API_KEY)
        
        # Use Gemini 1.5 Flash model
        model = genai.GenerativeModel('gemini-1.5-flash')
        print("Gemini 1.5 Flash API client setup successful!")
        return model
    except Exception as e:
        print(f"Error setting up Gemini API client: {e}")
        return None

def extract_text_from_image(image_path):
    """Extract text from an image file using Gemini 1.5 Flash API"""
    model = setup_gemini()
    if not model:
        return None
    
    try:
        # Read the image file
        with open(image_path, 'rb') as image_file:
            image_data = image_file.read()
        
        # Process image with comprehensive prompt
        prompt = """
        Extract all form fields from this image and return in this exact format:
        First Name: [value]
        Last Name: [value] 
        Email: [value]
        Address: [value]
        City: [value]
        State: [value]
        ZIP Code: [value]
        Age Confirmation: [Yes/No]
        Location Confirmation: [Yes/No]
        Lunch Preference: [Vegetarian/Meat]
        Liability Agreement: [Yes/No]
        
        If any field is not found, use 'None' as the value. For the lunch preference, if the check is on the top it is vegetarian and if on bottom is meat.
        """
        
        response = model.generate_content([prompt, {"mime_type": "image/jpeg", "data": image_data}])
        
        if response and response.text:
            return response.text.strip()
        else:
            return None
            
    except Exception as e:
        print(f"Error extracting text from image: {e}")
        return None

def extract_text_from_base64_image(base64_image):
    """Extract text from a base64 encoded image using Gemini 1.5 Flash API"""
    model = setup_gemini()
    if not model:
        return None
    
    try:
        # Decode base64 image
        image_content = base64.b64decode(base64_image)
        
        # Process image with comprehensive prompt
        prompt = """
        Extract all form fields from this image and return in this exact format:
        First Name: [value]
        Last Name: [value] 
        Email: [value]
        Address: [value]
        City: [value]
        State: [value]
        ZIP Code: [value]
        Age Confirmation: [Yes/No]
        Location Confirmation: [Yes/No]
        Lunch Preference: [Vegetarian/Meat]
        Liability Agreement: [Yes/No]
        
        If any field is not found, use 'None' as the value.
        """
        
        response = model.generate_content([prompt, {"mime_type": "image/jpeg", "data": image_content}])
        
        if response and response.text:
            return response.text.strip()
        else:
            return None
            
    except Exception as e:
        print(f"Error extracting text from base64 image: {e}")
        return None

def read_image_info(image_path):
    """Read image information (simulated for demo)"""
    print(f"Reading image: {image_path}")
    
    # Check if file exists
    if not os.path.exists(image_path):
        print(f"Error: File '{image_path}' does not exist.")
        return None
    
    # Get file information
    file_size = os.path.getsize(image_path)
    file_stats = os.stat(image_path)
    
    print(f"File exists: ✅")
    print(f"File size: {file_size} bytes")
    print(f"File type: JPEG image")
    
    # Extract text from the actual image using Gemini API
    extracted_text = extract_text_from_image(image_path)
    
    if extracted_text:
        print("Successfully extracted text from image using Gemini API")
        return extracted_text
    else:
        print("Failed to extract text from image.")
        return None

def extract_form_fields(text):
    """Extract form fields from Gemini API response"""
    extracted_data = {}
    confidence_scores = {}
    
    # Parse the structured response from Gemini
    lines = text.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if ':' in line:
            field, value = line.split(':', 1)
            field = field.strip().lower().replace(' ', '_')
            value = value.strip()
            
            # Map field names
            if field == 'first_name':
                extracted_data['first_name'] = value
                confidence_scores['first_name'] = 0.95
            elif field == 'last_name':
                extracted_data['last_name'] = value
                confidence_scores['last_name'] = 0.95
            elif field == 'email':
                extracted_data['email'] = value
                confidence_scores['email'] = 0.95
                # Add confirm_email using the same email
                extracted_data['confirm_email'] = value
                confidence_scores['confirm_email'] = 0.98
            elif field == 'address':
                extracted_data['address'] = value
                confidence_scores['address'] = 0.90
            elif field == 'city':
                extracted_data['city'] = value
                confidence_scores['city'] = 0.90
            elif field == 'state':
                extracted_data['state'] = value
                confidence_scores['state'] = 0.92
            elif field == 'zip_code':
                extracted_data['zip_code'] = value
                confidence_scores['zip_code'] = 0.96
            elif field == 'age_confirmation':
                extracted_data['age_confirmation'] = value
                confidence_scores['age_confirmation'] = 0.88
            elif field == 'location_confirmation':
                extracted_data['location_confirmation'] = value
                confidence_scores['location_confirmation'] = 0.88
            elif field == 'lunch_preference':
                extracted_data['lunch_preference'] = value
                confidence_scores['lunch_preference'] = 0.85
            elif field == 'liability_agreement':
                extracted_data['liability_agreement'] = value
                confidence_scores['liability_agreement'] = 0.90
    
    return extracted_data, confidence_scores

def extract_form_fields_from_image(image_path):
    """Extract form fields from the specific image using enhanced processing"""
    print(f"Extracting form fields from image: {image_path}")
    
    # Read image information using the enhanced function
    extracted_text = read_image_info(image_path)
    
    if not extracted_text:
        print("Could not read image information.")
        return {}
    
    print("\n" + "=" * 50)
    print("EXTRACTED TEXT FROM IMAGE:")
    print("=" * 50)
    print(extracted_text)
    print("=" * 50)
    
    # Extract form fields with confidence using the enhanced function
    print("\nExtracting form fields...")
    form_fields, confidence_scores = extract_form_fields(extracted_text)
    
    if form_fields:
        print("\n" + "=" * 50)
        print("EXTRACTED FORM FIELDS:")
        print("=" * 50)
        
        for field, value in form_fields.items():
            confidence = confidence_scores.get(field, 0.0)
            print(f"{field.replace('_', ' ').title()}: {value}")
            print(f"  Confidence: {confidence:.2f}")
            print()
        
        print("=" * 50)
        
        # Calculate average confidence
        if confidence_scores:
            avg_confidence = sum(confidence_scores.values()) / len(confidence_scores)
            print(f"\n📊 Average confidence: {avg_confidence:.2f}")
        
        print(f"\n✅ Successfully extracted {len(form_fields)} fields!")
        
        return form_fields
    else:
        print("No form fields could be extracted.")
        return {}

def fill_registration_form(driver, form_data):
    """Fill the registration form with extracted data"""
    print("\n=== Filling registration form ===")
    
    try:
        # Wait for form to load
        time.sleep(3)
        
        # Optimized field mapping with minimal selectors
        field_mapping = {
            'first_name': "//input[contains(@name, 'first') or contains(@placeholder, 'First')]",
            'last_name': "//input[contains(@name, 'last') or contains(@placeholder, 'Last')]",
            'email': "//input[@type='email']",
            'confirm_email': "//input[@type='email' and contains(@name, 'confirm')]",
            'address': "//input[contains(@name, 'address') or contains(@placeholder, 'Address')]",
            'city': "//input[contains(@name, 'city') or contains(@placeholder, 'City')]",
            'state': "//select[contains(@name, 'state') or contains(@name, 'region')]",
            'zip_code': "//input[contains(@name, 'postal')]",
        }
        
        # Ordered field mapping: field name -> list of likely selectors
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
            'confirm_email': [
                "//input[@type='email' and contains(@name, 'confirm')]",
                "//input[@type='email' and contains(@id, 'confirm')]",
                "//input[@type='email' and contains(@aria-label, 'confirm')]",
                "//input[@type='email' and contains(@placeholder, 'confirm')]",
                "//input[@type='email' and contains(@name, 'verify')]",
                "//input[@type='email' and contains(@id, 'verify')]",
                "//input[@type='email' and contains(@aria-label, 'verify')]",
                "//input[@type='email' and contains(@placeholder, 'verify')]",
                "//input[@type='email' and contains(@name, 'repeat')]",
                "//input[@type='email' and contains(@id, 'repeat')]",
                "//input[@type='email' and contains(@aria-label, 'repeat')]",
                "//input[@type='email' and contains(@placeholder, 'repeat')]",
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
                "//input[contains(@placeholder, 'ZIP Code')]",
                "//input[contains(@id, 'zip_code')]",
                "//input[contains(@aria-label, 'ZIP Code')]",
                "//input[contains(@name, 'zip_code')]",
                "//input[contains(@name, 'postal')]",
                "//input[contains(@id, 'postal')]",
                "//input[contains(@aria-label, 'postal')]",
            ],
            'site_location': [
                "//input[@name='site']",
                "//input[contains(@placeholder, 'site')]",
                "//input[contains(@id, 'site')]",
                "//input[contains(@aria-label, 'site')]",
                "//input[contains(@placeholder, 'location')]",
                "//input[contains(@id, 'location')]",
                "//input[contains(@aria-label, 'location')]",
                "//input[contains(@name, 'location')]",
                "//textarea[contains(@placeholder, 'site')]",
                "//textarea[contains(@id, 'site')]",
                "//textarea[contains(@aria-label, 'site')]",
                "//textarea[contains(@placeholder, 'location')]",
                "//textarea[contains(@id, 'location')]",
                "//textarea[contains(@aria-label, 'location')]",
            ],
            'site_coordinator': [
                "//input[@name='coordinator']",
                "//input[contains(@placeholder, 'coordinator')]",
                "//input[contains(@id, 'coordinator')]",
                "//input[contains(@aria-label, 'coordinator')]",
                "//input[contains(@name, 'site_coordinator')]",
                "//input[contains(@placeholder, 'site_coordinator')]",
                "//input[contains(@id, 'site_coordinator')]",
                "//input[contains(@aria-label, 'site_coordinator')]",
                "//input[contains(@name, 'who')]",
                "//input[contains(@placeholder, 'who')]",
                "//input[contains(@id, 'who')]",
                "//input[contains(@aria-label, 'who')]",
                "//textarea[contains(@placeholder, 'coordinator')]",
                "//textarea[contains(@id, 'coordinator')]",
                "//textarea[contains(@aria-label, 'coordinator')]",
                "//textarea[contains(@placeholder, 'site_coordinator')]",
                "//textarea[contains(@id, 'site_coordinator')]",
                "//textarea[contains(@aria-label, 'site_coordinator')]",
            ],
            'coordinator_email': [
                "//input[@type='email' and contains(@name, 'coordinator')]",
                "//input[@type='email' and contains(@id, 'coordinator')]",
                "//input[@type='email' and contains(@aria-label, 'coordinator')]",
                "//input[@type='email' and contains(@placeholder, 'coordinator')]",
                "//input[@type='email' and contains(@name, 'site_coordinator')]",
                "//input[@type='email' and contains(@id, 'site_coordinator')]",
                "//input[@type='email' and contains(@aria-label, 'site_coordinator')]",
                "//input[@type='email' and contains(@placeholder, 'site_coordinator')]",
                "//input[@type='email' and contains(@name, 'email') and contains(@name, 'coordinator')]",
                "//input[@type='email' and contains(@id, 'email') and contains(@id, 'coordinator')]",
                "//input[@type='email' and contains(@aria-label, 'email') and contains(@aria-label, 'coordinator')]",
                "//input[@type='email' and contains(@placeholder, 'email') and contains(@placeholder, 'coordinator')]",
                "//input[contains(@name, 'coordinator') and contains(@name, 'email')]",
                "//input[contains(@id, 'coordinator') and contains(@id, 'email')]",
                "//input[contains(@aria-label, 'coordinator') and contains(@aria-label, 'email')]",
                "//input[contains(@placeholder, 'coordinator') and contains(@placeholder, 'email')]",
            ],
        }
        
        from selenium.webdriver.support.ui import Select
        
        # Step 1: Fill First Name
        print("\n=== Step 1: Filling First Name ===")
        value = form_data.get('first_name', '')
        if value and value.lower() != 'none':
            try:
                element = driver.find_element(By.XPATH, field_mapping['first_name'])
                if element.is_displayed():
                    element.clear()
                    element.send_keys(value)
                    print(f"  Filled First Name: {value}")
                    time.sleep(FIELD_FILL_RATE_LIMIT)
                else:
                    print("  First Name field not visible.")
            except Exception as e:
                print(f"  Could not fill First Name: {e}")
        
        # Step 2: Fill Last Name
        print("\n=== Step 2: Filling Last Name ===")
        value = form_data.get('last_name', '')
        if value and value.lower() != 'none':
            try:
                element = driver.find_element(By.XPATH, field_mapping['last_name'])
                if element.is_displayed():
                    element.clear()
                    element.send_keys(value)
                    print(f"  Filled Last Name: {value}")
                    time.sleep(FIELD_FILL_RATE_LIMIT)
                else:
                    print("  Last Name field not visible.")
            except Exception as e:
                print(f"  Could not fill Last Name: {e}")
        
        # Step 3: Fill Email
        print("\n=== Step 3: Filling Email ===")
        value = form_data.get('email', '')
        if value and value.lower() != 'none':
            try:
                element = driver.find_element(By.XPATH, field_mapping['email'])
                if element.is_displayed():
                    element.clear()
                    element.send_keys(value)
                    print(f"  Filled Email: {value}")
                    time.sleep(FIELD_FILL_RATE_LIMIT)
                else:
                    print("  Email field not visible.")
            except Exception as e:
                print(f"  Could not fill Email: {e}")
        else:
            # Use site coordinator email as fallback
            fallback_email = SITE_COORDINATOR_EMAIL
            try:
                element = driver.find_element(By.XPATH, field_mapping['email'])
                if element.is_displayed():
                    element.clear()
                    element.send_keys(fallback_email)
                    print(f"  Filled Email (fallback): {fallback_email}")
                    time.sleep(FIELD_FILL_RATE_LIMIT)
                else:
                    print("  Email field not visible.")
            except Exception as e:
                print(f"  Could not fill Email: {e}")
        
        # Step 4: Fill Confirm Email
        print("\n=== Step 4: Filling Confirm Email ===")
        email_value = form_data.get('email', '')
        if email_value and email_value.lower() != 'none':
            confirm_value = email_value
        else:
            confirm_value = SITE_COORDINATOR_EMAIL  # Use fallback email
        
        try:
            element = driver.find_element(By.XPATH, field_mapping['confirm_email'])
            if element.is_displayed():
                element.clear()
                element.send_keys(confirm_value)
                print(f"  Filled Confirm Email: {confirm_value}")
                time.sleep(FIELD_FILL_RATE_LIMIT)
            else:
                print("  Confirm Email field not visible.")
        except Exception as e:
            print(f"  Could not fill Confirm Email: {e}")
        
        # Step 5: Uncheck "Keep me updated" checkbox
        print("\n=== Step 5: Unchecking 'Keep me updated' checkbox ===")
        time.sleep(2)
        
        try:
            checkbox = driver.find_element(By.XPATH, "//div[contains(@class, 'eds-checkbox')]//input[@type='checkbox']")
            if checkbox.is_displayed() and checkbox.is_selected():
                # Click the wrapper div to uncheck
                wrapper = driver.find_element(By.XPATH, "//div[contains(@class, 'eds-checkbox')]")
                wrapper.click()
                print("  Clicked 'Keep me updated' checkbox wrapper to uncheck it.")
                time.sleep(FIELD_FILL_RATE_LIMIT)
            else:
                print("  'Keep me updated' checkbox not found or already unchecked.")
        except Exception as e:
            print(f"  Could not handle 'Keep me updated' checkbox: {e}")
        
        # Step 6: Fill Address
        print("\n=== Step 6: Filling Address ===")
        value = form_data.get('address', '')
        if value and value.lower() != 'none':
            try:
                element = driver.find_element(By.XPATH, field_mapping['address'])
                if element.is_displayed():
                    element.clear()
                    element.send_keys(value)
                    print(f"  Filled Address: {value}")
                    time.sleep(FIELD_FILL_RATE_LIMIT)
                else:
                    print("  Address field not visible.")
            except Exception as e:
                print(f"  Could not fill Address: {e}")
        else:
            # Use fallback address
            fallback_address = "47111 Mission Falls Ct"
            try:
                element = driver.find_element(By.XPATH, field_mapping['address'])
                if element.is_displayed():
                    element.clear()
                    element.send_keys(fallback_address)
                    print(f"  Filled Address (fallback): {fallback_address}")
                    time.sleep(FIELD_FILL_RATE_LIMIT)
                else:
                    print("  Address field not visible.")
            except Exception as e:
                print(f"  Could not fill Address: {e}")
        
        # Step 7: Fill City
        print("\n=== Step 7: Filling City ===")
        address_value = form_data.get('address', '')
        if address_value and address_value.lower() != 'none':
            value = form_data.get('city', '')
        else:
            # Use fallback city when address is None
            value = 'Fremont'
        
        if value and value.lower() != 'none':
            try:
                element = driver.find_element(By.XPATH, field_mapping['city'])
                if element.is_displayed():
                    element.clear()
                    element.send_keys(value)
                    print(f"  Filled City: {value}")
                    time.sleep(FIELD_FILL_RATE_LIMIT)
                else:
                    print("  City field not visible.")
            except Exception as e:
                print(f"  Could not fill City: {e}")
        
        # Step 8: Fill State (Dropdown)
        print("\n=== Step 8: Filling State (Dropdown) ===")
        address_value = form_data.get('address', '')
        if address_value and address_value.lower() != 'none':
            state_value = form_data.get('state', '')
        else:
            # Use fallback state when address is None
            state_value = 'CA'
        
        if state_value == 'CA':
            state_value = 'California'  # Convert CA to California for dropdown
        
        try:
            element = driver.find_element(By.XPATH, field_mapping['state'])
            if element.is_displayed():
                select_element = Select(element)
                select_element.select_by_visible_text('California')
                print(f"  Selected State: California")
                time.sleep(FIELD_FILL_RATE_LIMIT)
            else:
                print("  State dropdown not visible.")
        except Exception as e:
            print(f"  Could not fill State: {e}")
        
        # Step 9: Fill Zip Code
        print("\n=== Step 9: Filling Zip Code ===")
        address_value = form_data.get('address', '')
        if address_value and address_value.lower() != 'none':
            value = form_data.get('zip_code', '')
        else:
            # Use fallback zip when address is None
            value = '94539'
        
        if value and value.lower() != 'none':
            try:
                element = driver.find_element(By.XPATH, field_mapping['zip_code'])
                if element.is_displayed():
                    element.clear()
                    element.send_keys(value)
                    print(f"  Filled Zip Code: {value}")
                    time.sleep(FIELD_FILL_RATE_LIMIT)
                else:
                    print("  Zip Code field not visible.")
            except Exception as e:
                print(f"  Could not fill Zip Code: {e}")
        
        # Step 10: Fill Country - Select United States
        print("\n=== Step 10: Filling Country ===")
        country_value = COUNTRY  # Use the configuration variable
        country_selectors = [
            "//select[@id='N-homecountry']",
            "//select[@name='buyer.N-home.country']",
            "//select[contains(@class, 'eds-field-styled__select')]",
            "//select[@name='country']",
            "//select[contains(@id, 'country')]",
            "//select[contains(@aria-label, 'Country')]",
            "//select[contains(@class, 'country')]",
            # Try to find any select element that might be a country dropdown
            "//select[contains(@name, 'country') or contains(@id, 'country') or contains(@aria-label, 'country')]",
        ]
        
        # Wait for dropdowns to be present
        time.sleep(2)
        
        country_filled = False
        for selector in country_selectors:
            try:
                elements = driver.find_elements(By.XPATH, selector)
                print(f"    Found {len(elements)} elements with selector: {selector}")
                for element in elements:
                    if element.is_displayed():
                        print(f"      Country dropdown found: {element.get_attribute('name')} | {element.get_attribute('id')} | {element.get_attribute('aria-label')}")
                        # Always try to work with the dropdown
                        try:
                            # First, let's see what options are available
                            select_element = Select(element)
                            options = [option.text for option in select_element.options]
                            print(f"      Available dropdown options: {options}")
                            
                            Select(element).select_by_visible_text(country_value)
                            print(f"  Selected Country: {country_value}")
                            country_filled = True
                            break
                        except Exception as e:
                            print(f"      Could not select country '{country_value}': {e}")
                            # Try with abbreviated name
                            if country_value == 'United States':
                                try:
                                    Select(element).select_by_visible_text('US')
                                    print(f"  Selected Country: US")
                                    country_filled = True
                                    break
                                except Exception as e2:
                                    print(f"      Could not select country 'US' either: {e2}")
                                    # Try with partial match
                                    try:
                                        for option in select_element.options:
                                            if 'united states' in option.text.lower() or 'usa' in option.text.lower() or 'us' in option.text.lower():
                                                select_element.select_by_visible_text(option.text)
                                                print(f"  Selected Country: {option.text}")
                                                country_filled = True
                                                break
                                    except Exception as e3:
                                        print(f"      Could not find United States in options: {e3}")
                if country_filled:
                    break
            except Exception as e:
                print(f"    Error with selector {selector}: {e}")
                continue
        
        if not country_filled:
            print("  Could not find Country dropdown.")
        else:
            print(f"  Waiting {FIELD_FILL_RATE_LIMIT} seconds...")
            time.sleep(FIELD_FILL_RATE_LIMIT)

        # Step 11b: Handle 55+ age confirmation (separate radio group)
        if form_data.get('age_confirmation', '').lower() == 'yes':
            print("\n=== Step 11b: Selecting 'Yes' for 55+ age confirmation (separate radio group) ===")
            try:
                # Find all radio groups
                radio_groups = driver.find_elements(By.XPATH, "//div[contains(@class, 'eds-radio') and @role='radiogroup']")
                print(f"      Found {len(radio_groups)} radio groups")
                
                for i, group in enumerate(radio_groups):
                    group_text = group.text.lower()
                    print(f"      Radio group {i} text: {group_text}")
                    
                    # Look for the 55+ age confirmation radio group
                    if 'i am an older adult age 55 or older' in group_text or 'older adult age 55' in group_text:
                        print(f"      Found 55+ age confirmation radio group {i}")
                        # Look for "Yes" option
                        try:
                            yes_option = group.find_element(By.XPATH, ".//div[contains(@class, 'eds-radio__option')]//label[contains(text(), 'Yes')] | .//div[contains(@class, 'eds-radio__option')]//span[contains(text(), 'Yes')]")
                            if yes_option:
                                yes_option.click()
                                print(f"  Selected 'Yes' for 55+ age confirmation radio group {i}")
                                break
                        except Exception as e:
                            print(f"      Could not find 'Yes' option in 55+ group {i}: {e}")
                            
            except Exception as e:
                print(f"  Could not select 'Yes' for 55+ age radio: {e}")
            print(f"  Waiting {FIELD_FILL_RATE_LIMIT} seconds...")
            time.sleep(FIELD_FILL_RATE_LIMIT)

        # Step 12b: Handle Alameda County confirmation (separate radio group)
        if form_data.get('location_confirmation', '').lower() == 'yes':
            print("\n=== Step 12b: Selecting 'Yes' for Alameda County confirmation (separate radio group) ===")
            try:
                radio_groups = driver.find_elements(By.XPATH, "//div[contains(@class, 'eds-radio') and @role='radiogroup']")
                print(f"      Found {len(radio_groups)} radio groups")
                
                for i, group in enumerate(radio_groups):
                    group_text = group.text.lower()
                    print(f"      Radio group {i} text: {group_text}")
                    
                    # Look for the separate "I live in Alameda County" radio group
                    if 'i live in alameda county' in group_text or ('yes i do' in group_text and 'no i do not' in group_text):
                        print(f"      Found 'I live in Alameda County' radio group {i}")
                        # Look for "Yes I do" option
                        try:
                            yes_option = group.find_element(By.XPATH, ".//div[contains(@class, 'eds-radio__option')]//label[contains(text(), 'Yes I do')] | .//div[contains(@class, 'eds-radio__option')]//span[contains(text(), 'Yes I do')]")
                            if yes_option:
                                yes_option.click()
                                print(f"  Selected 'Yes I do' for Alameda County radio group {i}")
                                break
                        except Exception as e:
                            print(f"      Could not find 'Yes I do' option in group {i}: {e}")
                            
            except Exception as e:
                print(f"  Could not select 'Yes' for Alameda County radio: {e}")
            print(f"  Waiting {FIELD_FILL_RATE_LIMIT} seconds...")
            time.sleep(FIELD_FILL_RATE_LIMIT)

        # Step 12b2: Handle HLF Bus option (right after Alameda County confirmation)
        if HLF_BUS_OPTION:
            print("\n=== Step 12b2: Selecting HLF Bus option ===")
            try:
                # Look for the HLF bus option in the transportation radio group
                radio_groups = driver.find_elements(By.XPATH, "//div[contains(@class, 'eds-radio') and @role='radiogroup']")
                print(f"      Found {len(radio_groups)} radio groups")
                
                for i, group in enumerate(radio_groups):
                    group_text = group.text.lower()
                    print(f"      Radio group {i} text: {group_text}")
                    
                    # Look for transportation radio group that contains HLF bus option
                    if 'hlf provided bus' in group_text or 'large sites only' in group_text:
                        print(f"      Found transportation radio group {i} with HLF bus option")
                        # Look for "HLF Provided Bus" option
                        try:
                            hlf_option = group.find_element(By.XPATH, ".//div[contains(@class, 'eds-radio__option')]//label[contains(text(), 'HLF Provided Bus')] | .//div[contains(@class, 'eds-radio__option')]//span[contains(text(), 'HLF Provided Bus')] | .//div[contains(@class, 'eds-radio__option')]//label[contains(text(), 'hlf provided bus')] | .//div[contains(@class, 'eds-radio__option')]//span[contains(text(), 'hlf provided bus')]")
                            if hlf_option:
                                hlf_option.click()
                                print(f"  Selected 'HLF Provided Bus' option in radio group {i}")
                                break
                        except Exception as e:
                            print(f"      Could not find 'HLF Provided Bus' option in group {i}: {e}")
                            
            except Exception as e:
                print(f"  Could not select HLF Bus option: {e}")
            print(f"  Waiting {FIELD_FILL_RATE_LIMIT} seconds...")
            time.sleep(FIELD_FILL_RATE_LIMIT)
        else:
            print("\n=== Step 12b2: Skipping HLF Bus option (HLF_BUS_OPTION = False) ===")

        # Step 12b3: Handle Site Coordinator Bus Confirmation (right after HLF Bus selection)
        if SITE_COORDINATOR_BUS_CONFIRMATION:
            print("\n=== Step 12b3: Selecting 'Yes' for Site Coordinator Bus Confirmation ===")
            try:
                # Look for the site coordinator bus confirmation radio group
                radio_groups = driver.find_elements(By.XPATH, "//div[contains(@class, 'eds-radio') and @role='radiogroup']")
                print(f"      Found {len(radio_groups)} radio groups")
                
                for i, group in enumerate(radio_groups):
                    group_text = group.text.lower()
                    print(f"      Radio group {i} text: {group_text}")
                    
                    # Look for site coordinator bus confirmation radio group
                    if 'have the site coordinator confirmed the bus' in group_text or 'site coordinator confirmed' in group_text:
                        print(f"      Found site coordinator bus confirmation radio group {i}")
                        # Look for "Yes" option
                        try:
                            yes_option = group.find_element(By.XPATH, ".//div[contains(@class, 'eds-radio__option')]//label[contains(text(), 'Yes')] | .//div[contains(@class, 'eds-radio__option')]//span[contains(text(), 'Yes')]")
                            if yes_option:
                                yes_option.click()
                                print(f"  Selected 'Yes' for site coordinator bus confirmation radio group {i}")
                                break
                        except Exception as e:
                            print(f"      Could not find 'Yes' option in site coordinator group {i}: {e}")
                            
            except Exception as e:
                print(f"  Could not select 'Yes' for site coordinator bus confirmation: {e}")
            print(f"  Waiting {FIELD_FILL_RATE_LIMIT} seconds...")
            time.sleep(FIELD_FILL_RATE_LIMIT)
        else:
            print("\n=== Step 12b3: Skipping Site Coordinator Bus Confirmation (SITE_COORDINATOR_BUS_CONFIRMATION = False) ===")

        # Step 12b4: Fill Site/Location Name and Site Coordinator Info (by order, after HLF Bus selection)
        if HLF_BUS_OPTION:
            print(f"\n=== Step 12b4: Filling Site/Location and Site Coordinator Info (after HLF Bus selection) ===")
            site_location_value = SITE_LOCATION
            site_coordinator_value = SITE_COORDINATOR_NAME
            site_coordinator_email_value = SITE_COORDINATOR_EMAIL
            site_coordinator_phone_value = SITE_COORDINATOR_PHONE
            print(f"  Site/Location value: {site_location_value}")
            print(f"  Site Coordinator value: {site_coordinator_value}")
            print(f"  Site Coordinator Email value: {site_coordinator_email_value}")
            print(f"  Site Coordinator Phone value: {site_coordinator_phone_value}")
            
            # Wait for additional fields to appear after HLF Bus selection
            print("  Waiting for additional fields to appear after HLF Bus selection...")
            time.sleep(3)
            
            # Find all visible input fields with name starting with 'buyer.U-'
            all_inputs = driver.find_elements(By.XPATH, "//input[starts-with(@name, 'buyer.U-') and not(@type='hidden')]")
            visible_inputs = [inp for inp in all_inputs if inp.is_displayed()]
            print(f"    Found {len(visible_inputs)} visible 'buyer.U-' input fields")
            # Optionally include textareas if needed
            all_textareas = driver.find_elements(By.XPATH, "//textarea[starts-with(@id, 'buyer.U-')]")
            visible_textareas = [ta for ta in all_textareas if ta.is_displayed()]
            print(f"    Found {len(visible_textareas)} visible 'buyer.U-' textarea fields")
            
            # Fill in order: site/location, coordinator name, coordinator email, coordinator phone
            values = [site_location_value, site_coordinator_value, site_coordinator_email_value, site_coordinator_phone_value]
            for i, value in enumerate(values):
                if i < len(visible_inputs):
                    try:
                        visible_inputs[i].clear()
                        visible_inputs[i].send_keys(value)
                        print(f"  Filled field {i+1} with value: {value}")
                        time.sleep(FIELD_FILL_RATE_LIMIT)
                    except Exception as e:
                        print(f"  Could not fill field {i+1}: {e}")
                else:
                    print(f"  Not enough visible input fields to fill value: {value}")
            # If there are textareas and more values, fill them too
            for j, ta in enumerate(visible_textareas):
                idx = len(visible_inputs) + j
                if idx < len(values):
                    try:
                        ta.clear()
                        ta.send_keys(values[idx])
                        print(f"  Filled textarea field {idx+1} with value: {values[idx]}")
                        time.sleep(FIELD_FILL_RATE_LIMIT)
                    except Exception as e:
                        print(f"  Could not fill textarea field {idx+1}: {e}")

            # Now select 'Yes' for the site coordinator confirmed bus radio group
            print(f"\n=== Step 12b5: Selecting 'Yes' for Site Coordinator Confirmed Bus (after HLF Bus selection) ===")
            try:
                # Find all radio groups after HLF Bus selection
                radio_groups = driver.find_elements(By.XPATH, "//div[contains(@class, 'eds-radio')]")
                print(f"  Found {len(radio_groups)} radio groups after HLF Bus selection")
                
                # Debug: Print HTML structure of each radio group
                for i, group in enumerate(radio_groups):
                    group_text = group.text.lower()
                    print(f"  Radio group {i} text: {group_text}")
                    
                    # Print HTML structure for debugging
                    try:
                        group_html = group.get_attribute('outerHTML')
                        print(f"  Radio group {i} HTML structure:")
                        print(f"    {group_html[:500]}...")  # First 500 chars
                    except Exception as html_error:
                        print(f"    Could not get HTML for radio group {i}: {html_error}")
                
                # Try multiple strategies to find and select the correct radio group
                selected = False
                
                # Strategy 1: Look for radio group that appears after HLF Bus selection (should be the 3rd or 4th radio group)
                if len(radio_groups) >= 13:
                    target_group_index = 13  # The site coordinator question is the 14th radio group (index 13)
                    if target_group_index < len(radio_groups):
                        print(f"  Trying Strategy 1: Targeting radio group {target_group_index} (should be site coordinator question)")
                        try:
                            target_group = radio_groups[target_group_index]
                            
                            # Find the radio input directly (not the container)
                            radio_inputs = target_group.find_elements(By.CSS_SELECTOR, "input[type='radio']")
                            if radio_inputs:
                                # Target the first radio input (which should be "Yes")
                                first_radio_input = radio_inputs[0]
                                
                                # Scroll to the element
                                driver.execute_script("arguments[0].scrollIntoView(true);", first_radio_input)
                                time.sleep(0.5)
                                
                                # Method 1: Try clicking the label first (this often works better)
                                try:
                                    radio_id = first_radio_input.get_attribute('id')
                                    if radio_id:
                                        # Find the label associated with this radio input
                                        label = driver.find_element(By.CSS_SELECTOR, f"label[for='{radio_id}']")
                                        driver.execute_script("arguments[0].scrollIntoView(true);", label)
                                        time.sleep(0.5)
                                        label.click()
                                        print(f"    Clicked label for radio input in radio group {target_group_index}")
                                        time.sleep(0.5)
                                except Exception as label_error:
                                    print(f"    Could not click label: {label_error}")
                                
                                # Method 2: Direct click on radio input (if label didn't work)
                                try:
                                    first_radio_input.click()
                                    print(f"    Clicked radio input directly for radio group {target_group_index}")
                                    time.sleep(0.5)
                                except Exception as radio_error:
                                    print(f"    Could not click radio input directly: {radio_error}")
                                
                                # Method 3: JavaScript to set checked and trigger events
                                try:
                                    driver.execute_script("""
                                        arguments[0].checked = true;
                                        arguments[0].click();
                                        arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
                                        arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                                    """, first_radio_input)
                                    print(f"    Forced radio input selection with JavaScript for radio group {target_group_index}")
                                    time.sleep(0.5)
                                except Exception as js_error:
                                    print(f"    JavaScript method failed: {js_error}")
                                
                                # Method 4: Try clicking the parent container
                                try:
                                    parent_container = first_radio_input.find_element(By.XPATH, "./..")
                                    parent_container.click()
                                    print(f"    Clicked parent container for radio group {target_group_index}")
                                    time.sleep(0.5)
                                except Exception as parent_error:
                                    print(f"    Could not click parent container: {parent_error}")
                                
                                selected = True
                            else:
                                print(f"    Could not find radio inputs in radio group {target_group_index}")
                        except Exception as e:
                            print(f"    Strategy 1 failed: {e}")
                
                # Strategy 2: Look for radio group with simple "yes/no" text
                if not selected:
                    for i, group in enumerate(radio_groups):
                        group_text = group.text.lower()
                        if 'yes' in group_text and 'no' in group_text and len(group_text.split()) < 10:
                            print(f"  Trying Strategy 2: Targeting radio group {i} with simple yes/no text")
                            try:
                                first_option = group.find_element(By.CSS_SELECTOR, "div.eds-radio__option[data-spec='radio-option-container']")
                                if first_option:
                                    driver.execute_script("arguments[0].scrollIntoView(true);", first_option)
                                    first_option.click()
                                    print(f"    Clicked first option in radio group {i}")
                                    time.sleep(0.5)
                                    
                                    # Also try JavaScript
                                    driver.execute_script("""
                                        arguments[0].click();
                                        var event = new Event('click', { bubbles: true });
                                        arguments[0].dispatchEvent(event);
                                    """, first_option)
                                    print(f"    Forced click with JavaScript on radio group {i}")
                                    selected = True
                                    break
                            except Exception as e:
                                print(f"    Strategy 2 failed for group {i}: {e}")
                
                # Strategy 3: Try clicking the 3rd radio group specifically (most likely to be site coordinator)
                if not selected and len(radio_groups) >= 3:
                    print(f"  Trying Strategy 3: Targeting radio group 2 (3rd radio group)")
                    try:
                        target_group = radio_groups[2]  # 3rd radio group (index 2)
                        first_option = target_group.find_element(By.CSS_SELECTOR, "div.eds-radio__option[data-spec='radio-option-container']")
                        if first_option:
                            driver.execute_script("arguments[0].scrollIntoView(true);", first_option)
                            first_option.click()
                            print(f"    Clicked first option in radio group 2")
                            time.sleep(0.5)
                            
                            # Also try JavaScript
                            driver.execute_script("""
                                arguments[0].click();
                                var event = new Event('click', { bubbles: true });
                                arguments[0].dispatchEvent(event);
                            """, first_option)
                            print(f"    Forced click with JavaScript on radio group 2")
                            selected = True
                    except Exception as e:
                        print(f"    Strategy 3 failed: {e}")
                
                if selected:
                    print(f"  Successfully selected 'Yes' for site coordinator confirmed bus")
                else:
                    print(f"  Could not select 'Yes' for site coordinator confirmed bus with any strategy")
                    
            except Exception as e:
                print(f"  Error selecting site coordinator confirmed bus: {e}")
            
            print(f"  Waiting {FIELD_FILL_RATE_LIMIT} seconds...")
            time.sleep(FIELD_FILL_RATE_LIMIT)

        # Note: Site coordinator fields are now handled in Step 12b4 using order-based filling
        # Removed duplicate sections 12b6, 12b7, 12b8 to prevent overwriting main email field

        # Step 12c: Handle lunch preference (Vegetarian)
        if form_data.get('lunch_preference', '').lower() == 'vegetarian':
            print("\n=== Step 12c: Selecting 'Vegetarian' for lunch preference ===")
            try:
                radio_groups = driver.find_elements(By.XPATH, "//div[contains(@class, 'eds-radio') and @role='radiogroup']")
                print(f"      Found {len(radio_groups)} radio groups")
                
                for i, group in enumerate(radio_groups):
                    group_text = group.text.lower()
                    print(f"      Radio group {i} text: {group_text}")
                    
                    # Look for lunch preference radio group
                    if 'vegetarian lunch' in group_text and 'meat option lunch' in group_text:
                        print(f"      Found lunch preference radio group {i}")
                        # Look for "Vegetarian Lunch" option
                        try:
                            veg_option = group.find_element(By.XPATH, ".//div[contains(@class, 'eds-radio__option')]//label[contains(text(), 'Vegetarian Lunch')] | .//div[contains(@class, 'eds-radio__option')]//span[contains(text(), 'Vegetarian Lunch')]")
                            if veg_option:
                                veg_option.click()
                                print(f"  Selected 'Vegetarian Lunch' for lunch preference radio group {i}")
                                break
                        except Exception as e:
                            print(f"      Could not find 'Vegetarian Lunch' option in group {i}: {e}")
                            
            except Exception as e:
                print(f"  Could not select 'Vegetarian' for lunch preference: {e}")
            print(f"  Waiting {FIELD_FILL_RATE_LIMIT} seconds...")
            time.sleep(FIELD_FILL_RATE_LIMIT)

        # Step 12d: Handle liability agreement
        print("\n=== Step 12d: Selecting 'Yes, I agree' for liability agreement ===")
        try:
            radio_groups = driver.find_elements(By.XPATH, "//div[contains(@class, 'eds-radio') and @role='radiogroup']")
            print(f"      Found {len(radio_groups)} radio groups")
            
            for i, group in enumerate(radio_groups):
                group_text = group.text.lower()
                print(f"      Radio group {i} text: {group_text}")
                
                # Look for liability agreement radio group
                if 'yes, i agree' in group_text:
                    print(f"      Found liability agreement radio group {i}")
                    # Look for "Yes, I agree" option
                    try:
                        agree_option = group.find_element(By.XPATH, ".//div[contains(@class, 'eds-radio__option')]//label[contains(text(), 'Yes, I agree')] | .//div[contains(@class, 'eds-radio__option')]//span[contains(text(), 'Yes, I agree')]")
                        if agree_option:
                            agree_option.click()
                            print(f"  Selected 'Yes, I agree' for liability agreement radio group {i}")
                            break
                    except Exception as e:
                        print(f"      Could not find 'Yes, I agree' option in group {i}: {e}")
                        
        except Exception as e:
            print(f"  Could not select 'Yes, I agree' for liability agreement: {e}")
        print(f"  Waiting {FIELD_FILL_RATE_LIMIT} seconds...")
        time.sleep(FIELD_FILL_RATE_LIMIT)
        
        # Step 11: Check 55+ age confirmation
        print("\n=== Step 11: Checking 55+ age confirmation ===")
        age_checkbox_selectors = [
            "//input[@type='checkbox' and contains(@name, '55')]",
            "//input[@type='checkbox' and contains(@id, '55')]",
            "//input[@type='checkbox' and contains(@aria-label, '55')]",
            "//input[@type='checkbox' and contains(@name, 'age')]",
            "//input[@type='checkbox' and contains(@id, 'age')]",
            "//input[@type='checkbox' and contains(@aria-label, 'age')]",
            "//input[@type='checkbox' and contains(@name, 'older')]",
            "//input[@type='checkbox' and contains(@id, 'older')]",
            "//input[@type='checkbox' and contains(@aria-label, 'older')]",
            "//input[@type='checkbox' and contains(@name, 'senior')]",
            "//input[@type='checkbox' and contains(@id, 'senior')]",
            "//input[@type='checkbox' and contains(@aria-label, 'senior')]",
            # More generic selectors
            "//input[@type='checkbox' and ancestor::div[contains(text(), '55')]]",
            "//input[@type='checkbox' and ancestor::div[contains(text(), 'age')]]",
            "//input[@type='checkbox' and ancestor::div[contains(text(), 'older')]]",
            "//input[@type='checkbox' and following-sibling::label[contains(text(), '55')]]",
            "//input[@type='checkbox' and following-sibling::label[contains(text(), 'age')]]",
            "//input[@type='checkbox' and following-sibling::label[contains(text(), 'older')]]",
        ]
        
        age_checked = False
        for selector in age_checkbox_selectors:
            try:
                elements = driver.find_elements(By.XPATH, selector)
                print(f"    Found {len(elements)} elements with selector: {selector}")
                for element in elements:
                    if element.is_displayed():
                        print(f"      Age checkbox found: {element.get_attribute('name')} | {element.get_attribute('id')} | {element.get_attribute('aria-label')}")
                        if not element.is_selected():
                            element.click()
                            print("  Checked 55+ age confirmation.")
                            age_checked = True
                            break
                        else:
                            print("  Age checkbox already selected.")
                            age_checked = True
                            break
                if age_checked:
                    break
            except Exception as e:
                print(f"    Error with selector {selector}: {e}")
                continue
        
        if not age_checked:
            print("  Could not find or check 55+ age confirmation checkbox.")
        
        print(f"  Waiting {FIELD_FILL_RATE_LIMIT} seconds...")
        time.sleep(FIELD_FILL_RATE_LIMIT)
        
        # Step 12: Alameda County is handled by radio button selection above
        print("\n=== Step 12: Alameda County confirmation handled by radio button ===")
        print("  Alameda County confirmation is a radio button, not a checkbox.")
        print("  Radio button selection was already handled in Step 12b.")
        print(f"  Waiting {FIELD_FILL_RATE_LIMIT} seconds...")
        time.sleep(FIELD_FILL_RATE_LIMIT)
        
        # Step 13: Check HLF bus option
        print("\n=== Step 13: Checking HLF bus option ===")
        hlf_checkbox_selectors = [
            "//input[@type='checkbox' and contains(@name, 'HLF')]",
            "//input[@type='checkbox' and contains(@id, 'HLF')]",
            "//input[@type='checkbox' and contains(@aria-label, 'HLF')]",
            "//input[@type='checkbox' and contains(@name, 'hlf')]",
            "//input[@type='checkbox' and contains(@id, 'hlf')]",
            "//input[@type='checkbox' and contains(@aria-label, 'hlf')]",
            "//input[@type='checkbox' and contains(@name, 'bus')]",
            "//input[@type='checkbox' and contains(@id, 'bus')]",
            "//input[@type='checkbox' and contains(@aria-label, 'bus')]",
            "//input[@type='checkbox' and contains(@name, 'transport')]",
            "//input[@type='checkbox' and contains(@id, 'transport')]",
            "//input[@type='checkbox' and contains(@aria-label, 'transport')]",
        ]
        
        hlf_checked = False
        for selector in hlf_checkbox_selectors:
            try:
                elements = driver.find_elements(By.XPATH, selector)
                for element in elements:
                    if element.is_displayed() and not element.is_selected():
                        element.click()
                        print("  Checked HLF bus option.")
                        hlf_checked = True
                        break
                if hlf_checked:
                    break
            except:
                continue
        
        if not hlf_checked:
            print("  Could not find or check HLF bus option checkbox.")
        
        print(f"  Waiting {FIELD_FILL_RATE_LIMIT} seconds...")
        time.sleep(FIELD_FILL_RATE_LIMIT)
        
        # Step 14: Check site coordinator confirmed bus
        print("\n=== Step 14: Checking site coordinator confirmed bus ===")
        coordinator_checkbox_selectors = [
            "//input[@type='checkbox' and contains(@name, 'coordinator')]",
            "//input[@type='checkbox' and contains(@id, 'coordinator')]",
            "//input[@type='checkbox' and contains(@aria-label, 'coordinator')]",
            "//input[@type='checkbox' and contains(@name, 'site')]",
            "//input[@type='checkbox' and contains(@id, 'site')]",
            "//input[@type='checkbox' and contains(@aria-label, 'site')]",
            "//input[@type='checkbox' and contains(@name, 'confirmed')]",
            "//input[@type='checkbox' and contains(@id, 'confirmed')]",
            "//input[@type='checkbox' and contains(@aria-label, 'confirmed')]",
        ]
        
        coordinator_checked = False
        for selector in coordinator_checkbox_selectors:
            try:
                elements = driver.find_elements(By.XPATH, selector)
                for element in elements:
                    if element.is_displayed() and not element.is_selected():
                        element.click()
                        print("  Checked site coordinator confirmed bus.")
                        coordinator_checked = True
                        break
                if coordinator_checked:
                    break
            except:
                continue
        
        if not coordinator_checked:
            print("  Could not find or check site coordinator confirmed bus checkbox.")
        
        print(f"  Waiting {FIELD_FILL_RATE_LIMIT} seconds...")
        time.sleep(FIELD_FILL_RATE_LIMIT)
        
        print("  Form filling completed!")
        
        # Handle checkboxes for age confirmation and location confirmation
        print("\n=== Handling checkboxes ===")
        
        # Check age confirmation (55+)
        if CHECK_AGE_CONFIRMATION and form_data.get('age_confirmation') == 'Yes':
            age_checkbox_selectors = [
                "//input[@type='checkbox' and contains(@name, 'age')]",
                "//input[@type='checkbox' and contains(@id, 'age')]",
                "//input[@type='checkbox' and contains(@aria-label, 'age')]",
                "//input[@type='checkbox' and contains(@name, '55')]",
                "//input[@type='checkbox' and contains(@id, '55')]",
                "//input[@type='checkbox' and contains(@aria-label, '55')]",
                "//input[@type='checkbox' and contains(@name, 'older')]",
                "//input[@type='checkbox' and contains(@id, 'older')]",
                "//input[@type='checkbox' and contains(@aria-label, 'older')]",
                "//input[@type='checkbox' and contains(@name, 'senior')]",
                "//input[@type='checkbox' and contains(@id, 'senior')]",
                "//input[@type='checkbox' and contains(@aria-label, 'senior')]",
            ]
            
            age_checked = False
            for selector in age_checkbox_selectors:
                try:
                    elements = driver.find_elements(By.XPATH, selector)
                    for element in elements:
                        if element.is_displayed() and not element.is_selected():
                            element.click()
                            print("  Checked age confirmation (55+) checkbox.")
                            age_checked = True
                            break
                    if age_checked:
                        break
                except:
                    continue
            
            if not age_checked:
                print("  Could not find age confirmation checkbox.")
            else:
                print(f"  Waiting {FIELD_FILL_RATE_LIMIT} seconds before next checkbox...")
                time.sleep(FIELD_FILL_RATE_LIMIT)
        
        # Location confirmation (Alameda County) is handled by radio button selection above
        if CHECK_LOCATION_CONFIRMATION and form_data.get('location_confirmation') == 'Yes':
            print("  Location confirmation (Alameda County) is handled by radio button selection.")
            print("  Radio button selection was already handled in Step 12b.")
            print(f"  Waiting {FIELD_FILL_RATE_LIMIT} seconds before next checkbox...")
            time.sleep(FIELD_FILL_RATE_LIMIT)
        
        # Check HLF Provided Bus option
        if CHECK_HLF_BUS:
            bus_checkbox_selectors = [
            "//input[@type='checkbox' and contains(@name, 'bus')]",
            "//input[@type='checkbox' and contains(@id, 'bus')]",
            "//input[@type='checkbox' and contains(@aria-label, 'bus')]",
            "//input[@type='checkbox' and contains(@name, 'HLF')]",
            "//input[@type='checkbox' and contains(@id, 'HLF')]",
            "//input[@type='checkbox' and contains(@aria-label, 'HLF')]",
            "//input[@type='checkbox' and contains(@name, 'provided')]",
            "//input[@type='checkbox' and contains(@id, 'provided')]",
            "//input[@type='checkbox' and contains(@aria-label, 'provided')]",
            "//input[@type='checkbox' and contains(@name, 'transport')]",
            "//input[@type='checkbox' and contains(@id, 'transport')]",
            "//input[@type='checkbox' and contains(@aria-label, 'transport')]",
            "//input[@type='checkbox' and contains(@name, 'shuttle')]",
            "//input[@type='checkbox' and contains(@id, 'shuttle')]",
            "//input[@type='checkbox' and contains(@aria-label, 'shuttle')]",
        ]
        
        bus_checked = False
        for selector in bus_checkbox_selectors:
            try:
                elements = driver.find_elements(By.XPATH, selector)
                for element in elements:
                    if element.is_displayed() and not element.is_selected():
                        element.click()
                        print("  Checked HLF Provided Bus option.")
                        bus_checked = True
                        break
                if bus_checked:
                    break
            except:
                continue
        
            if not bus_checked:
                print("  Could not find HLF Provided Bus checkbox.")
            else:
                print(f"  Waiting {FIELD_FILL_RATE_LIMIT} seconds before next checkbox...")
                time.sleep(FIELD_FILL_RATE_LIMIT)
        
        # Check site coordinator confirmation (after bus option)
        if CHECK_COORDINATOR_CONFIRMATION:
            coordinator_checkbox_selectors = [
            "//input[@type='checkbox' and contains(@name, 'coordinator')]",
            "//input[@type='checkbox' and contains(@id, 'coordinator')]",
            "//input[@type='checkbox' and contains(@aria-label, 'coordinator')]",
            "//input[@type='checkbox' and contains(@name, 'site')]",
            "//input[@type='checkbox' and contains(@id, 'site')]",
            "//input[@type='checkbox' and contains(@aria-label, 'site')]",
            "//input[@type='checkbox' and contains(@name, 'confirmed')]",
            "//input[@type='checkbox' and contains(@id, 'confirmed')]",
            "//input[@type='checkbox' and contains(@aria-label, 'confirmed')]",
            "//input[@type='checkbox' and contains(@name, 'bus') and contains(@name, 'confirm')]",
            "//input[@type='checkbox' and contains(@id, 'bus') and contains(@id, 'confirm')]",
            "//input[@type='checkbox' and contains(@aria-label, 'bus') and contains(@aria-label, 'confirm')]",
        ]
        
        coordinator_checked = False
        for selector in coordinator_checkbox_selectors:
            try:
                elements = driver.find_elements(By.XPATH, selector)
                for element in elements:
                    if element.is_displayed() and not element.is_selected():
                        element.click()
                        print("  Checked site coordinator confirmation checkbox.")
                        coordinator_checked = True
                        break
                if coordinator_checked:
                    break
            except:
                continue
        
            if not coordinator_checked:
                print("  Could not find site coordinator confirmation checkbox.")
            else:
                print(f"  Waiting {FIELD_FILL_RATE_LIMIT} seconds before completing...")
                time.sleep(FIELD_FILL_RATE_LIMIT)
        
        print("  Checkbox handling completed!")
        
        # Step 15: Check all liability checkboxes with the label 'I agree to the above additional terms.'
        print("\n=== Step 15: Checking all liability checkboxes ===")
        
        # Always check liability checkboxes regardless of form data
        print("  Always checking liability checkboxes (default behavior)")
        
        try:
            checkbox_labels = driver.find_elements(
                By.XPATH,
                "//label[contains(., 'I agree to the above additional terms.')]"
            )
            print(f"  Found {len(checkbox_labels)} liability checkboxes")
            for idx, label in enumerate(checkbox_labels):
                try:
                    driver.execute_script("arguments[0].scrollIntoView(true);", label)
                    label.click()
                    print(f"  Checked liability checkbox {idx+1}")
                    time.sleep(FIELD_FILL_RATE_LIMIT)
                except Exception as e:
                    print(f"  Could not check liability checkbox {idx+1}: {e}")
        except Exception as e:
            print(f"  Error finding liability checkboxes: {e}")
        
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
    driver.get(EVENTBRITE_URL)

    # Wait for the page to load
    time.sleep(PAGE_LOAD_WAIT)

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
    time.sleep(IFRAME_WAIT)
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
        time.sleep(IFRAME_WAIT)
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
            promo_input.send_keys(PROMO_CODE)
            print(f"  Entered promo code: {PROMO_CODE}")
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
        
        # Step 4: Select country as United States if dropdown appears
        print("\n=== Looking for country dropdown ===")
        country_selectors = [
            "//select[@id='N-homecountry']",
            "//select[@name='buyer.N-home.country']",
            "//select[contains(@class, 'eds-field-styled__select')]",
            "//select[@name='country']",
            "//select[contains(@id, 'country')]",
            "//select[contains(@aria-label, 'Country')]",
            "//select[contains(@class, 'country')]",
        ]
        
        country_selected = False
        for selector in country_selectors:
            try:
                elements = driver.find_elements(By.XPATH, selector)
                for element in elements:
                    if element.is_displayed():
                        try:
                            from selenium.webdriver.support.ui import Select
                            select = Select(element)
                            select.select_by_visible_text(COUNTRY)
                            print(f"  Selected '{COUNTRY}' from country dropdown.")
                            country_selected = True
                            break
                        except Exception as e:
                            print(f"  Could not select United States from dropdown: {e}")
                            continue
                if country_selected:
                    break
            except:
                continue
        
        if not country_selected:
            print("  No country dropdown found or could not select United States.")
        
        # Step 5: Extract form data from image and fill registration form
        print("\n=== Extracting form data and filling registration ===")
        
        # Extract form data from the specific image
        image_path = IMAGE_PATH
        extracted_text = read_image_info(image_path)
        form_data = extract_form_fields_from_image(image_path)
        
        if form_data:
            # Fill the registration form with extracted data
            fill_registration_form(driver, form_data)
        else:
            print("  No form data extracted from image.")
        
        # Print the raw text extracted from the image
        print("\n=== RAW TEXT EXTRACTED FROM IMAGE ===")
        print(extracted_text if extracted_text else "No text extracted.")
        
    else:
        print("No iframe found. Exiting.")
        driver.quit()
        exit()

    # Wait to see the final result
    time.sleep(FINAL_WAIT)

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    driver.quit()
    time.sleep(FINAL_WAIT)

def process_image_standalone():
    """Standalone function to process image without Eventbrite automation"""
    print("Simple Image Form Reader")
    print("=" * 30)
    
    # The specific image path
    image_path = IMAGE_PATH
    
    # Read image information
    extracted_text = read_image_info(image_path)
    
    if extracted_text:
        print("\n" + "=" * 50)
        print("EXTRACTED TEXT FROM IMAGE:")
        print("=" * 50)
        print(extracted_text)
        print("=" * 50)
        
        # Extract form fields with confidence
        print("\nExtracting form fields...")
        form_fields, confidence_scores = extract_form_fields(extracted_text)
        
        if form_fields:
            print("\n" + "=" * 50)
            print("EXTRACTED FORM FIELDS:")
            print("=" * 50)
            
            for field, value in form_fields.items():
                confidence = confidence_scores.get(field, 0.0)
                print(f"{field.replace('_', ' ').title()}: {value}")
                print(f"  Confidence: {confidence:.2f}")
                print()
            
            print("=" * 50)
            
            # Store in variables
            form_data = extracted_text
            extracted_fields = form_fields
            field_confidence = confidence_scores
            
            print(f"\n✅ Successfully extracted {len(form_fields)} fields!")
            print(f"📄 Full text stored in: form_data")
            print(f"📋 Form fields stored in: extracted_fields")
            print(f"🎯 Confidence scores stored in: field_confidence")
            
            # Calculate average confidence
            avg_confidence = sum(confidence_scores.values()) / len(confidence_scores) if confidence_scores else 0
            print(f"📊 Average confidence: {avg_confidence:.2f}")
            
        else:
            print("No form fields could be extracted.")
    else:
        print("Could not read image information.")

# Uncomment the line below to run standalone image processing instead of Eventbrite automation
# if __name__ == "__main__":
#     process_image_standalone()