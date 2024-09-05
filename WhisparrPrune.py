import os
import requests
from datetime import datetime, timedelta
import logging
import argparse
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Constants
WHISPARR_BASEURL = os.getenv("WHISPARR_BASEURL")
if not WHISPARR_BASEURL:
    raise EnvironmentError("WHISPARR_BASEURL is not set in the environment")

SCENES_ENDPOINT = f"{WHISPARR_BASEURL}/api/v3/movie/list"
DELETE_ENDPOINT = f"{WHISPARR_BASEURL}/api/v3/movie/{{sceneID}}/?deleteFiles=true&addImportExclusion=true"
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
        response = requests.get(SCENES_ENDPOINT)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        error_logger.error(f"Failed to get scene IDs: {e}")
        return []

# Get scene details by scene ID
def get_scene_details(scene_ids):
    try:
        response = requests.post(BULK_ENDPOINT, json=scene_ids)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        error_logger.error(f"Failed to get scene details: {e}")
        return []

# Delete a scene by scene ID
def delete_scene(scene_id):
    try:
        response = requests.delete(DELETE_ENDPOINT.format(sceneID=scene_id))
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
def prune_scenes(dry_run):
    scene_ids = get_scene_ids()
    if not scene_ids:
        logging.error("No scenes found.")
        return

    two_weeks_ago = datetime.now() - timedelta(days=14)
    scenes_to_delete = []
    successful_deletes = 0
    failed_deletes = 0

    for i in range(0, len(scene_ids), 10):
        chunk = scene_ids[i:i+10]
        scene_details = get_scene_details(chunk)

        for scene in scene_details:
            release_date_str = scene.get("releaseDate", "")
            if release_date_str:
                release_date = datetime.strptime(release_date_str, "%Y-%m-%d")
                if release_date < two_weeks_ago:
                    scenes_to_delete.append(scene['id'])

    if dry_run:
        logging.info(f"[DRY RUN] Scenes older than 14 days: {scenes_to_delete}")
    else:
        for scene_id in scenes_to_delete:
            success = delete_scene(scene_id)
            if success:
                successful_deletes += 1
                logging.info(f"Successfully deleted scene ID {scene_id}")
            else:
                failed_deletes += 1
                logging.error(f"Failed to delete scene ID {scene_id}")

    logging.info(f"Processed {len(scenes_to_delete)} scenes. Successful deletes: {successful_deletes}, Failed deletes: {failed_deletes}")

# Command line argument parsing
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prune scenes from Whisparr older than 14 days.")
    parser.add_argument('--check', action='store_true', help="Perform a dry-run without deleting scenes.")
    args = parser.parse_args()

    prune_scenes(args.check)
