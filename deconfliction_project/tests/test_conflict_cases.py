import unittest
from models import Mission, Waypoint
from deconfliction_engine import detect_conflicts

class TestConflictCases(unittest.TestCase):
    def test_conflict_detection(self):
        mission = Mission(
            drone_id="primary",
            waypoints=[Waypoint(x=0, y=0, z=0), Waypoint(x=100, y=100, z=0)],
            start_time=1620000000.0,
            end_time=1620003600.0,
            speed=5.0,
            safety_buffer=50.0
        )
        simulated = [Mission(
            drone_id="test_flight",
            waypoints=[
                Waypoint(x=50, y=50, z=0, timestamp=1620001800.0),
                Waypoint(x=150, y=150, z=0, timestamp=1620003600.0)
            ],
            start_time=1620001800.0,
            end_time=1620003600.0,
            speed=5.0,
            safety_buffer=50.0
        )]
        conflicts = detect_conflicts(mission, simulated)
        self.assertTrue(conflicts)
        self.assertGreater(len(conflicts), 0)

if __name__ == "__main__":
    unittest.main()