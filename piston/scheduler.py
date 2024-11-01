from datetime import datetime, timedelta
from piston.models import Website, update_website, db

SCRAPE_INTERVALS = {
    'never': timedelta(days=9999),  # effectively never
    '5min': timedelta(minutes=5),
    '30min': timedelta(minutes=30),
    '1hour': timedelta(hours=1),
    '2hours': timedelta(hours=2),
    '12hours': timedelta(hours=12),
    '1day': timedelta(days=1),
    '1week': timedelta(weeks=1)
}

def init_scheduler(app, scheduler):
    @scheduler.task('interval', id='check_all_updates', seconds=30)
    def scheduled_check_all_updates():
        with app.app_context():
            check_all_websites()

def check_all_websites():
    now = datetime.now()
    websites = Website.query.all()
    
    for website in websites:
        if should_scrape(website, now):
            if isinstance(website, Website):
                print(f"{now} - Updating {website.name} ({website.scraping_type} - {website.scrape_interval})")
                update_website(website)

            website.last_checked = now
            db.session.commit()
            
    # Fetch updated data and update the frontend
    fetch_updated_data()

def should_scrape(website, now):
    if website.last_checked is None:
        return True
    
    interval = website.scrape_interval
    return SCRAPE_INTERVALS.get(interval, timedelta(days=9999)) <= (now - website.last_checked)

def should_scrape(website, now):
    if website.last_checked is None:
        return True
    
    interval = website.scrape_interval

    if interval == 'never':
        return False
    elif interval == 'daily':
        return (now - website.last_checked) > timedelta(days=1)
    elif interval == 'hourly':
        return (now - website.last_checked) > timedelta(hours=1)
    elif interval == '5min':
        return (now - website.last_checked) > timedelta(minutes=5)
    
    return False

def fetch_updated_data():
    updated_websites = Website.query.all()
    updated_data = []
    for website in updated_websites:
        updated_data.append({
            'id': website.id,
            'name': website.name,
            'url': website.url,
            'last_checked': website.last_checked.strftime('%Y-%m-%d %H:%M:%S') if website.last_checked else None,
        })
    
    return updated_data
