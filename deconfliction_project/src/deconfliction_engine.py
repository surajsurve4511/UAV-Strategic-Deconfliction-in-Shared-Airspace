from typing import List, Optional, Tuple
from models import Mission, SimulatedFlight, Conflict, Waypoint
from utils import interpolate_position
import numpy as np
from collections import defaultdict
import logging

# Configure logging for debugging and performance tracking
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SpatialIndex:
    """Grid-based spatial index to optimize collision detection by grouping segments into cells."""
    def __init__(self, grid_size: float = 50.0):
        self.grid_size = grid_size
        self.cells = defaultdict(list)

    def add_segment(self, mission: Mission, segment_idx: int):
        """Add a mission segment to relevant grid cells based on its spatial bounds."""
        wp1, wp2 = mission.waypoints[segment_idx], mission.waypoints[segment_idx + 1]
        min_x, max_x = min(wp1.x, wp2.x), max(wp1.x, wp2.x)
        min_y, max_y = min(wp1.y, wp2.y), max(wp1.y, wp2.y)
        min_z, max_z = min(wp1.z, wp2.z), max(wp1.z, wp2.z)
        for x in range(int(min_x // self.grid_size), int(max_x // self.grid_size) + 1):
            for y in range(int(min_y // self.grid_size), int(max_y // self.grid_size) + 1):
                for z in range(int(min_z // self.grid_size), int(max_z // self.grid_size) + 1):
                    self.cells[(x, y, z)].append((mission, segment_idx))

    def add_static_waypoint(self, mission: Mission):
        """Add a static waypoint to the spatial index for single-waypoint missions."""
        wp = mission.waypoints[0]
        x, y, z = int(wp.x // self.grid_size), int(wp.y // self.grid_size), int(wp.z // self.grid_size)
        self.cells[(x, y, z)].append((mission, None))  # None indicates static waypoint

    def query(self, mission: Mission, segment_idx: int) -> List[Tuple[Mission, int]]:
        """Retrieve segments or static waypoints in nearby grid cells."""
        wp1, wp2 = mission.waypoints[segment_idx], mission.waypoints[segment_idx + 1]
        min_x, max_x = min(wp1.x, wp2.x), max(wp1.x, wp2.x)
        min_y, max_y = min(wp1.y, wp2.y), max(wp1.y, wp2.y)
        min_z, max_z = min(wp1.z, wp2.z), max(wp1.z, wp2.z)
        nearby = []
        for x in range(int(min_x // self.grid_size), int(max_x // self.grid_size) + 1):
            for y in range(int(min_y // self.grid_size), int(max_y // self.grid_size) + 1):
                for z in range(int(min_z // self.grid_size), int(max_z // self.grid_size) + 1):
                    nearby.extend(self.cells.get((x, y, z), []))
        return nearby

    def query_static(self, wp: Waypoint) -> List[Tuple[Mission, Optional[int]]]:
        """Query nearby static waypoints or segments for a static waypoint."""
        x, y, z = int(wp.x // self.grid_size), int(wp.y // self.grid_size), int(wp.z // self.grid_size)
        return self.cells.get((x, y, z), [])

def detect_conflicts(primary_mission: Mission, other_flights: List[SimulatedFlight]) -> List[Conflict]:
    """Detect spatial-temporal conflicts between primary mission and other flights."""
    try:
        # Assign timestamps to waypoints
        primary_mission.assign_timestamps()
        spatial_index = SpatialIndex(grid_size=50.0)
        conflicts = []

        # Index other flights' segments or static waypoints
        for flight in other_flights:
            flight.assign_timestamps()
            if len(flight.waypoints) == 1:
                spatial_index.add_static_waypoint(flight)
            else:
                for i in range(len(flight.waypoints) - 1):
                    spatial_index.add_segment(flight, i)

        # Handle single-waypoint primary mission
        if len(primary_mission.waypoints) == 1:
            wp1 = primary_mission.waypoints[0]
            nearby = spatial_index.query_static(wp1)
            for other_mission, segment_idx in nearby:
                if other_mission.drone_id == primary_mission.drone_id:
                    continue
                if segment_idx is None:  # Static vs static
                    conflict = check_static_collision(wp1, other_mission.waypoints[0],
                                                    primary_mission, other_mission)
                else:  # Static vs segment
                    wp3, wp4 = other_mission.waypoints[segment_idx], other_mission.waypoints[segment_idx + 1]
                    conflict = check_static_vs_segment_collision(wp1, wp3, wp4,
                                                               primary_mission.safety_buffer + other_mission.safety_buffer)
                if conflict:
                    conflicts.append(conflict)
        else:
            # Check primary mission segments
            for i in range(len(primary_mission.waypoints) - 1):
                wp1, wp2 = primary_mission.waypoints[i], primary_mission.waypoints[i + 1]
                nearby = spatial_index.query(primary_mission, i)
                for other_mission, segment_idx in nearby:
                    if other_mission.drone_id == primary_mission.drone_id:
                        continue
                    if segment_idx is None:  # Segment vs static
                        conflict = check_static_vs_segment_collision(other_mission.waypoints[0], wp1, wp2,
                                                                   primary_mission.safety_buffer + other_mission.safety_buffer)
                    else:  # Segment vs segment
                        wp3, wp4 = other_mission.waypoints[segment_idx], other_mission.waypoints[segment_idx + 1]
                        conflict = check_segment_collision(wp1, wp2, wp3, wp4,
                                                         primary_mission.safety_buffer + other_mission.safety_buffer)
                    if conflict:
                        conflicts.append(conflict)

        logger.info(f"Detected {len(conflicts)} conflicts for mission {primary_mission.drone_id}")
        return conflicts
    except Exception as e:
        logger.error(f"Error in detect_conflicts: {str(e)}")
        raise

def check_static_collision(wp1: Waypoint, wp2: Waypoint, mission1: Mission, mission2: Mission) -> Optional[Conflict]:
    """Check for collision between two static waypoints."""
    try:
        # Check if time windows overlap
        t_start = max(mission1.start_time, mission2.start_time)
        t_end = min(mission1.end_time, mission2.end_time)
        if t_start >= t_end:
            return None

        # Calculate distance between static waypoints
        dist = wp1.distance_to(wp2)
        min_safe_distance = mission1.safety_buffer + mission2.safety_buffer
        if dist < min_safe_distance:
            return Conflict(
                time=t_start,
                location=(wp1.x, wp1.y, wp1.z),
                involved_flights=[mission1.drone_id, mission2.drone_id],
                distance=dist
            )
        return None
    except Exception as e:
        logger.error(f"Error in check_static_collision: {str(e)}")
        raise

def check_static_vs_segment_collision(static_wp: Waypoint, wp1: Waypoint, wp2: Waypoint, min_safe_distance: float) -> Optional[Conflict]:
    """Check for collision between a static waypoint and a moving segment."""
    try:
        # Check time overlap
        t_start = max(static_wp.timestamp, wp1.timestamp)
        t_end = min(static_wp.timestamp, wp2.timestamp)
        if t_start >= t_end:
            return None

        # Interpolate segment position at static waypoint's timestamp
        t = (static_wp.timestamp - wp1.timestamp) / (wp2.timestamp - wp1.timestamp) if wp2.timestamp != wp1.timestamp else 0
        segment_pos = Waypoint(
            x=wp1.x + t * (wp2.x - wp1.x),
            y=wp1.y + t * (wp2.y - wp1.y),
            z=wp1.z + t * (wp2.z - wp1.z),
            timestamp=static_wp.timestamp
        )
        dist = static_wp.distance_to(segment_pos)
        if dist < min_safe_distance:
            return Conflict(
                time=static_wp.timestamp,
                location=(static_wp.x, static_wp.y, static_wp.z),
                involved_flights=["primary", "other"],
                distance=dist
            )
        return None
    except Exception as e:
        logger.error(f"Error in check_static_vs_segment_collision: {str(e)}")
        raise

def check_segment_collision(wp1: Waypoint, wp2: Waypoint, wp3: Waypoint, wp4: Waypoint, min_safe_distance: float) -> Optional[Conflict]:
    """Calculate closest approach between two trajectory segments in space and time."""
    try:
        # Determine overlapping time window
        t_start = max(wp1.timestamp, wp3.timestamp)
        t_end = min(wp2.timestamp, wp4.timestamp)
        if t_start >= t_end:
            return None

        # Compute velocity vectors for both segments
        t1_duration = wp2.timestamp - wp1.timestamp or 1e-6
        t2_duration = wp4.timestamp - wp3.timestamp or 1e-6
        v1 = [(wp2.x - wp1.x) / t1_duration, (wp2.y - wp1.y) / t1_duration, (wp2.z - wp1.z) / t1_duration]
        v2 = [(wp4.x - wp3.x) / t2_duration, (wp4.y - wp3.y) / t2_duration, (wp4.z - wp3.z) / t2_duration]
        w = [wp1.x - wp3.x, wp1.y - wp3.y, wp1.z - wp3.z]
        vr = [v1[i] - v2[i] for i in range(3)]
        vr_dot_vr = sum(v * v for v in vr)

        if vr_dot_vr == 0:  # Handle parallel paths
            pos1 = interpolate_position([wp1, wp2], t_start)
            pos2 = interpolate_position([wp3, wp4], t_start)
            dist = pos1.distance_to(pos2)
            if dist < min_safe_distance:
                return Conflict(time=t_start, location=(pos1.x, pos1.y, pos1.z), involved_flights=["primary", "other"], distance=dist)
            return None

        # Calculate time of closest approach
        t_closest = -sum(w[i] * vr[i] for i in range(3)) / vr_dot_vr
        t_closest_abs = wp1.timestamp + t_closest * t1_duration
        t_closest_abs = max(t_start, min(t_end, t_closest_abs))
        pos1 = interpolate_position([wp1, wp2], t_closest_abs)
        pos2 = interpolate_position([wp3, wp4], t_closest_abs)
        dist = pos1.distance_to(pos2)
        if dist < min_safe_distance:
            return Conflict(time=t_closest_abs, location=(pos1.x, pos1.y, pos1.z), involved_flights=["primary", "other"], distance=dist)
        return None
    except Exception as e:
        logger.error(f"Error in check_segment_collision: {str(e)}")
        raise