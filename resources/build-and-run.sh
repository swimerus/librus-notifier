#!/bin/sh
docker build --tag librus-notifier .
docker rm librus-notifier
docker run -d -v $PWD/logs:/usr/src/app/logs --restart unless-stopped --name librus-notifier librus-notifier