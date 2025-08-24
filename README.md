# UAV Strategic Deconfliction in Shared Airspace

## Objective

Design and implement a strategic deconfliction system that acts as the final authority for verifying whether a drone's planned waypoint mission is safe to execute in shared airspace. This system checks for conflicts in both space and time against the simulated flight paths of multiple other drones. The solution is extendable to a 4D simulation (3D spatial coordinates + time).

**Extra Credit:** Includes 4D visualization (3D space + time).

---

## Scenario

- A drone is scheduled to execute a waypoint mission within a specified time window (e.g., between `T_start` and `T_end`).
- The mission consists of a series of waypoints (spatial coordinates; optionally altitude for 3D) defining the drone’s route.
- Before takeoff, the drone queries a central deconfliction service that maintains the flight schedules of several other drones operating in the same airspace.
- Each simulated drone has its own flight path which may intersect with the primary mission in both space and time.

---

## Features

### Input
- **Primary Drone Mission:**  
  - Series of waypoints (x, y, optionally z for altitude).
  - Overall time window for mission completion.
- **Simulated Flight Schedules:**  
  - Dataset of other drones' flight paths and timings (hardcoded or file-based).

### Functionality
- **Spatial Check:**  
  - Validates that the primary mission does not intersect with any other drone’s trajectory within a defined safety buffer.
- **Temporal Check:**  
  - Ensures no other drone is present in the same spatial region during overlapping time segments.
- **Conflict Explanation:**  
  - Returns detailed explanations, including location(s), time(s), and conflicting flights for any detected conflict.
- **Query Interface:**  
  - Simple Python function to check mission status and retrieve conflict details.
- **Simulation & Visualization:**  
  - Generates simulation graphs and animations to depict:
    - The primary drone’s mission.
    - Simulated drone trajectories.
    - Highlighted conflict areas and times.
  - Produces videos or plotted graphs for:
    - Conflict-free missions.
    - Conflict scenarios with explanations.
  - **Extra Credit:** 4D visualization (3D space + time).
- **Scalability Discussion:**  
  - Reflection document discusses architecture for scaling to tens of thousands of commercial drones, including distributed computing, real-time pipelines, fault tolerance, and algorithm scalability.

---

## Getting Started

### Prerequisites
- Python 3.8+
- Recommended: [matplotlib](https://matplotlib.org/), [numpy](https://numpy.org/), [pandas](https://pandas.pydata.org/)
- For 3D/4D visualization: [matplotlib 3D toolkit](https://matplotlib.org/stable/gallery/mplot3d/index.html), [plotly](https://plotly.com/python/)

### Installation

```bash
git clone https://github.com/surajsurve4511/UAV-Strategic-Deconfliction-in-Shared-Airspace.git
cd UAV-Strategic-Deconfliction-in-Shared-Airspace
pip install -r requirements.txt
```

### Usage

1. **Prepare input data:**  
   - Define the primary drone’s mission (waypoints, time window).
   - Provide simulated flight schedules (as file or hardcoded dataset).

2. **Run the deconfliction check:**
   - Use the provided Python interface:
     ```python
     from deconfliction import check_mission_conflicts
     status, details = check_mission_conflicts(primary_mission, simulated_flights)
     print(status)
     if status == "conflict detected":
         print(details)
     ```
   - Visualize results:
     ```bash
     python visualize_simulation.py
     ```

3. **View simulation outputs:**
   - Find generated images/graphs/videos in the `outputs/` or `visualizations/` directory.

---

## Code Structure

```
deconfliction_project/
├── deconfliction.py          # Main deconfliction logic (spatial/temporal checks)
├── data/
│   └── simulated_flights.json
├── visualize_simulation.py   # Script for visualization and animation
├── tests/
│   └── test_deconfliction.py
├── outputs/                  # Generated graphs/animations/videos
└── README.md
```

---

## AI-Assisted Development

This project leverages AI-assisted tools (e.g., Claude Code, Cursor AI, Windsurf, Lovable, Replit) to expedite development and documentation. See the reflection document for examples and discussion of how these tools contributed to code quality and speed.

---

## Testing

- Comprehensive test cases are provided covering:
  - Conflict-free missions
  - Conflicting missions (with location, time, and causation explained)
  - Edge cases (e.g., overlapping waypoints, simultaneous arrivals)
- Automated testing scripts are included in the `tests/` directory.

---

## Scalability

For real-world deployment with tens of thousands of drones, the reflection document outlines:
- Distributed system architecture
- Real-time data ingestion pipelines
- Fault tolerance strategies
- Scalable conflict resolution algorithms

---

## Documentation

- **README.md:** Setup and usage instructions (this file).
- **Reflection & Justification Document:**  
  - Design decisions, architectural choices, spatial/temporal check explanations, AI integration, testing strategy, scalability discussion.
- **Demonstration Video:**  
  - 3–5 minute narrated walkthrough of the system and simulations (conflict-free & conflict-present scenarios, plus 4D visualization if implemented).

---

## Evaluation Rubric

- **Code Quality & Architecture:** Modularity, coding standards, architectural decisions, documentation.
- **Testability & QA:** Test coverage, automation, error handling, QA practices.
- **AI Use & Innovation:** Integration and evaluation of AI tools in the workflow.
- **Documentation & Communication:** Demonstration video, reflection document, scalability discussion.
- **Extra Credit:** 4D visualization.

---

## License

MIT License. See LICENSE file for details.

---

## Contact

For questions or contributions, please open an issue or contact surajsurve4511 (https://github.com/surajsurve4511).