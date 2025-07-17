import os
import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
import zipfile
from pathlib import Path

# Setup paths
downloads_dir = Path.home() / "Downloads"
image_folder = downloads_dir / "ti_rover_images"
zip_file = downloads_dir / "ti_rover_images.zip"
os.makedirs(image_folder, exist_ok=True)

def fetch_image_urls(search_url, keywords, limit=5):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    image_links = []

    for img in soup.find_all("img"):
        src = img.get("src") or img.get("data-src")
        if src and src.startswith("http") and any(k in src.lower() for k in keywords):
            image_links.append(src)
        if len(image_links) >= limit:
            break

    return image_links

# Define sources
sources = {
    "bing": {
        "url": "https://www.bing.com/images/search?q=TI+Innovator+Rover",
        "keywords": ["rover", "ti", "innovator"]
    },
    "duckduckgo": {
        "url": "https://duckduckgo.com/?q=TI+Innovator+Rover&iax=images&ia=images",
        "keywords": ["rover", "ti", "innovator"]
    }
}

# Download and convert to .webp
saved_images = []
img_index = 1

for name, config in sources.items():
    urls = fetch_image_urls(config["url"], config["keywords"], limit=10)
    for url in urls:
        try:
            response = requests.get(url, timeout=5)
            img = Image.open(BytesIO(response.content)).convert("RGB")

            if img.width >= 500 or img.height >= 500:
                webp_path = image_folder / f"{name}_rover_{img_index}.webp"
                img.save(webp_path, "WEBP", quality=90)
                saved_images.append(webp_path)
                img_index += 1

            if img_index > 10:
                break

        except Exception as e:
            print(f"Skipped {url}: {e}")

# Zip images
with zipfile.ZipFile(zip_file, "w") as zipf:
    for img_path in saved_images:
        zipf.write(img_path, arcname=img_path.name)

print(f"✅ Done! All images saved as .webp in ZIP: {zip_file}")
