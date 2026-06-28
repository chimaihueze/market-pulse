from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[2]


class DockerComposeTest(unittest.TestCase):
    def test_clickhouse_mounts_startup_init_script(self):
        compose = (ROOT / "docker-compose.yml").read_text()
        init_sql = (
            ROOT / "docker" / "clickhouse" / "initdb" / "001-create-users.sql"
        ).read_text()

        self.assertIn("CLICKHOUSE_ALWAYS_RUN_INITDB_SCRIPTS: 1", compose)
        self.assertIn("CLICKHOUSE_USER: admin", compose)
        self.assertIn("CLICKHOUSE_PASSWORD: admin", compose)
        self.assertIn("CLICKHOUSE_DEFAULT_ACCESS_MANAGEMENT: 1", compose)
        self.assertIn(
            "./docker/clickhouse/initdb:/docker-entrypoint-initdb.d:ro",
            compose,
        )
        self.assertIn("CREATE DATABASE IF NOT EXISTS market_pulse", init_sql)
        self.assertIn("CREATE USER IF NOT EXISTS market_pulse", init_sql)

    def test_app_services_wait_for_clickhouse_health(self):
        compose = (ROOT / "docker-compose.yml").read_text()

        for service_name in ("ingestion", "storage"):
            match = re.search(
                rf"^  {service_name}:\n(?P<body>(?:^    .*\n?)*)",
                compose,
                re.MULTILINE,
            )

            self.assertIsNotNone(match)
            body = match.group("body")
            self.assertIn("depends_on:", body)
            self.assertIn("clickhouse:", body)
            self.assertIn("condition: service_healthy", body)
