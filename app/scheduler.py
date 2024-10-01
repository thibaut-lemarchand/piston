import schedule
import time
from .models import check_updates, check_custom_updates


def run_scheduler():
    schedule.every().day.at("00:00").do(check_updates)
    schedule.every().day.at("00:00").do(check_custom_updates)
    while True:
        schedule.run_pending()
        time.sleep(1)
