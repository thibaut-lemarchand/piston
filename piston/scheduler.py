from datetime import datetime, timedelta
from piston.models import Website, CustomWebsite, check_updates, check_custom_updates, db

def init_scheduler(app, scheduler):
    @scheduler.task('interval', id='check_all_updates', seconds=30)
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
                print(f"Updating {website.name} ({website.scrape_interval})")
                check_updates(website)
            else:
                print(f"Updating custom {website.name} ({website.scrape_interval})")
                check_custom_updates(website)
            website.last_checked = now
            db.session.commit()

def should_scrape(website, now):

    if website.last_checked is None:
        return True
    
    interval = website.scrape_interval
    print(website.name, (now - website.last_checked))

    if interval == 'never':
        return False
    elif interval == 'daily':
        return (now - website.last_checked) > timedelta(days=1)
    elif interval == 'hourly':
        return (now - website.last_checked) > timedelta(hours=1)
    elif interval == '5min':
        return (now - website.last_checked) > timedelta(minutes=5)
    
    return False