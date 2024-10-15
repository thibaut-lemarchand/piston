import sys
import os
import pytest
from unittest.mock import patch, MagicMock
from flask import Flask

# Add the root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.utils import scrape_website, send_email  # Corrected import


@pytest.mark.parametrize(
    "plugin_name, expected_result",
    [
        (
            "test_plugin",
            {
                "link_count": 10,
                "links_with_descriptions": [("link1", "desc1"), ("link2", "desc2")],
            },
        )
    ],
)

def test_scrape_website(plugin_name, expected_result):
    mock_plugin = MagicMock()
    mock_plugin.scrape = MagicMock(return_value=expected_result)

    with patch(
        "app.utils.load_plugins",
        return_value=({plugin_name: mock_plugin}, []),
    ):
        result = scrape_website("http://example.com", plugin_name)
        assert result == expected_result


# @patch("smtplib.SMTP_SSL")
# def test_send_email(mock_smtp):
#     # Create a Flask app instance
#     app = Flask(__name__)
#     app.config["EMAIL_ADDRESS"] = "test@example.com"
#     app.config["RECIPIENT_EMAIL"] = "recipient@example.com"
#     app.config["EMAIL_PASSWORD"] = "password"

#     # Create a mock SMTP instance
#     smtp_instance = mock_smtp.return_value

#     # Run the test within an app context
#     with app.app_context():
#         # Now call the send_email function
#         send_email("Test Subject", "Test Body")

#     # Assertions
#     mock_smtp.assert_called_once_with("smtp.gmail.com", 465)
#     smtp_instance.login.assert_called_once_with("test@example.com", "password")
#     smtp_instance.send_message.assert_called_once()


if __name__ == "__main__":
    pytest.main()
