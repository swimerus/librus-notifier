FROM python:3.10.15-bullseye

RUN apt-get update && apt-get -y install cron

WORKDIR /usr/src/app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

RUN crontab crontab

CMD ["cron", "-f"]