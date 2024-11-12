from flask_apscheduler import APScheduler
from piston import (
    create_app,
    init_db,
    load_plugins,
    init_websites,
    ensure_plugins_directory
)
from piston.scheduler import init_scheduler


if __name__ == "__main__":
    ensure_plugins_directory()

    app = create_app()
    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.start()

    init_db(app)
    plugins, websites_data = load_plugins()
    init_websites(app, websites_data)
    init_scheduler(app, scheduler)

    app.run(host="0.0.0.0", port=app.config["PORT"], debug=True)
