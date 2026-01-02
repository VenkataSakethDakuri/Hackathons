from google.adk.tools import FunctionTool
from google.adk.tools import ToolContext
from dotenv import load_dotenv, find_dotenv
from serpapi import GoogleSearch
import os
import requests
import asyncio
from pathlib import Path
import time

load_dotenv(find_dotenv())

count = 0


def download_image_with_retry(image_url: str, filepath: Path, max_retries: int = 3):
    """Downloads an image with retry logic for handling failures."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.get(image_url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                with open(filepath, "wb") as f:
                    f.write(response.content)
                print(f"Image saved to {filepath}")
                return True
            else:
                print(f"Download attempt {attempt + 1} failed (Status: {response.status_code})")
                
        except requests.exceptions.Timeout:
            print(f"Download attempt {attempt + 1} timed out")
        except requests.exceptions.ConnectionError:
            print(f"Download attempt {attempt + 1} connection error")
        except Exception as e:
            print(f"Download attempt {attempt + 1} error: {e}")
        
        if attempt < max_retries - 1:
            time.sleep(2 * (attempt + 1))  # Backoff
    
    return False


def image_tool(tool_context: ToolContext, topic: str):
    """Fetches image url for the required topic and downloads it. Returns the image url."""
    global count
    count += 1
    
    # Create save directory
    save_dir = Path(r"C:\Users\DELL\OneDrive\Desktop\Project\Hackathons\Acharya\images")
    save_dir.mkdir(parents=True, exist_ok=True)
    filepath = save_dir / f"image_{count}.jpg"

    # Get API key
    api_key = os.getenv("SERPAPI_API_KEY")
    if not api_key:
        print("SERPAPI_API_KEY not found in environment variables")
        return None

    params = {
        "engine": "google_images",
        "q": topic,
        "api_key": api_key
    }

    try:
        print(f"Searching for image: {topic}")
        search = GoogleSearch(params)
        results = search.get_dict()
        
        # Try multiple images in case some fail to download
        images_results = results.get("images_results", [])
        
        if not images_results:
            print(f"No image results found for: {topic}")
            return None
        
        # Try downloading from multiple sources
        for i, img_result in enumerate(images_results[:5]):  # Try up to 5 images
            image_url = img_result.get("original")
            if not image_url:
                continue
                
            print(f"Trying image source {i + 1}: {image_url[:80]}...")
            
            if download_image_with_retry(image_url, filepath):
                return image_url
        
        print(f"Failed to download any image for: {topic}")
        return None

    except KeyError as e:
        print(f"Data format error: Missing key {e}")
        return None
    except IndexError:
        print("List index error: Result list was empty.")
        return None
    except Exception as e:
        print(f"An error occurred while processing '{topic}': {e}")
        return None
