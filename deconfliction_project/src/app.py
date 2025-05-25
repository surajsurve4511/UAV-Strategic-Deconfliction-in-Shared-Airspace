from flask import Flask, request, jsonify
from flask_cors import CORS
from models import Mission, SimulatedFlight, Conflict
from deconfliction_engine import detect_conflicts
from config import PORT, DEBUG_MODE
import json
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Load simulated flights
try:
    with open(os.path.join("data", "sample_simulated_flights.json"), "r") as f:
        SIMULATED_FLIGHTS = [SimulatedFlight(**flight) for flight in json.load(f)]
    logger.info("Loaded simulated flights successfully")
except Exception as e:
    logger.error(f"Failed to load simulated flights: {str(e)}")
    SIMULATED_FLIGHTS = []

@app.route('/api/health', methods=['GET'])
def health_check():
    logger.info("Health check requested")
    return jsonify({"status": "healthy", "message": "Server is running"}), 200

@app.route('/api/analyze-mission', methods=['POST'])
def analyze_mission():
    try:
        data = request.get_json()
        mission = Mission(**data["mission"])
        logger.info(f"Analyzing mission for drone {mission.drone_id}")
        conflicts = detect_conflicts(mission, SIMULATED_FLIGHTS)
        response = {
            "status": "conflict" if conflicts else "clear",
            "conflicts": [c.dict() for c in conflicts] if conflicts else [],
            "message": "Conflicts detected" if conflicts else "No conflicts detected"
        }
        logger.info(f"Analysis complete: {response['status']}")
        return jsonify(response), 200
    except Exception as e:
        logger.error(f"Error in analyze_mission: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/api/simulated-flights', methods=['GET'])
def get_simulated_flights():
    try:
        logger.info("Fetching simulated flights")
        return jsonify([flight.dict() for flight in SIMULATED_FLIGHTS]), 200
    except Exception as e:
        logger.error(f"Error in get_simulated_flights: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    logger.info(f"Starting server on port {PORT}")
    app.run(host="0.0.0.0", port=PORT, debug=DEBUG_MODE)