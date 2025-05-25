from models import Waypoint
from typing import List, Optional

def interpolate_position(waypoints: List[Waypoint], time: float) -> Optional[Waypoint]:
    """Interpolate position at a given time."""
    if not waypoints or time < waypoints[0].timestamp or time > waypoints[-1].timestamp:
        return None
    for i in range(len(waypoints) - 1):
        wp1, wp2 = waypoints[i], waypoints[i + 1]
        if wp1.timestamp <= time <= wp2.timestamp:
            t = (time - wp1.timestamp) / (wp2.timestamp - wp1.timestamp) if wp2.timestamp != wp1.timestamp else 0
            return Waypoint(
                x=wp1.x + t * (wp2.x - wp1.x),
                y=wp1.y + t * (wp2.y - wp1.y),
                z=wp1.z + t * (wp2.z - wp1.z),
                timestamp=time
            )
    return waypoints[-1]