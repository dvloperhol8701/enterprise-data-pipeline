import logging
import sys
import unittest
from pathlib import Path
from pipeline_engine import DataPipelineEngine

# Ensure diagnostic verification checks are cleanly displayed in logs
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)


class TestDataPipelineLifecycle(unittest.TestCase):
    """Automated testing suite to audit the health and parameters of the pipeline engine."""

    def setUp(self):
        """Initializes testing workspace parameters before running individual test cases."""
        self.test_db = "test_sandbox.db"
        self.test_json = "structured_analytics.json"
        self.test_report = "test_summary.md"

        self.engine = DataPipelineEngine(
            db_name=self.test_db,
            json_name=self.test_json,
            report_name=self.test_report,
        )

    def test_engine_initialization_paths(self):
        """Test Case 1: Asserts that target parameters correctly resolve into Path objects."""
        logging.info("🧪 Running Test: Path Object Mapping Verification...")
        self.assertIsInstance(self.engine.db_path, Path)
        self.assertIsInstance(self.engine.json_path, Path)
        self.assertIsInstance(self.engine.report_path, Path)

    def test_missing_json_defensive_handling(self):
        """Test Case 2: Asserts that the engine returns False cleanly when paths are missing."""
        logging.info("🧪 Running Test: Defensive Missing Data Wall Verification...")
        broken_engine = DataPipelineEngine(
            db_name="ghost.db",
            json_name="non_existent_file.json",
            report_name="ghost.md",
        )
        success_flag = broken_engine.load_and_ingest_records()
        self.assertFalse(success_flag)

    def tearDown(self):
        """Safely cleans up temporary testing sandbox environmental artifacts."""
        sandbox_db = Path(self.test_db)
        if sandbox_db.exists():
            try:
                sandbox_db.unlink()
            except Exception:
                pass


if __name__ == "__main__":
    unittest.main()
