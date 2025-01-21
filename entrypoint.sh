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
gunicorn --bind "${BK_SERVER}:${BK_PORT}" "app:create_app()" --worker-class "eventlet" "$@"
