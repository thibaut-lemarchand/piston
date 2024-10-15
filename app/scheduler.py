import schedule
import time
from .models import check_updates, check_custom_updates

def run_scheduler(app):
    def run_check_updates():
        with app.app_context():
            check_updates()

    def run_check_custom_updates():
        with app.app_context():
            check_custom_updates()

    schedule.every().day.at("00:00").do(run_check_updates)
    schedule.every().day.at("00:00").do(run_check_custom_updates)

    while True:
        schedule.run_pending()
        time.sleep(1)
