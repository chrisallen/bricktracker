# Development

> **Note**
> The following page is based on version `1.0.0` of BrickTracker.

The application is written in Python version 3.
It uses the following Python/pip packages:

- `flask` (Web framework)
- `flask_socketio` (Socket.IO: Websocket library for real-time client-server communication)
- `flask-login` (Lightweight Flask authentication library)
- `humanize` (Unit and datetime conversion)
- `sqlite3` (Light database management system)
- `rebrick` API (Library to interact with the Rebrickable.com API)

It also uses the following libraries and frameworks:

- Boostrap (https://getbootstrap.com/)
- Remixicon (https://remixicon.com/)
- `baguettebox` (https://github.com/feimosi/baguetteBox.js)
- `tinysort` (https://github.com/Sjeiti/TinySort)
- `sortable` (https://github.com/tofsjonas/sortable)
- `simple-datatables` (https://github.com/fiduswriter/simple-datatables)
- `vanillajs-datepicker` (https://github.com/mymth/vanillajs-datepicker)

The BrickTracker brick logo is part of the Small n' Flat Icons set designed by [Arnaud Chesne](https://iconduck.com/designers/arnaud-chesne).


## Running a local debug instance

You can use the [compose.local.yaml](../compose.local.yaml) file to build and run an instance with debug enabled and on a different port (`3334`).

```
$ mkdir local

$ docker compose -f compose.local.yaml build
[+] Building 0.6s (10/10) FINISHED                                                                                                         docker:default
 => [bricktracker internal] load build definition from Dockerfile                                                                                    0.0s
 => => transferring dockerfile: 211B                                                                                                                 0.0s
 => [bricktracker internal] load metadata for docker.io/library/python:3-slim                                                                        0.4s
 => [bricktracker internal] load .dockerignore                                                                                                       0.0s
 => => transferring context: 307B                                                                                                                    0.0s
 => [bricktracker 1/4] FROM docker.io/library/python:3-slim@sha256:23a81be7b258c8f516f7a60e80943cace4350deb8204cf107c7993e343610d47                  0.0s
 => [bricktracker internal] load build context                                                                                                       0.0s
 => => transferring context: 9.02kB                                                                                                                  0.0s
 => CACHED [bricktracker 2/4] WORKDIR /app                                                                                                           0.0s
 => CACHED [bricktracker 3/4] COPY . .                                                                                                               0.0s
 => CACHED [bricktracker 4/4] RUN pip --no-cache-dir install -r requirements.txt                                                                     0.0s
 => [bricktracker] exporting to image                                                                                                                0.0s
 => => exporting layers                                                                                                                              0.0s
 => => writing image sha256:5e913b01b10a51afae952187a45593d4c4a35635d084c8e9ba012476f21b2d0b                                                         0.0s
 => => naming to docker.io/library/bricktracker-bricktracker                                                                                         0.0s
 => [bricktracker] resolving provenance for metadata file                                                                                            0.0s

$ docker compose -f compose.local.yaml up -d
[+] Running 2/2
 ✔ Network bricktracker_default  Created                                                                                                             0.4s
 ✔ Container BrickTracker        Started                                                                                                            11.2s
```

You should have the app available on port `3334` (not `3333`!). For instance at http://127.0.0.1:3334.
