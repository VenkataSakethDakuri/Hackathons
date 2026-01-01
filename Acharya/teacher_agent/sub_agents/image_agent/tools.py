from google.adk.tools import FunctionTool
from google.adk.tools import ToolContext
from dotenv import load_dotenv, find_dotenv
from serpapi import GoogleSearch
import os
import requests
import asyncio
from pathlib import Path
load_dotenv(find_dotenv())

count = 0

def download_image(image_url: str, save_dir: str = "images"):
    """Downloads an image from the given URL and saves it to the specified directory."""
    global count
    count += 1
    
    save_path = Path(save_dir)
    save_path.mkdir(parents=True, exist_ok=True)
    
    filepath = save_path / f"image_{count}.jpg"
    
    response = requests.get(image_url)
    if response.status_code == 200:
        with open(filepath, "wb") as f:
            f.write(response.content)
        print(f"Saved to {filepath}")
    else:
        print("Failed to download image")


def image_tool(tool_context: ToolContext, topic: str):
    """ Fetches image url for the required topic and downloads it"""

    params = {
    "engine": "google_images",
    "q": topic,
    "api_key": os.getenv("SERPAPI_API_KEY")
    }

    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        images_url = results["images_results"][0]["original"]
        download_image(images_url, r"C:\Users\DELL\OneDrive\Desktop\Project\Hackathons\Acharya\images")

    except KeyError as e:
        print(f"Data format error: Missing key {e}")
        return None
    except IndexError:
        print("List index error: Result list was empty.")
        return None
    except Exception as e:
        # Catches network errors, API errors, or file permission errors
        print(f"An error occurred while processing '{topic}': {e}")
        return None

    return images_url




    
    


