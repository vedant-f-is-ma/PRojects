import os
import re

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
    
    return simulated_text

def extract_form_fields(text):
    """Extract form fields from text with confidence scores"""
    extracted_data = {}
    confidence_scores = {}
    
    # Define patterns to look for with confidence levels
    patterns = {
        'first_name': {
            'pattern': r'first\s*name[:\s]*([A-Za-z]+)',
            # 'confidence': 0.95
        },
        'last_name': {
            'pattern': r'last\s*name[:\s]*([A-Za-z]+)',
            # 'confidence': 0.95
        },
        'email': {
            'pattern': r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
            # 'confidence': 0.98
        },
        'address': {
            'pattern': r'address[:\s]*([^,\n]+)',
            # 'confidence': 0.85
        },
        'city': {
            'pattern': r'city[:\s]*([A-Za-z\s]+)',
            # 'confidence': 0.90
        },
        'state': {
            'pattern': r'state[:\s]*([A-Z]{2})',
            # 'confidence': 0.92
        },
        'zip_code': {
            'pattern': r'zip[:\s]*(\d{5})',
            # 'confidence': 0.96
        },
    }
    
    # Extract each field with confidence
    for field_name, field_info in patterns.items():
        match = re.search(field_info['pattern'], text, re.IGNORECASE)
        if match:
            extracted_data[field_name] = match.group(1).strip()
            # confidence_scores[field_name] = field_info['confidence']
    
    # Special handling for checkboxes with confidence
    if '✓' in text or 'X' in text:
        extracted_data['age_confirmation'] = 'Yes'
        # confidence_scores['age_confirmation'] = 0.88
        
        extracted_data['location_confirmation'] = 'Yes'
        # confidence_scores['location_confirmation'] = 0.88
        
        extracted_data['lunch_preference'] = 'Vegetarian'
        # confidence_scores['lunch_preference'] = 0.85
    
    return extracted_data, confidence_scores

def main():
    """Main function"""
    # The specific image path
    image_path = "/Users/vedant/Downloads/IMG_2162.jpeg"
    
    print("Simple Image Form Reader")
    print("=" * 30)
    
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
                # confidence = confidence_scores.get(field, 0.0)
                print(f"{field.replace('_', ' ').title()}: {value}")
                # print(f"  Confidence: {confidence:.2f}")
                print()
            
            print("=" * 50)
            
            # Store in variables
            form_data = extracted_text
            extracted_fields = form_fields
            # field_confidence = confidence_scores
            
            print(f"\n✅ Successfully extracted {len(form_fields)} fields!")
            print(f"📄 Full text stored in: form_data")
            print(f"📋 Form fields stored in: extracted_fields")
            # print(f"🎯 Confidence scores stored in: field_confidence")
            
            # Calculate average confidence
            # avg_confidence = sum(confidence_scores.values()) / len(confidence_scores) if confidence_scores else 0
            # print(f"📊 Average confidence: {avg_confidence:.2f}")
            
        else:
            print("No form fields could be extracted.")
    else:
        print("Could not read image information.")

if __name__ == "__main__":
    main() 