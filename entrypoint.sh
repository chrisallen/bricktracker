#!/usr/bin/env sh

# Host
if [ -z "$BK_HOST" ]
then
    export BK_HOST="0.0.0.0"
fi

# Port
if [ -z "$BK_PORT" ]
then
    export BK_PORT=3333
fi

# Execute the WSGI server
gunicorn --bind "${BK_HOST}:${BK_PORT}" "wsgi:application" --worker-class "gevent" --workers 1 "$@"
