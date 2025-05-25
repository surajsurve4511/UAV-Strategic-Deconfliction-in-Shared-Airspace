import sys
import os
import unittest
import logging
from pydantic import ValidationError

# Add src/ to the module search path
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from models import Mission, Waypoint
from deconfliction_engine import detect_conflicts

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestEdgeCases(unittest.TestCase):
    def test_single_waypoint(self):
        logger.info("Running test_single_waypoint")
        mission = Mission(
            drone_id="primary",
            waypoints=[Waypoint(x=10, y=20, z=30)],
            start_time=1620000000.0,
            end_time=1620003600.0,
            speed=5.0,
            safety_buffer=10.0
        )
        simulated = [Mission(
            drone_id="test_flight",
            waypoints=[Waypoint(x=10, y=20, z=30)],
            start_time=1620000000.0,
            end_time=1620003600.0,
            speed=5.0,
            safety_buffer=10.0
        )]
        conflicts = detect_conflicts(mission, simulated)
        self.assertTrue(conflicts, "Expected conflict with identical waypoint")
        self.assertEqual(len(conflicts), 1, "Expected one conflict")
        conflict = conflicts[0]
        self.assertEqual(conflict.involved_flights, ["primary", "test_flight"], "Expected correct drone IDs")
        self.assertAlmostEqual(conflict.distance, 0.0, places=2, msg="Expected zero distance")
        self.assertEqual(conflict.location, (10, 20, 30), "Expected conflict at waypoint location")

    def test_zero_waypoints(self):
        logger.info("Running test_zero_waypoints")
        with self.assertRaises(ValidationError):
            Mission(
                drone_id="primary",
                waypoints=[],
                start_time=1620000000.0,
                end_time=1620003600.0,
                speed=5.0,
                safety_buffer=10.0
            )

    def test_negative_coordinates(self):
        logger.info("Running test_negative_coordinates")
        with self.assertRaises(ValidationError):
            Mission(
                drone_id="primary",
                waypoints=[Waypoint(x=-10, y=20, z=30)],
                start_time=1620000000.0,
                end_time=1620003600.0,
                speed=5.0,
                safety_buffer=10.0
            )

    def test_invalid_time_window(self):
        logger.info("Running test_invalid_time_window")
        with self.assertRaises(ValidationError):
            Mission(
                drone_id="primary",
                waypoints=[Waypoint(x=10, y=20, z=30), Waypoint(x=50, y=60, z=30)],
                start_time=1620003600.0,
                end_time=1620000000.0,
                speed=5.0,
                safety_buffer=10.0
            )

if __name__ == "__main__":
    unittest.main()