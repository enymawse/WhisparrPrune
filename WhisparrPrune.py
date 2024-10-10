import os
import requests
from datetime import datetime, timedelta
import logging
import argparse
from dotenv import load_dotenv
from tqdm import tqdm  # Import the tqdm library for the progress bar

# Load environment variables from .env file
load_dotenv()

# Constants
WHISPARR_BASEURL = os.getenv("WHISPARR_BASEURL")
WHISPARR_APIKEY = os.getenv("WHISPARR_APIKEY")
if not WHISPARR_BASEURL or not WHISPARR_APIKEY:
    raise EnvironmentError("WHISPARR_BASEURL or WHISPARR_APIKEY is not set in the environment")

HEADERS_WHISPARR = {
    'X-Api-Key': WHISPARR_APIKEY,
    'Content-Type': 'application/json'
}

SCENES_ENDPOINT = f"{WHISPARR_BASEURL}/api/v3/movie/list"
DELETE_ENDPOINT = f"{WHISPARR_BASEURL}/api/v3/movie/{{sceneID}}/?deleteFiles=true&addImportExclusion=false"
BULK_ENDPOINT = f"{WHISPARR_BASEURL}/api/v3/movie/bulk"
LOG_FILE = "whisparr_prune.log"
ERROR_LOG_FILE = "whisparr_prune_error.log"

# Set up logging
logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
error_logger = logging.getLogger('error_logger')
error_handler = logging.FileHandler(ERROR_LOG_FILE)
error_handler.setLevel(logging.ERROR)
error_logger.addHandler(error_handler)

# Get the list of scene IDs from Whisparr
def get_scene_ids():
    try:
        response = requests.get(SCENES_ENDPOINT, headers=HEADERS_WHISPARR)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        error_logger.error(f"Failed to get scene IDs: {e}")
        return []

# Get scene details by scene ID
def get_scene_details(scene_ids):
    try:
        response = requests.post(BULK_ENDPOINT, json=scene_ids, headers=HEADERS_WHISPARR)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        error_logger.error(f"Failed to get scene details: {e}")
        return []

# Delete a scene by scene ID
def delete_scene(scene_id):
    try:
        response = requests.delete(DELETE_ENDPOINT.format(sceneID=scene_id), headers=HEADERS_WHISPARR)
        if response.status_code == 404:
            message = response.json().get('message')
            if f"Movie with ID {scene_id} does not exist" in message:
                error_logger.error(f"Scene with ID {scene_id} does not exist: {message}")
            else:
                error_logger.error(f"Error deleting scene: {message}")
            return False
        elif response.status_code == 200:
            return True
    except requests.exceptions.RequestException as e:
        error_logger.error(f"Failed to delete scene {scene_id}: {e}")
    return False

# Main function
def prune_scenes(dry_run, days):
    scene_ids = get_scene_ids()
    if not scene_ids:
        logging.error("No scenes found.")
        return

    days_ago = datetime.now() - timedelta(days=days)
    scenes_to_delete = []
    successful_deletes = 0
    failed_deletes = 0

    # Use tqdm for the progress bar
    with tqdm(total=len(scene_ids), desc="Processing scenes", unit="scene") as progress_bar:
        for i in range(0, len(scene_ids), 10000):
            chunk = scene_ids[i:i+10000]
            scene_details = get_scene_details(chunk)

            for scene in scene_details:
                release_date_str = scene.get("releaseDate", "")
                if release_date_str:
                    try:
                        if len(release_date_str) == 7:  # Format: YYYY-MM
                            release_date_str += "-01"  # Assume the first day of the month
                        release_date = datetime.strptime(release_date_str, "%Y-%m-%d")
                        if release_date < days_ago:
                            scenes_to_delete.append(scene['id'])
                    except ValueError:
                        if len(release_date_str) == 4:  # Format: YYYY
                            logging.error(f"Invalid date format: Only year provided for scene ID {scene['id']}, skipping.")
                        else:
                            logging.error(f"Invalid date format for scene ID {scene['id']}: {release_date_str}, skipping.")
            
            progress_bar.update(len(chunk))  # Update the progress bar by the size of the chunk processed

    if dry_run:
        logging.info(f"[DRY RUN] Scenes older than {days} days: {scenes_to_delete}")
    else:
        # Progress bar for deletion process
        with tqdm(total=len(scenes_to_delete), desc="Deleting scenes", unit="scene") as delete_bar:
            for scene_id in scenes_to_delete:
                success = delete_scene(scene_id)
                if success:
                    successful_deletes += 1
                    logging.info(f"Successfully deleted scene ID {scene_id}")
                else:
                    failed_deletes += 1
                    logging.error(f"Failed to delete scene ID {scene_id}")
                delete_bar.update(1)  # Update the progress bar for each deletion attempt

    logging.info(f"Processed {len(scenes_to_delete)} scenes. Successful deletes: {successful_deletes}, Failed deletes: {failed_deletes}")

# Command line argument parsing
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prune scenes from Whisparr older than the given number of days.")
    parser.add_argument('--check', action='store_true', help="Perform a dry-run without deleting scenes.")
    parser.add_argument('-d', '--days', type=int, default=14, help="Number of days to consider for deletion (default: 14 days).")
    args = parser.parse_args()

    prune_scenes(args.check, args.days)
