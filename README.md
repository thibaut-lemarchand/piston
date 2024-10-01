# Job Offer Update Checker

## Overview
The **Job Offer Update Checker** is a powerful Python-based application designed to monitor job offer websites for updates. It leverages Flask for the web interface, SQLite for efficient database management, and a flexible plugin system for scraping various job sites. This tool empowers users to stay on top of the latest job postings by automating the monitoring process and providing timely notifications.

## Key Features

- **Automated Job Site Monitoring**: Regularly checks configured job websites for new or updated listings based on user-defined intervals.
- **Manual Scraping**: Allows users to trigger immediate scrapes of specific job sites on demand.
- **Customizable Scrape Intervals**: Users can fine-tune the frequency of checks for each monitored website.
- **Email Notifications**: Sends alerts when new job offers or updates are detected.
- **Extensible Plugin System**: Supports custom plugins for scraping different job boards and websites.
- **User-Friendly Web Interface**: Easy-to-use Flask-based frontend for managing monitored sites and viewing results.

## Installation

### Prerequisites

- Python 3.7+
- Docker (optional, for containerized deployment)
- Git (for cloning the repository)

### Installation Steps

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/job-offer-update-checker.git
   cd job-offer-update-checker
   ```

2. **Set Up the Python Environment**:
   
   This project uses Poetry for dependency management. However, if you encounter issues with Poetry and venv compatibility, you can use a traditional venv setup:

   Using Poetry (recommended):
   ```bash
   poetry install
   poetry shell
   ```

   Alternative method using venv:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   pip install -r requirements.txt
   ```

   Note: If using the venv method, ensure you have a `requirements.txt` file in your project root.

3. **Configure the Application**:
   - Copy the example configuration file:
     ```bash
     cp config.example.yml config.yml
     ```
   - Edit `config.yml` to set up your email notifications and database preferences.

4. **Initialize the Database**:
   ```bash
   python manage.py init_db
   ```

5. **Run the Application**:
   ```bash
   python app.py
   ```

   The application will be available at `http://localhost:5000`.

## Usage

1. Access the web interface at `http://localhost:5000`.
2. Add job websites you want to monitor using the "Add Website" feature.
3. Configure scraping intervals for each website.
4. Use the "Manual Scrape" button to immediately check a website for updates.
5. View the latest job offers and updates in the dashboard.

## Development

### Adding New Plugins

To create a plugin for a new job website:

1. Create a new Python file in the `plugins/` directory.
2. Implement the required scraping logic, following the existing plugin structure.
3. Register your new plugin in `plugins/__init__.py`.

### Running Tests

Execute the test suite using:

```bash
pytest
```

## Deployment

For production deployment, consider using Docker:

```bash
docker build -t job-offer-update-checker .
docker run -p 5000:5000 job-offer-update-checker
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.