# Whisparr Scene Pruning Script

## Overview

This Python script is designed to prune scenes from a Whisparr instance based on their release date. It interacts with the Whisparr API to identify and delete scenes older than a specified number of days. The script can also perform a dry-run where no deletions are made, allowing you to verify which scenes would be deleted.

## Features

- **Prune Scenes by Release Date**: Deletes scenes older than a user-specified number of days.
- **Dry-Run Mode**: Allows you to check which scenes would be deleted without actually deleting them.
- **Progress Tracking**: Uses a progress bar to track the progress of both scene processing and deletion.
- **Logging**: Logs actions, errors, and results to log files for easy troubleshooting and auditing.

## Requirements

- Python 3.x
- The following Python libraries:
  - `requests`
  - `tqdm`
  - `python-dotenv`

Install these dependencies via pip:

```bash
git clone https://github.com/enymawse/WhisparrPrune.git && \
cd WhisparrPrune && \
pip install -r requirements.txt
```

## Setup

1. **Whisparr API Key and Base URL**:

   - You must provide your Whisparr API base URL and API key through environment variables. Create a `.env` file in the same directory as the script with the following content:

   ```env
   WHISPARR_BASEURL=http://localhost:7878
   WHISPARR_APIKEY=your_whisparr_api_key
   ```

2. **Logging**:
   - The script logs its operations to `whisparr_prune.log`.
   - Errors are logged separately in `whisparr_prune_error.log`.

## Usage

Run the script from the command line, specifying the number of days after which scenes should be pruned.

### Command Line Options

- **`--check`**: Perform a dry-run without actually deleting scenes. Use this to verify what would be deleted.
- **`-d`, `--days`**: Specify the number of days (default is 14 days). Any scenes older than this will be deleted.

### Examples

1. **Dry-Run Mode (Check which scenes would be deleted)**:

   ```bash
   python whisparr_prune.py --check -d 30
   ```

   This will list scenes older than 30 days without deleting them.

2. **Prune Scenes Older Than 14 Days (Default)**:

   ```bash
   python whisparr_prune.py
   ```

   This will prune all scenes older than 14 days.

3. **Prune Scenes Older Than 60 Days**:
   ```bash
   python whisparr_prune.py -d 60
   ```

## How It Works

1. **Fetching Scene IDs**:

   - The script retrieves a list of all scene IDs from your Whisparr instance using the `/api/v3/movie/list` endpoint.

2. **Filtering Scenes by Release Date**:

   - For each scene, the release date is checked against the provided threshold (e.g., 14 days ago).
   - Scenes that are older than the threshold are marked for deletion.

3. **Deleting Scenes**:

   - In live mode (non-dry-run), the script deletes each scene using the `/api/v3/movie/{sceneID}` endpoint.
   - If a scene cannot be deleted, an error is logged in `whisparr_prune_error.log`.

4. **Progress Bars**:
   - Two progress bars are displayed: one for scene processing and another for the deletion process.

## Logs

- **Main Log (`whisparr_prune.log`)**:
  - Contains details about successfully processed and deleted scenes.
- **Error Log (`whisparr_prune_error.log`)**:
  - Logs any errors encountered, including issues with API requests or date formatting.

## Notes

- **Date Handling**: The script assumes the first day of the month if the release date only provides the year and month (`YYYY-MM`). If only the year is provided (`YYYY`), the script logs an error and skips that scene.
- **Batch Processing**: The script processes scenes in batches of 10,000 to optimize the number of API requests.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

If you have any questions or need further assistance, feel free to reach out.
