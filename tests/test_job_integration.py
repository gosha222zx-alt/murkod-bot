import os
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

from app.integrations import load_job_items


class TestJobIntegration(unittest.TestCase):
    def test_load_job_items_filters_by_keywords(self):
        feed_xml = b"""
        <rss>
          <channel>
            <item>
              <title>Telegram bot parser</title>
              <link>https://example.com/telegram</link>
              <description>Python parser for chats</description>
            </item>
            <item>
              <title>UI redesign</title>
              <link>https://example.com/ui</link>
              <description>Only design work</description>
            </item>
          </channel>
        </rss>
        """

        with patch.dict(os.environ, {"JOB_FEEDS": "https://example.com/feed.xml", "JOB_KEYWORDS": "telegram,python,бот,парсер"}, clear=False):
            with patch("app.integrations.urllib.request.urlopen") as mock_urlopen:
                class DummyResponse:
                    def __enter__(self):
                        return self

                    def __exit__(self, exc_type, exc, tb):
                        return False

                    def read(self):
                        return feed_xml

                mock_urlopen.return_value = DummyResponse()
                items = load_job_items()

        self.assertEqual(len(items), 1)
        self.assertIn("Telegram", items[0].title)
        self.assertIn("python", items[0].summary.lower())


if __name__ == "__main__":
    unittest.main()
