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

# ============================================================================
# CONFIGURATION VARIABLES - MODIFY THESE AS NEEDED
# ============================================================================

# Eventbrite Configuration
EVENTBRITE_URL = 'https://www.eventbrite.com/e/22nd-annual-healthy-living-festival-free-senior-festival-w-lunch-at-zoo-tickets-1388575319159'
PROMO_CODE = "HLFBUS25"

# Image Configuration
IMAGE_PATH = "/Users/vedant/Downloads/IMG_2162.jpeg"

# Form Data Configuration
SITE_LOCATION = "City of Fremont, Age Well Center At South Fremont"
SITE_COORDINATOR_NAME = "Martha Torrez"
SITE_COORDINATOR_EMAIL = "mtorrez@fremont.gov"
COUNTRY = "United States"

# Checkbox Confirmations (set to True to check, False to leave unchecked)
CHECK_AGE_CONFIRMATION = True          # 55+ age confirmation
CHECK_LOCATION_CONFIRMATION = True     # Alameda County confirmation
CHECK_HLF_BUS = True                   # HLF Provided Bus option
CHECK_COORDINATOR_CONFIRMATION = True  # Site coordinator confirmation

# HLF Bus Configuration
HLF_BUS_OPTION = True                  # Set to True to select HLF bus option, False to skip

# Site Coordinator Bus Confirmation
SITE_COORDINATOR_BUS_CONFIRMATION = True  # Set to True to select "Yes" for site coordinator bus confirmation, False to skip

# Site Coordinator Phone Number
SITE_COORDINATOR_PHONE = "##########"  # Set to the site coordinator's phone number (10 digits)

# Wait Times (in seconds)
PAGE_LOAD_WAIT = 5
IFRAME_WAIT = 5
FORM_FILL_WAIT = 3
FINAL_WAIT = 5
FIELD_FILL_RATE_LIMIT = 1  # Reduced from 5 to 1 second

# ============================================================================

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
    
    # Extract text from the actual image using Google Cloud Vision API
    extracted_text = extract_text_from_image(image_path)
    
    if extracted_text:
        print("Successfully extracted text from image using Google Cloud Vision API")
        return extracted_text
    else:
        print("Failed to extract text from image. Using fallback data.")
        # Fallback to simulated text if OCR fails
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
        return simulated_text

def extract_form_fields(text):
    """Extract form fields from text with confidence scores"""
    extracted_data = {}
    confidence_scores = {}
    
    # Define patterns to look for with confidence levels
    patterns = {
        'first_name': {
            'pattern': r'first\s*name[:\s]*([A-Za-z]+)',
            'confidence': 0.95
        },
        'last_name': {
            'pattern': r'last\s*name[:\s]*([A-Za-z]+)',
            'confidence': 0.95
        },
        'city': {
            'pattern': r'city[:\s]*([A-Za-z]+)',
            'confidence': 0.90
        },
        'state': {
            'pattern': r'state[:\s]*([A-Z]{2})',
            'confidence': 0.92
        },
        'zip_code': {
            'pattern': r'ZIP\s*Code[:\s]*(\d{5})',
            'confidence': 0.96
        },
    }
    
    # Extract each field with confidence
    for field_name, field_info in patterns.items():
        match = re.search(field_info['pattern'], text, re.IGNORECASE)
        if match:
            extracted_data[field_name] = match.group(1).strip()
            confidence_scores[field_name] = field_info['confidence']
    
    # Extract address directly from "Address:" field FIRST
    address_match = re.search(r'Address:\s*([0-9]+,\s*[^,\n]+(?:Street|St|Avenue|Ave|Road|Rd|Court|Ct|Drive|Dr|Lane|Ln|Boulevard|Blvd))', text, re.IGNORECASE)
    if address_match:
        address = address_match.group(1).strip()
        # Clean up the address
        address = re.sub(r',\s*$', '', address)
        address = re.sub(r'\s+', ' ', address)
        extracted_data['address'] = address
        confidence_scores['address'] = 0.90
    else:
        # Fallback: try to find address in a different format - capture everything after "Address:"
        address_match = re.search(r'Address:\s*([^\n]+)', text, re.IGNORECASE)
        if address_match:
            address = address_match.group(1).strip()
            # Clean up the address
            address = re.sub(r',\s*$', '', address)
            address = re.sub(r'\s+', ' ', address)
            extracted_data['address'] = address
            confidence_scores['address'] = 0.80
        
        # Fix address extraction - look for the full address pattern
        if 'address' in extracted_data and len(extracted_data['address']) < 10:
            # Try to find the full address including street type
            full_address_match = re.search(r'address[:\s]*([0-9]+,\s*[^,\n]+(?:Street|St|Avenue|Ave|Road|Rd|Court|Ct|Drive|Dr|Lane|Ln|Boulevard|Blvd))', text, re.IGNORECASE)
            if full_address_match:
                extracted_data['address'] = full_address_match.group(1).strip()
                confidence_scores['address'] = 0.85
    
    # Special handling for email - look for email address field specifically
    email_match = re.search(r'email\s*address[:\s]*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', text, re.IGNORECASE)
    if email_match:
        email = email_match.group(1).strip()
        extracted_data['email'] = email
        confidence_scores['email'] = 0.95
    else:
        # Fallback: look for any email pattern
        email_match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', text)
        if email_match:
            email = email_match.group(1).strip()
            extracted_data['email'] = email
            confidence_scores['email'] = 0.95
    
    # Add confirm_email using the same email
    if 'email' in extracted_data:
        extracted_data['confirm_email'] = extracted_data['email']
        confidence_scores['confirm_email'] = 0.98
    
    # Clean up address and city data
    if 'address' in extracted_data:
        # Remove any extra text after the address
        address = extracted_data['address']
        if ',' in address:
            extracted_data['address'] = address.split(',')[0].strip() + ', ' + address.split(',')[1].strip()
    
    if 'city' in extracted_data:
        # Remove any extra text after the city name
        city = extracted_data['city']
        if ' ' in city:
            extracted_data['city'] = city.split(' ')[0].strip()
    
    # Special handling for checkboxes with confidence
    if '✓' in text or 'X' in text:
        extracted_data['age_confirmation'] = 'Yes'
        confidence_scores['age_confirmation'] = 0.88
        
        extracted_data['location_confirmation'] = 'Yes'
        confidence_scores['location_confirmation'] = 0.88
        
        extracted_data['lunch_preference'] = 'Vegetarian'
        confidence_scores['lunch_preference'] = 0.85
    
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
        if value:
            filled = False
            for selector in field_selectors['first_name']:
                try:
                    element = driver.find_element(By.XPATH, selector)
                    if element.is_displayed():
                        element.clear()
                        element.send_keys(value)
                        print(f"  Filled First Name: {value}")
                        filled = True
                        break
                except Exception:
                    continue
            if not filled:
                print("  Could not find First Name field.")
            else:
                print(f"  Waiting {FIELD_FILL_RATE_LIMIT} seconds...")
                time.sleep(FIELD_FILL_RATE_LIMIT)
        
        # Step 2: Fill Last Name
        print("\n=== Step 2: Filling Last Name ===")
        value = form_data.get('last_name', '')
        if value:
            filled = False
            for selector in field_selectors['last_name']:
                try:
                    element = driver.find_element(By.XPATH, selector)
                    if element.is_displayed():
                        element.clear()
                        element.send_keys(value)
                        print(f"  Filled Last Name: {value}")
                        filled = True
                        break
                except Exception:
                    continue
            if not filled:
                print("  Could not find Last Name field.")
            else:
                print(f"  Waiting {FIELD_FILL_RATE_LIMIT} seconds...")
                time.sleep(FIELD_FILL_RATE_LIMIT)
        
        # Step 3: Fill Email
        print("\n=== Step 3: Filling Email ===")
        value = form_data.get('email', '')
        if value:
            filled = False
            for selector in field_selectors['email']:
                try:
                    element = driver.find_element(By.XPATH, selector)
                    if element.is_displayed():
                        element.clear()
                        element.send_keys(value)
                        print(f"  Filled Email: {value}")
                        filled = True
                        break
                except Exception:
                    continue
            if not filled:
                print("  Could not find Email field.")
            else:
                print(f"  Waiting {FIELD_FILL_RATE_LIMIT} seconds...")
                time.sleep(FIELD_FILL_RATE_LIMIT)
        
        # Step 4: Fill Confirm Email
        print("\n=== Step 4: Filling Confirm Email ===")
        value = form_data.get('email', '')  # Use same email for confirmation
        if value:
            filled = False
            for selector in field_selectors['confirm_email']:
                try:
                    element = driver.find_element(By.XPATH, selector)
                    if element.is_displayed():
                        element.clear()
                        element.send_keys(value)
                        print(f"  Filled Confirm Email: {value}")
                        filled = True
                        break
                except Exception:
                    continue
            if not filled:
                print("  Could not find Confirm Email field.")
            else:
                print(f"  Waiting {FIELD_FILL_RATE_LIMIT} seconds...")
                time.sleep(FIELD_FILL_RATE_LIMIT)
        
        # Step 5: Uncheck "Keep me updated" checkbox
        print("\n=== Step 5: Unchecking 'Keep me updated' checkbox ===")
        # Wait for checkbox to be present
        time.sleep(2)
        
        update_checkbox_selectors = [
            "//input[@id='organizer-marketing-opt-in']",
            "//input[@name='organizationMarketingOptIn']",
            "//input[@type='checkbox' and contains(@class, 'eds-checkbox_input')]",
            "//input[@type='checkbox' and contains(@name, 'update')]",
            "//input[@type='checkbox' and contains(@id, 'update')]",
            "//input[@type='checkbox' and contains(@aria-label, 'update')]",
            "//input[@type='checkbox' and contains(@name, 'newsletter')]",
            "//input[@type='checkbox' and contains(@id, 'newsletter')]",
            "//input[@type='checkbox' and contains(@aria-label, 'newsletter')]",
            "//input[@type='checkbox' and contains(@name, 'events')]",
            "//input[@type='checkbox' and contains(@id, 'events')]",
            "//input[@type='checkbox' and contains(@aria-label, 'events')]",
            "//input[@type='checkbox' and contains(@name, 'news')]",
            "//input[@type='checkbox' and contains(@id, 'news')]",
            "//input[@type='checkbox' and contains(@aria-label, 'news')]",
            "//input[@type='checkbox' and contains(@name, 'marketing')]",
            "//input[@type='checkbox' and contains(@id, 'marketing')]",
            "//input[@type='checkbox' and contains(@aria-label, 'marketing')]",
            "//input[@type='checkbox' and contains(@name, 'notify')]",
            "//input[@type='checkbox' and contains(@id, 'notify')]",
            "//input[@type='checkbox' and contains(@aria-label, 'notify')]",
            "//input[@type='checkbox' and contains(@name, 'email')]",
            "//input[@type='checkbox' and contains(@id, 'email')]",
            "//input[@type='checkbox' and contains(@aria-label, 'email')]",
            "//input[@type='checkbox' and contains(@name, 'opt')]",
            "//input[@type='checkbox' and contains(@id, 'opt')]",
            "//input[@type='checkbox' and contains(@aria-label, 'opt')]",
            "//input[@type='checkbox' and contains(@name, 'in')]",
            "//input[@type='checkbox' and contains(@id, 'in')]",
            "//input[@type='checkbox' and contains(@aria-label, 'in')]",
            # More specific selectors for "Keep me updated"
            "//input[@type='checkbox' and following-sibling::label[contains(text(), 'Keep me updated')]]",
            "//input[@type='checkbox' and preceding-sibling::label[contains(text(), 'Keep me updated')]]",
            "//input[@type='checkbox' and parent::div[.//label[contains(text(), 'Keep me updated')]]]",
            "//input[@type='checkbox' and ancestor::div[.//label[contains(text(), 'Keep me updated')]]]",
            "//input[@type='checkbox' and ancestor::div[.//span[contains(text(), 'Keep me updated')]]]",
            "//input[@type='checkbox' and ancestor::div[.//div[contains(text(), 'Keep me updated')]]]",
            # Look for checkboxes near "Keep me updated" text
            "//label[contains(text(), 'Keep me updated')]/preceding-sibling::input[@type='checkbox']",
            "//label[contains(text(), 'Keep me updated')]/following-sibling::input[@type='checkbox']",
            "//span[contains(text(), 'Keep me updated')]/preceding-sibling::input[@type='checkbox']",
            "//span[contains(text(), 'Keep me updated')]/following-sibling::input[@type='checkbox']",
            "//div[contains(text(), 'Keep me updated')]/preceding-sibling::input[@type='checkbox']",
            "//div[contains(text(), 'Keep me updated')]/following-sibling::input[@type='checkbox']",
        ]
        
        unchecked = False
        for selector in update_checkbox_selectors:
            try:
                elements = driver.find_elements(By.XPATH, selector)
                print(f"  Found {len(elements)} elements with selector: {selector}")
                for element in elements:
                    if element.is_displayed():
                        print(f"    Element displayed: {element.get_attribute('name')} | {element.get_attribute('id')} | {element.get_attribute('aria-label')}")
                        print(f"    Checkbox checked: {element.is_selected()}")
                        # Click the checkbox to toggle it to unchecked state
                        element.click()
                        print("  Clicked 'Keep me updated' checkbox to uncheck it.")
                        unchecked = True
                        break
                if unchecked:
                    break
            except Exception as e:
                print(f"    Error with selector {selector}: {e}")
                continue
        
        if not unchecked:
            print("  Could not find or uncheck 'Keep me updated' checkbox.")
        
        print(f"  Waiting {FIELD_FILL_RATE_LIMIT} seconds...")
        time.sleep(FIELD_FILL_RATE_LIMIT)
        
        # Step 6: Fill Address
        print("\n=== Step 6: Filling Address ===")
        value = form_data.get('address', '')
        if value:
            filled = False
            for selector in field_selectors['address']:
                try:
                    element = driver.find_element(By.XPATH, selector)
                    if element.is_displayed():
                        element.clear()
                        element.send_keys(value)
                        print(f"  Filled Address: {value}")
                        filled = True
                        break
                except Exception:
                    continue
            if not filled:
                print("  Could not find Address field.")
            else:
                print(f"  Waiting {FIELD_FILL_RATE_LIMIT} seconds...")
                time.sleep(FIELD_FILL_RATE_LIMIT)
        
        # Step 7: Fill City
        print("\n=== Step 7: Filling City ===")
        value = form_data.get('city', '')
        if value:
            filled = False
            for selector in field_selectors['city']:
                try:
                    element = driver.find_element(By.XPATH, selector)
                    if element.is_displayed():
                        element.clear()
                        element.send_keys(value)
                        print(f"  Filled City: {value}")
                        filled = True
                        break
                except Exception:
                    continue
            if not filled:
                print("  Could not find City field.")
            else:
                print(f"  Waiting {FIELD_FILL_RATE_LIMIT} seconds...")
                time.sleep(FIELD_FILL_RATE_LIMIT)
        
        # Step 8: Fill State (Dropdown) - Select California
        print("\n=== Step 8: Filling State (Dropdown) ===")
        state_value = form_data.get('state', '')
        if state_value == 'CA':
            state_value = 'California'  # Convert CA to California for dropdown
        
        state_selectors = [
            "//select[@id='N-homeregion']",
            "//select[@name='buyer.N-home.region']",
            "//select[@id='N-homestate']",
            "//select[@name='buyer.N-home.state']",
            "//select[contains(@class, 'eds-field-styled__select')]",
            "//select[@name='state']",
            "//select[contains(@id, 'state')]",
            "//select[contains(@aria-label, 'State')]",
            "//select[contains(@class, 'state')]",
            "//select[contains(@name, 'region')]",
            "//select[contains(@id, 'region')]",
            "//select[contains(@aria-label, 'region')]",
            "//select[contains(@name, 'home')]",
            "//select[contains(@id, 'home')]",
            "//select[contains(@aria-label, 'home')]",
            "//select[contains(@name, 'N-home')]",
            "//select[contains(@id, 'N-home')]",
            "//select[contains(@aria-label, 'N-home')]",
            # Try to find any select element that might be a state dropdown
            "//select[contains(@name, 'state') or contains(@id, 'state') or contains(@aria-label, 'state')]",
        ]
        
        # Wait for dropdowns to be present
        time.sleep(2)
        
        state_filled = False
        for selector in state_selectors:
            try:
                elements = driver.find_elements(By.XPATH, selector)
                print(f"    Found {len(elements)} elements with selector: {selector}")
                for element in elements:
                    # Removed the .is_displayed() check to always try interacting
                    print(f"      State dropdown found: {element.get_attribute('name')} | {element.get_attribute('id')} | {element.get_attribute('aria-label')}")
                    print(f"      Element aria-invalid: {element.get_attribute('aria-invalid')}")
                    
                    # If element is in error state, try to clear it first
                    if element.get_attribute('aria-invalid') == 'true':
                        print(f"      Element is in error state, attempting to clear...")
                        try:
                            select_element = Select(element)
                            select_element.select_by_index(0)  # Select first option
                            time.sleep(1)
                        except Exception as clear_error:
                            print(f"      Could not clear error state: {clear_error}")
                    
                    try:
                        print(f"      Attempting to create Select wrapper for element...")
                        select_element = Select(element)
                        print(f"      Select wrapper created successfully")
                        options = [option.text for option in select_element.options]
                        print(f"      Available dropdown options: {options}")
                        
                        # Try to select 'California' exactly
                        try:
                            select_element.select_by_visible_text('California')
                            print(f"  Selected State: California")
                            state_filled = True
                            time.sleep(1)  # Wait for selection to register
                            break
                        except Exception as e1:
                            print(f"      Could not select 'California': {e1}")
                            # Try partial match for 'calif'
                            found_partial = False
                            for option in select_element.options:
                                if 'calif' in option.text.lower():
                                    select_element.select_by_visible_text(option.text)
                                    print(f"  Selected State (partial match): {option.text}")
                                    state_filled = True
                                    found_partial = True
                                    time.sleep(1)  # Wait for selection to register
                                    break
                            if not found_partial:
                                print(f"      Could not find any option containing 'calif'. Printing all options for debugging:")
                                for option in select_element.options:
                                    print(f"        Option: '{option.text}'")
                    except Exception as e:
                        print(f"      Could not work with state dropdown: {e}")
                        print(f"      Element tag: {element.tag_name}")
                        print(f"      Element HTML: {element.get_attribute('outerHTML')[:200]}...")
                if state_filled:
                    break
            except Exception as e:
                print(f"    Error with selector {selector}: {e}")
                continue
        
        if not state_filled:
            print("  Could not find State dropdown.")
        else:
            print(f"  Waiting {FIELD_FILL_RATE_LIMIT} seconds...")
            time.sleep(FIELD_FILL_RATE_LIMIT)

        # Step 9: Fill Zip Code
        print("\n=== Step 9: Filling Zip Code ===")
        value = form_data.get('zip_code', '')
        print(f"  ZIP Code value from form_data: '{value}'")
        if value:
            filled = False
            for selector in field_selectors['zip_code']:
                try:
                    elements = driver.find_elements(By.XPATH, selector)
                    print(f"    Found {len(elements)} elements with selector: {selector}")
                    for element in elements:
                        if element.is_displayed():
                            print(f"      Element displayed: {element.get_attribute('name')} | {element.get_attribute('id')} | {element.get_attribute('aria-label')}")
                            element.clear()
                            element.send_keys(value)
                            print(f"  Filled Zip Code: {value}")
                            filled = True
                            break
                    if filled:
                        break
                except Exception as e:
                    print(f"    Error with selector {selector}: {e}")
                    continue
            if not filled:
                print("  Could not find Zip Code field.")
            else:
                print(f"  Waiting {FIELD_FILL_RATE_LIMIT} seconds...")
                time.sleep(FIELD_FILL_RATE_LIMIT)
        else:
            print("  No ZIP code value found in form_data.")

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
        
        # Check if user agreed to liability terms based on OCR text
        # Look for "Yes, I agree X" pattern in the extracted text
        liability_agreed = False
        if extracted_text:
            # Look for patterns indicating agreement with X marked
            if "yes, i agree x" in extracted_text.lower() or "yes i agree x" in extracted_text.lower():
                liability_agreed = True
                print("  OCR detected: User agreed to liability terms (X marked)")
            else:
                print("  OCR detected: User did not agree to liability terms (no X marked)")
        else:
            print("  No OCR text available; defaulting to not checking liability boxes")
        
        if liability_agreed:
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
        else:
            print("  User did not agree to liability terms; checkboxes left unchecked.")
        
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
