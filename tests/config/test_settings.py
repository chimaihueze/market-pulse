import unittest
from unittest.mock import patch

from app.config.settings import Settings


class SettingsTest(unittest.TestCase):
    def test_reads_service_connection_settings_from_environment(self):
        with patch.dict(
            "os.environ",
            {
                "KAFKA_URL": "kafka:9092",
                "CLICKHOUSE_HOST": "clickhouse",
                "CLICKHOUSE_PORT": "9000",
                "CLICKHOUSE_USER": "default",
                "CLICKHOUSE_PASSWORD": "",
                "CLICKHOUSE_DATABASE": "default",
                "CLICKHOUSE_BATCH_SIZE": "500",
            },
        ):
            settings = Settings()

        self.assertEqual(settings.kafka_url, "kafka:9092")
        self.assertEqual(settings.clickhouse_host, "clickhouse")
        self.assertEqual(settings.clickhouse_port, 9000)
        self.assertEqual(settings.clickhouse_user, "default")
        self.assertEqual(settings.clickhouse_password, "")
        self.assertEqual(settings.clickhouse_database, "default")
        self.assertEqual(settings.clickhouse_batch_size, 500)
