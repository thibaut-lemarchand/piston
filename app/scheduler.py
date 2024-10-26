from datetime import datetime, timedelta
from .models import Website, CustomWebsite, check_updates, check_custom_updates, db

def init_scheduler(app, scheduler):
    @scheduler.task('interval', id='check_all_updates', minutes=1)
    def scheduled_check_all_updates():
        with app.app_context():
            print('Checking all sites for updates')
            check_all_websites()

def check_all_websites():
    now = datetime.now()
    websites = Website.query.filter_by(is_enabled=True).all()
    custom_websites = CustomWebsite.query.all()
    
    for website in websites + custom_websites:
        if should_scrape(website, now):
            if isinstance(website, Website):
                check_updates(website)
            else:
                check_custom_updates(website)
            website.last_checked = now
            db.session.commit()

def should_scrape(website, now):
    # if website.last_checked is None:
    #     return True
    
    interval = website.scrape_interval
    print(website.name, website.scrape_interval)

    if interval == 'never':
        return False
    elif interval == 'daily':
        return (now - website.last_checked) > timedelta(days=1)
    elif interval == 'hourly':
        return (now - website.last_checked) > timedelta(hours=1)
    elif interval == '5min':
        print("update")
        return (now - website.last_checked) > timedelta(minutes=1)
    # Add more intervals as needed
    
    return False