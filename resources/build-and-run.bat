docker build --tag librus-notifier .
docker rm librus-notifier
docker run -d -v /logs/:/logs/ --name librus-notifier librus-notifier