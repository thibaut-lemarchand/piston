# Piston Job Search Assistant

## Overview
Piston is a job search assistant designed to automate the process of scraping job portals and sending email notifications when new job offers are found. Leveraging Flask, APScheduler, and a modular plugin system, it ensures flexibility and scalability in handling various job websites.

## Features
- **Automated Scraping**: Efficiently gathers job postings from multiple job websites.
-**Email Alerts**: Provides timely updates via email whenever new relevant job offers are detected
-**Modular Plugin System**: Supports default plugins for demonstration purposes and can be extended with custom plugins to scrape additional sources

## Getting Started
### Prerequisites:
- Python 3.12+
- Docker (optional, for containerized deployment)
- `uv` package manager for dependency management (can use `pipenv` or `poetry` instead)

### Installation
#### Using Docker:
1. Clone the repository
2. Build the Docker image
3. Run the Docker container

#### Using Command Line
1. Clone the repository
2. Install dependencies using your preferred package manager
3. Configure environment variables for database and email settings
4. Run the application in a development or production mode as needed

## Testing
### Integration Tests
Piston includes a comprehensive set of integration tests to ensure that the core functionalities of the web application and its interaction with the database are working seamlessly.

#### Running the Tests
- Ensure all necessary components and configurations are correctly set up.
- Execute the integration tests using `pytest`

```bash
pytest test/integration.py
```

### Unit Tests
For detailed unit testing, refer to the individual modules and components within the project

## Contributing
- Fork the repository on GitHub
- Create your feature branch (`git checkout -b feature/AmazingFeature`)
- Commit your changes (`git commit -m 'Add some AmazingFeature'`)
- Push to the branch (`git push origin feature/AmazingFeature`)
- Open a pull request

## License
Distributed under the MIT License. See `LICENSE` for more information.

## Contact
Your Name - [your_email@example.com](mailto:your_email@example.com)
Project Link: [https://github.com/your-repo/piston](https://github.com/your-repo/piston)

---

This README provides a general overview of the project, including how to get started and run tests. The integration tests section mentions that they exist for verifying the application's core functionalities without delving into specific code snippets.