import datetime
import json
import logging
import sqlite3
import sys
from pathlib import Path
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)


class DataPipelineEngine:
    """A unified Object-Oriented engine to orchestrate the entire data pipeline lifecycle."""

    def __init__(self, db_name: str, json_name: str, report_name: str):
        self.db_path = Path(db_name)
        self.json_path = Path(json_name)
        self.report_path = Path(report_name)
        self.dataframe = None

    def load_and_ingest_records(self) -> bool:
        """Step 1: Ingests structured JSON data and builds the relational database table."""
        logging.info(f"🚀 Ingesting dataset from '{self.json_path.name}'...")
        if not self.json_path.exists():
            logging.error(f"Ingestion failed: File missing at {self.json_path}")
            return False

        try:
            with open(self.json_path, "r", encoding="utf-8") as file:
                payload = json.load(file)
            events = payload.get("extracted_events", [])

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS production_analytics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        error_code TEXT,
                        user_id TEXT,
                        message TEXT,
                        latency_ms INTEGER,
                        is_anomaly INTEGER
                    )
                """
                )

                insert_query = """
                    INSERT INTO production_analytics (timestamp, error_code, user_id, message, latency_ms, is_anomaly)
                    VALUES (?, ?, ?, ?, ?, ?)
                """
                for event in events:
                    cursor.execute(
                        insert_query,
                        (
                            event["timestamp"],
                            event["error_code"],
                            event["user_id"],
                            event["message"],
                            event["latency_ms"],
                            1 if event["is_anomaly"] else 0,
                        ),
                    )
            logging.info(
                f"✅ Successfully ingested {len(events)} database rows dynamically."
            )
            return True
        except Exception as err:
            logging.critical(f"❌ Error during ingestion module run: {err}")
            return False

    def transform_with_vectors(self) -> bool:
        """Step 2: Loads records directly into Pandas to perform matrix calculations."""
        logging.info("📊 Pulling database layer into Pandas vector space...")
        try:
            with sqlite3.connect(self.db_path) as conn:
                self.dataframe = pd.read_sql_query(
                    "SELECT * FROM production_analytics", conn
                )

            self.dataframe["user_id"] = self.dataframe["user_id"].str.upper()
            logging.info(
                f"✅ Vector matrix compiled successfully. Shape context: {self.dataframe.shape}"
            )
            return True
        except Exception as err:
            logging.critical(f"❌ Vector processing exception encountered: {err}")
            return False

    def generate_anomaly_report(self) -> None:
        """Step 3: Filters target data frames and automatically exports markdown templates."""
        logging.info("📝 Compiling final enterprise analytics summary document...")
        if self.dataframe is None or self.dataframe.empty:
            logging.warning("No memory active to export records from.")
            return

        try:
            anomalies = self.dataframe[self.dataframe["is_anomaly"] == 1]
            markdown_summary = f"""# Enterprise Class Architecture Summary
**Pipeline Status:** Operational | **Anomalies Filtered:** {len(anomalies)}
**Execution Run UTC:** {datetime.datetime.now(datetime.timezone.utc).isoformat()}

## Verified Event Logs
{anomalies[['id', 'timestamp', 'error_code', 'user_id', 'latency_ms']].to_markdown(index=False)}
"""
            with open(self.report_path, "w", encoding="utf-8") as file:
                file.write(markdown_summary)
            logging.info(
                f"💾 Report finalized: '{self.report_path.name}' compiled cleanly."
            )
        except Exception as err:
            logging.critical(f"❌ Reporting framework module crash: {err}")


if __name__ == "__main__":
    engine = DataPipelineEngine(
        db_name="littlelemon.db",
        json_name="structured_analytics.json",
        report_name="orchestration_summary.md",
    )

    if engine.load_and_ingest_records():
        if engine.transform_with_vectors():
            engine.generate_anomaly_report()
            logging.info(
                "🌟 SUCCESS: Full-stack pipeline orchestration lifecycle finished."
            )
