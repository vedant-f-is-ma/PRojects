import google.generativeai as genai

# Put your API key here
API_KEY = ""

# Setup Gemini
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Image path
image_path = "/Users/vedant/Downloads/IMG_2162.jpeg"

# Read image
with open(image_path, 'rb') as image_file:
    image_data = image_file.read()

# Process image with single comprehensive prompt
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

response = model.generate_content([prompt, {"mime_type": "image/jpeg", "data": image_data}])
result = response.text

# Print results
print(result) 