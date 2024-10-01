import sys
import os
import pytest
from unittest.mock import patch, MagicMock

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
    with patch(
        "app.utils.load_plugins",
        return_value=(
            {plugin_name: {"scrape": MagicMock(return_value=expected_result)}},
            [],
        ),
    ):
        result = scrape_website("http://example.com", plugin_name)
        assert result == expected_result


@patch("smtplib.SMTP_SSL")
def test_send_email(mock_smtp):
    app = MagicMock()
    app.config = {
        "EMAIL_ADDRESS": "test@example.com",
        "RECIPIENT_EMAIL": "recipient@example.com",
        "EMAIL_PASSWORD": "password",
    }
    send_email("Test Subject", "Test Body", app)
    mock_smtp.assert_called_once()


if __name__ == "__main__":
    pytest.main()
