# Setup

> **Note**
> The following page is based on version `1.1.1` of BrickTracker.

## Prerequisites

Check your operating system documentation to install `docker` and `docker compose`.

## A note on environment variables

You need to pass the `BK_<name>` environment to your application, depending on how you run the application.
For instance:

- Docker: `docker run -e BK_<name>=xxxx`
- Docker compose (directly in `compose.yaml`):

```
services:
  bricktracker:
    environment:
      - BK_<name>=xxxx
```

- Docker compose (with an environement file, for instance `.env`)

```
-- .env
BK_<name>=xxxx

-- compose.yaml
services:
  bricktracker:
    env_file: ".env"
```

> **Warning**
> Do not use quotes (", ') around your environment variables.
> Docker will interpret them has being part of the **value** of the environment variable.
> For instance...
>
> ```
> services:
>  bricktracker:
>    environment:
>      - BK_AUTHENTICATION_KEY="xxxx"
> ```
>
> ...will make Docker believe that your API key is `"xxxx"`.

## Environment file and customization options

The [.env.sample](../.env.sample) file provides ample documentation on all the configurable options. Have a look at it.
You can make a copy of `.env.sample` as `.env` with your options or create an `.env` file from scratch.

[Environment Variables Reference](env.md) contains a table of the available variables.

## Database file

To accomodate for the original version of BrickTracker, the default database path is `./app.db`.
This is not ideal for a setup with volumes because it is a single file.
You can use a combination of a volume and the `BK_DATABASE_PATH` environment variable to accomodate for that.
For instance:

```
services:
  bricktracker:
    volumes:
      - database:/database/
    environment:
      BK_DATABASE_PATH: /database/app.db

volumes:
  database:
```

## Rebrickable API key

Although not mandatory for the application to run, it is necessary to add any data to the application.
It is set up with the `BK_REBRICKABLE_API_KEY` environment variable (or `REBRICKABLE_API_KEY` to accomodate for the original version of BrickTracker).

## Static image and instructions files folders

Since the images and instruction files are to be served by the webserver, it is expected they reside in the `/app/static` folder.
You can control the name/path of each image type relative to `app/static` with the `BK_*_FOLDER` variables.

## CSV files

Some CSV files are used to resolve informations like theme names or retired set dates.
In the original version of BrickTracker they were either shipped with the container or residing at the root of the application, meaning that any update to it would not survive a container update.

You can use the `BK_RETIRED_SET_PATH` and `BK_THEMES_PATH` to relocate them into a volume.

## Directory Structure

Updated directory structure showing data volume organization:
```
bricktracker/
├── data/                  # Persistent data
│   ├── app.db             # Database file
│   ├── retired_sets.csv   # Retired sets data
│   └── themes.csv         # Themes data
├── static/                # Static files
│   ├── instructions/      # PDF and other instruction files
│   ├── minifigures/       # Minifigure images
│   ├── parts/             # Part images
│   └── sets/              # Set images
├── .env                   # Environment configuration
└── compose.yaml     # Docker compose configuration
```

## Authentication

See [authentication](authentication.md)
