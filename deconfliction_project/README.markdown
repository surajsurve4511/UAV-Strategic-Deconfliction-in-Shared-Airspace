UAV Strategic Deconfliction System
A 4D (3D space + time) system for detecting and visualizing spatial-temporal conflicts between drone missions in shared airspace.
Setup (Windows)

Install Dependencies:cd C:\Suraj\deconfliction_project
conda activate base
pip install -r requirements.txt


Run Backend:python src\app.py

Access at http://localhost:5000.
Serve Frontend:cd frontend
python -m http.server 8000

Open http://localhost:8000.
Run Tests:cd C:\Suraj\deconfliction_project
python -m unittest discover tests



Usage

Open http://localhost:8000.
Paste mission JSON (see index.html placeholder).
Click "Analyze Mission" to detect conflicts.
View 3D visualization (blue: primary, green: simulated, red: conflicts).
Use pause/resume/reset and time slider to control animation.
Results show conflict details or "No conflicts detected."

Features

4D Visualization: 3D trajectories with time slider for temporal control.
Scalability: SpatialIndex optimizes conflict detection for 20+ drones.
Edge Cases:
Single waypoint: Handled with conflict detection.
Zero waypoints: Blocked by validation.
Negative coordinates: Rejected.
Invalid time windows: Caught by Pydantic.



Deliverables

Code: Modular Python/Three.js solution.
Tests: Cover conflict, no-conflict, and edge cases.
Documentation: README.md, reflection_document.pdf.
Video: simulation_video.mp4 (3-5 min with voiceover).

Troubleshooting

ModuleNotFoundError: Verify src/models.py and test path fixes.
Frontend Lag: Reduce sphere complexity in main.js.
No Conflicts: Adjust safety buffers or waypoints in JSON.

