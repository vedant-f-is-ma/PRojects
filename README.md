# PRojects
Projects I do with api and stuff

## 🔄 Recent Updates

### Gemini 1.5 Flash API Integration
The main application (`AgeWellEventbriteLogin.py`) now uses **Gemini 1.5 Flash API** for intelligent form data extraction from images.

#### Key Benefits:
- ✅ **AI-Powered Extraction**: Uses Gemini 1.5 Flash for accurate text extraction
- ✅ **Structured Data**: Returns formatted field data (name, email, address, etc.)
- ✅ **Fast Processing**: Single API call extracts all form fields
- ✅ **Reliable**: No hardcoded fallbacks - pure AI extraction

#### Setup Required:
1. Get a Gemini API key from [Google AI Studio](https://aistudio.google.com/)
2. The API key is already configured in the code
3. Install dependencies: `pip install -r requirements.txt`
4. Run: `python AgeWellEventbriteLogin.py`

#### Features:
- **Selenium Web Automation**: Automated form filling
- **Gemini 1.5 Flash API**: Intelligent image text extraction
- **PDF Storage**: Automatic ticket download and storage
- **Comprehensive Form Handling**: All Eventbrite form fields supported
