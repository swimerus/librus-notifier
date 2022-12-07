# LIBRUS-NOTIFIER
MVP app that checks Librus for new messages (AKA wiadomości) and announcements (AKA ogłoszenia) and sends email notifications. App uses [librus-api-python](https://github.com/findepi/librus-api-python).  
While starting the app, a simple schedule is created that checks for news and sends notofications in a given period of time.

## Configuring the app
See file `resources/config.json`.
All params are pretty self-explaining.

## Running the app
### Linux
    sh resources/build-and-run.sh
### Windows
    resources/build-and-run.bat
