# Whisparr Scene Pruning Script

## Overview

This script prunes scenes from Whisparr based on release date, with optional tag filtering. It can run in dry-run mode (`--check`) to preview deletions before making changes.

## Features

- Prune scenes older than a configurable number of days
- Optional tag filtering
- Dry-run mode for safe validation
- Progress bars for fetch/delete phases
- Separate success and error logs

## Requirements

- Python 3.x (for direct execution)
- Docker (for containerized execution)
- Whisparr API URL and API key

Python dependencies:

- `requests`
- `python-dotenv`
- `tqdm`

## Environment Variables

Copy `.env.example` to `.env`, then set your values:

```bash
cp .env.example .env
```

`.env` contents:

```env
WHISPARR_BASEURL=http://localhost:7878
WHISPARR_APIKEY=your_whisparr_api_key
```

## Run Directly (Python)

Install and run:

```bash
git clone https://github.com/enymawse/WhisparrPrune.git
cd WhisparrPrune
pip install -r requirements.txt
python WhisparrPrune.py --check -d 30
```

## Run in Docker

Build locally:

```bash
docker build -t whisparr-prune:local .
```

Dry-run example:

```bash
docker run --rm --env-file .env whisparr-prune:local --check -d 30
```

Live prune example:

```bash
docker run --rm --env-file .env whisparr-prune:local -d 30
```

Using Docker Compose:

```bash
docker compose run --rm whisparr-prune --check -d 30
```

Tag-filtered dry-run with Docker:

```bash
docker run --rm --env-file .env whisparr-prune:local --check -d 30 -t stashdb-favorite stashdb-favorite-performer
```

Tag-filtered dry-run with Docker Compose:

```bash
docker compose run --rm whisparr-prune --check -d 30 -t stashdb-favorite stashdb-favorite-performer
```

Configure tags in `compose.yaml`:

```yaml
command:
  - "-d"
  - "30"
  - "-t"
  - "stashdb-favorite"
  - "stashdb-favorite-performer"
```

## Container Publishing (GHCR)

This repo includes `.github/workflows/container-publish.yml` to build multi-arch images (`linux/amd64`, `linux/arm64`) and publish to:

`ghcr.io/enymawse/whisparrprune`

Automated flow:

- Pull requests to `main`: build only (no push)
- Pushes to `main`: run `semantic-release` using Conventional Commits
- If a release is created, publish image tags:
  - `vX.Y.Z`
  - `vX.Y`
  - `vX`
  - `latest`
  - `sha-<commit>`

Release config lives in `.releaserc.json`.

Conventional Commit impact:

- `fix:` -> patch release
- `feat:` -> minor release
- `feat!:` or `BREAKING CHANGE:` -> major release

Example commit messages:

- `fix: handle missing releaseDate values`
- `feat: add tag-based filtering examples`
- `feat!: change default prune behavior`

If you use squash merges, make sure the squash commit title also follows Conventional Commits, since that is what `semantic-release` reads on `main`.

## TrueNAS SCALE Scheduler Example

For a TrueNAS Cron Job command:

```bash
docker run --rm --env-file /mnt/<pool>/scripts/whisparrprune.env ghcr.io/enymawse/whisparrprune:latest -d 30 >> /mnt/<pool>/scripts/whisparrprune.log 2>&1
```

This keeps scheduling in TrueNAS and avoids running cron inside the container.

## Script Options

| Option         | Description                                |
| -------------- | ------------------------------------------ |
| `--check`      | Perform a dry-run without deleting scenes  |
| `-d`, `--days` | Days threshold for pruning (default: `14`) |
| `-t`, `--tags` | Optional tag labels to include for pruning |

If `--tags` is omitted, all scenes older than the threshold are considered.
To include multiple tags, pass each label as a separate value after `-t`.

## Logging

- Main log: `whisparr_prune.log`
- Error log: `whisparr_prune_error.log`

## Notes

- If a release date is `YYYY-MM`, the script assumes day `01`
- If a release date is only `YYYY`, the scene is skipped and logged as invalid
- Scenes are processed in batches of 10,000 IDs

## License

MIT. See `LICENSE`.
