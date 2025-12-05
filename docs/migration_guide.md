# Data Folder Migration Guide (Docker Compose)

## Overview

Starting with version 1.3, BrickTracker consolidates all user data into a single `data/` folder for easier backup, persistence, and volume mapping.

**This guide assumes you are running BrickTracker using Docker Compose with bind mounts.**

> **Note:** If you're using Docker named volumes instead of bind mounts, you'll need to manually copy data between volumes. The commands below are specific to bind mount setups.

**Backup your data before to making any changes!**

## What Changed?

### New Default Structure (v1.3+)

**All relative paths are resolved relative to `/app` inside the container.** Previously all paths were relative to `/app/static`. 

For example: `data/app.db` → `/app/data/app.db`

```
Container (/app/):
├── data/                   # NEW: Single volume mount for all user data
│   ├── app.db              # Database
│   ├── retired_sets.csv    # Downloaded CSV files
│   ├── themes.csv
│   ├── sets/               # Set images
│   ├── parts/              # Part images
│   ├── minifigures/        # Minifigure images
│   └── instructions/       # PDF instructions
└── static/                  # App assets
    ├── brick.png
    ├── styles.css
    └── scripts/
```

**Docker Compose volume:** Single mount `./data:/app/data/`

### Previous Structure (v1.2 and earlier)

```
Container (/app/):
├── app.db                   # Mounted from ./data/ on host
├── retired_sets.csv         # Mounted from ./data/ on host
├── themes.csv
└── static/
    ├── instructions/       # Separate bind mount
    ├── minifigures/        # Separate bind mount
    ├── parts/              # Separate bind mount
    ├── sets/               # Separate bind mount
```

**Docker Compose bind mounts:** 5 separate mounts
```yaml
volumes:
  - ./data:/app/
  - ./instructions:/app/static/instructions/
  - ./minifigures:/app/static/minifigures/
  - ./parts:/app/static/parts/
  - ./sets:/app/static/sets/
```

## Migration Options

### Option 1: Migrate to New Data Folder Structure (Recommended)

This is the recommended approach for cleaner backups and simpler bind mount management.

1. **Stop the container:**
   ```bash
   docker compose down
   ```

2. **Create new consolidated data directory on host:**
   ```bash
   mkdir -p ./bricktracker-data/{sets,parts,minifigures,instructions}
   ```

3. **Move data from old bind mount locations to new structure:**

   Assuming your old `compose.yaml` had:
   - `./data:/app/` (contains app.db, retired_sets.csv, themes.csv)
   - `./instructions:/app/static/instructions/`
   - `./minifigures:/app/static/minifigures/`
   - `./parts:/app/static/parts/`
   - `./sets:/app/static/sets/`

   Run:
   ```bash
   # Move database and CSV files
   mv ./data/app.db ./bricktracker-data/
   mv ./data/retired_sets.csv ./bricktracker-data/
   mv ./data/themes.csv ./bricktracker-data/ 

   # Move image and instruction folders
   mv ./instructions/* ./bricktracker-data/instructions/
   mv ./minifigures/* ./bricktracker-data/minifigures/
   mv ./parts/* ./bricktracker-data/parts/
   mv ./sets/* ./bricktracker-data/sets/
   ```

4. **Update `compose.yaml` to use single bind mount:**
   ```yaml
   services:
     bricktracker:
       volumes:
         - ./bricktracker-data:/app/data/

   # Remove old volume mounts
   ```

5. **Remove old environment overrides from `.env` (if present):**
   Delete any lines starting with:
   - `BK_DATABASE_PATH=`
   - `BK_INSTRUCTIONS_FOLDER=`
   - `BK_MINIFIGURES_FOLDER=`
   - `BK_PARTS_FOLDER=`
   - `BK_SETS_FOLDER=`
   - `BK_RETIRED_SETS_PATH=`
   - `BK_THEMES_PATH=`

6. **Start the container:**
   ```bash
   docker compose up -d
   ```

7. **Verify everything works:**
   ```bash
   docker compose logs -f bricktracker
   # Check the web interface to ensure images/data are loading
   ```

8. **Clean up old directories (after verification):**
   ```bash
   rm -r ./data ./instructions ./minifigures ./parts ./sets
   ```

### Option 2: Keep Current Setup (No Data Migration)

If you want to keep your current volume structure without moving any files:

1. **Add these environment variables to your `.env` file:**

   ```env
   # Keep database and CSV files in /data volume (old location)
   BK_DATABASE_PATH=app.db
   BK_RETIRED_SETS_PATH=retired_sets.csv
   BK_THEMES_PATH=themes.csv

   # Keep image/instruction folders in static/ (old location)
   BK_INSTRUCTIONS_FOLDER=static/instructions
   BK_MINIFIGURES_FOLDER=static/minifigures
   BK_PARTS_FOLDER=static/parts
   BK_SETS_FOLDER=static/sets
   ```

2. **Keep your existing volume mounts in `compose.yaml`:**

   ```yaml
   volumes:
     - ./data:/app/
     - ./instructions:/app/static/instructions/
     - ./minifigures:/app/static/minifigures/
     - ./parts:/app/static/parts/
     - ./sets:/app/static/sets/
   ```

3. **Update to v1.3 and restart:**
   ```bash
   docker compose pull
   docker compose up -d
   ```

That's it! Your existing setup will continue to work.

## Configuration Reference

### New Default Paths (v1.3+)

All paths are relative to `/app` inside the container.

| Config Variable | Default Value | Resolves To (Container) | Description |
|----------------|---------------|------------------------|-------------|
| `BK_DATABASE_PATH` | `data/app.db` | `/app/data/app.db` | Database file |
| `BK_RETIRED_SETS_PATH` | `data/retired_sets.csv` | `/app/data/retired_sets.csv` | Retired sets CSV |
| `BK_THEMES_PATH` | `data/themes.csv` | `/app/data/themes.csv` | Themes CSV |
| `BK_INSTRUCTIONS_FOLDER` | `data/instructions` | `/app/data/instructions` | PDF instructions |
| `BK_MINIFIGURES_FOLDER` | `data/minifigures` | `/app/data/minifigures` | Minifigure images |
| `BK_PARTS_FOLDER` | `data/parts` | `/app/data/parts` | Part images |
| `BK_SETS_FOLDER` | `data/sets` | `/app/data/sets` | Set images |

**Docker Compose bind mount:** `./bricktracker-data:/app/data/` (single mount)

### Old Paths (v1.2 and earlier)

To preserve old volume structure without migration, add to `.env`:

| Config Variable | Value to Preserve Old Behavior | Resolves To (Container) |
|----------------|-------------------------------|------------------------|
| `BK_DATABASE_PATH` | `app.db` | `/app/app.db` |
| `BK_RETIRED_SETS_PATH` | `retired_sets.csv` | `/app/retired_sets.csv` |
| `BK_THEMES_PATH` | `themes.csv` | `/app/themes.csv` |
| `BK_INSTRUCTIONS_FOLDER` | `static/instructions` | `/app/static/instructions` |
| `BK_MINIFIGURES_FOLDER` | `static/minifigures` | `/app/static/minifigures` |
| `BK_PARTS_FOLDER` | `static/parts` | `/app/static/parts` |
| `BK_SETS_FOLDER` | `static/sets` | `/app/static/sets` |

## Benefits of New Structure

1. **Single Bind Mount**: One `./bricktracker-data:/app/data/` mount instead of five separate mounts
2. **Easier Backups**: All user data in one location - just backup the `bricktracker-data` directory
3. **Cleaner Separation**: User data separated from application assets
4. **Better Portability**: Migrate between systems by copying/moving single directory

## Troubleshooting

### Images/Instructions Not Loading After Migration

1. **Check if data was copied correctly:**
   ```bash
   docker compose exec bricktracker ls -la /app/data/
   docker compose exec bricktracker ls -la /app/data/sets/
   docker compose exec bricktracker ls -la /app/data/instructions/
   ```

2. **Verify bind mount:**
   ```bash
   docker compose config
   # Should show: volumes: - ./bricktracker-data:/app/data/
   ```

3. **Check logs for path errors:**
   ```bash
   docker compose logs -f
   ```

4. **Verify no old environment overrides:**
   ```bash
   cat .env | grep BK_
   ```

### Database Not Found

1. **Check database file location in container:**
   ```bash
   docker compose exec bricktracker ls -la /app/data/app.db
   ```

2. **If using old setup, verify environment variables:**
   ```bash
   docker compose exec bricktracker env | grep BK_DATABASE_PATH
   ```

3. **Check host directory contains database:**
   ```bash
   ls -la ./bricktracker-data/
   # Should show: app.db, retired_sets.csv, themes.csv, and subdirectories
   ```

### Permission Errors

If you see permission errors after migration:

```bash
# Fix permissions on bind-mounted directory
sudo chown -R $(id -u):$(id -g) ./bricktracker-data
```

### Reverting Migration

If you need to revert to the old structure:

1. Stop the container: `docker compose down`
2. Restore old `compose.yaml` with 5 volume mounts
3. Add old path environment variables to `.env` (see Option 1)
4. Start: `docker compose up -d`
