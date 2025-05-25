import unittest
from models import Mission, Waypoint
from deconfliction_engine import detect_conflicts

class TestNoConflict(unittest.TestCase):
    def test_no_conflict(self):
        mission = Mission(
            drone_id="primary",
            waypoints=[Waypoint(x=0, y=0, z=100), Waypoint(x=100, y=100, z=100)],
            start_time=1620000000.0,
            end_time=1620003600.0,
            speed=5.0,
            safety_buffer=10.0
        )
        simulated = [Mission(
            drone_id="test_flight",
            waypoints=[Waypoint(x=0, y=0, z=0), Waypoint(x=100, y=100, z=0)],
            start_time=1620000000.0,
            end_time=1620003600.0,
            speed=5.0,
            safety_buffer=10.0
        )]
        conflicts = detect_conflicts(mission, simulated)
        self.assertFalse(conflicts)

if __name__ == "__main__":
    unittest.main()