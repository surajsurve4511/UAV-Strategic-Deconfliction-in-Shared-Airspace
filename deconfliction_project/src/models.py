from pydantic import BaseModel, Field, validator
from typing import List, Optional, Tuple
from datetime import datetime

class Waypoint(BaseModel):
    x: float = Field(..., ge=0, description="X-coordinate (meters)")
    y: float = Field(..., ge=0, description="Y-coordinate (meters)")
    z: float = Field(..., ge=0, description="Z-coordinate (meters)")
    timestamp: Optional[float] = None

    def distance_to(self, other: 'Waypoint') -> float:
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2 + (self.z - other.z) ** 2) ** 0.5

class Mission(BaseModel):
    drone_id: str = Field(..., min_length=1)
    waypoints: List[Waypoint] = Field(..., min_items=1)
    start_time: float = Field(..., ge=0)
    end_time: float = Field(..., gt=0)
    speed: float = Field(default=5.0, gt=0)
    safety_buffer: float = Field(default=10.0, gt=0)

    @validator('end_time')
    def validate_time_window(cls, v, values):
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError("end_time must be greater than start_time")
        return v

    def assign_timestamps(self):
        if len(self.waypoints) == 1:
            self.waypoints[0].timestamp = self.start_time
            return
        distances = [0.0]
        for i in range(1, len(self.waypoints)):
            distances.append(distances[-1] + self.waypoints[i-1].distance_to(self.waypoints[i]))
        total_distance = distances[-1]
        if total_distance == 0:
            for wp in self.waypoints:
                wp.timestamp = self.start_time
            return
        for i, wp in enumerate(self.waypoints):
            wp.timestamp = self.start_time + (distances[i] / total_distance) * (self.end_time - self.start_time)

class SimulatedFlight(Mission):
    pass

class Conflict(BaseModel):
    time: float
    location: Tuple[float, float, float]
    involved_flights: List[str]
    distance: float