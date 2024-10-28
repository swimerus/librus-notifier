import time
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler

from modules.librus_notifier import Notifier
from modules import utils


def notify():
    receivers = utils.get_config_entry('notifier_receivers')

    notifier = Notifier()
    notifier.check_for_messages()
    notifier.check_for_announcements()
    notifier.send_notification(receivers)

    print(f"{datetime.now()}: Notify function stops")


if __name__ == '__main__':
    checking_frequency_minutes = int(
        utils.get_config_entry('checking_frequency_minutes'))

    sched = BackgroundScheduler()
    sched.add_job(notify, 'interval', minutes=checking_frequency_minutes)
    sched.start()

    while True:
        time.sleep(1)
