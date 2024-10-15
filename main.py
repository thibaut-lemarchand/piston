from app import create_app, init_db, load_plugins, init_websites
from app.scheduler import run_scheduler
import threading

if __name__ == "__main__":
    app = create_app()
    init_db(app)
    plugins, websites_data = load_plugins()
    init_websites(app, websites_data)

    # Run the Flask app
    threading.Thread(target=run_scheduler, args=(app,), daemon=True).start()
    app.run(host="0.0.0.0", port=app.config["PORT"], debug=True)
