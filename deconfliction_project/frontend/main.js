const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer();
const container = document.getElementById('scene-container');
renderer.setSize(window.innerWidth * 0.7, window.innerHeight * 0.7);
container.appendChild(renderer.domElement);

camera.position.set(100, 100, 100);
camera.lookAt(0, 0, 0);

const axesHelper = new THREE.AxesHelper(50);
scene.add(axesHelper);

const drones = {};
const conflictMarkers = [];
const trajectories = [];
let simulationTime = 0;
const simulationSpeed = 0.5; // Slower for 20 drones
let simulatedFlights = [];
let isPaused = false;
let timeRange = { min: 0, max: 1 };

const form = document.getElementById('mission-form');
const resultsDiv = document.getElementById('results');
const pauseResumeBtn = document.getElementById('pause-resume');
const resetBtn = document.getElementById('reset');
const timeSlider = document.getElementById('time-slider');
const timeDisplay = document.getElementById('time-display');

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    clearScene();
    const missionInput = document.getElementById('mission-input').value;
    try {
        const missionData = JSON.parse(missionInput);
        console.log('Submitting mission:', missionData);
        await analyzeMission(missionData);
        isPaused = false;
        pauseResumeBtn.textContent = 'Pause';
    } catch (error) {
        console.error('JSON parse error:', error);
        resultsDiv.innerHTML = `<p style="color: red;">Error: Invalid JSON - ${error.message}</p>`;
    }
});

pauseResumeBtn.addEventListener('click', () => {
    isPaused = !isPaused;
    pauseResumeBtn.textContent = isPaused ? 'Resume' : 'Pause';
    console.log('Simulation paused:', isPaused);
});

resetBtn.addEventListener('click', () => {
    simulationTime = drones['primary'] ? drones['primary'].start_time : 0;
    timeSlider.value = 0;
    updateTimeDisplay();
    isPaused = false;
    pauseResumeBtn.textContent = 'Pause';
    console.log('Simulation reset');
});

timeSlider.addEventListener('input', () => {
    isPaused = true;
    pauseResumeBtn.textContent = 'Resume';
    const t = parseFloat(timeSlider.value);
    simulationTime = timeRange.min + t * (timeRange.max - timeRange.min);
    updateTimeDisplay();
    updateDronePositions();
});

async function fetchSimulatedFlights() {
    try {
        const response = await fetch('http://localhost:5000/api/simulated-flights');
        simulatedFlights = await response.json();
        console.log('Fetched simulated flights:', simulatedFlights);
        renderTrajectories();
    } catch (error) {
        console.error('Error fetching simulated flights:', error);
    }
}

async function analyzeMission(missionData) {
    try {
        const response = await fetch('http://localhost:5000/api/analyze-mission', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(missionData)
        });
        const result = await response.json();
        console.log('Analysis result:', result);
        displayResults(result);
        renderDronesAndConflicts(missionData.mission, result);
    } catch (error) {
        console.error('Error analyzing mission:', error);
        resultsDiv.innerHTML = `<p style="color: red;">Error: ${error.message}</p>`;
    }
}

function displayResults(result) {
    resultsDiv.innerHTML = `<h3>Result: ${result.status.toUpperCase()}</h3>`;
    resultsDiv.innerHTML += `<p>Total Drones: ${simulatedFlights.length + 1}</p>`;
    if (result.status === 'conflict') {
        result.conflicts.forEach((conflict, i) => {
            resultsDiv.innerHTML += `
                <p>Conflict ${i + 1}:
                    Location: (${conflict.location[0].toFixed(2)}, ${conflict.location[1].toFixed(2)}, ${conflict.location[2].toFixed(2)})<br>
                    Time: ${new Date(conflict.time * 1000).toISOString()}<br>
                    Conflicting Drones: ${conflict.involved_flights.join(', ')}<br>
                    Distance: ${conflict.distance.toFixed(2)}m
                </p>`;
        });
    } else {
        resultsDiv.innerHTML += `<p>${result.message}</p>`;
    }
}

function renderTrajectories() {
    trajectories.forEach(t => scene.remove(t));
    trajectories.length = 0;

    if (drones['primary']) {
        const points = drones['primary'].waypoints.map(wp => new THREE.Vector3(wp.x, wp.y, wp.z));
        const geometry = new THREE.BufferGeometry().setFromPoints(points);
        const material = new THREE.LineBasicMaterial({ color: 0x0000ff });
        const line = new THREE.Line(geometry, material);
        scene.add(line);
        trajectories.push(line);
    }

    simulatedFlights.forEach(flight => {
        const points = flight.waypoints.map(wp => new THREE.Vector3(wp.x, wp.y, wp.z));
        const geometry = new THREE.BufferGeometry().setFromPoints(points);
        const material = new THREE.LineBasicMaterial({ color: 0x00ff00 });
        const line = new THREE.Line(geometry, material);
        scene.add(line);
        trajectories.push(line);
    });
}

function renderDronesAndConflicts(mission, result) {
    clearScene();
    drones['primary'] = mission;
    timeRange.min = mission.start_time;
    timeRange.max = mission.end_time;
    timeSlider.min = 0;
    timeSlider.max = 1;
    timeSlider.value = 0;
    simulationTime = mission.start_time;
    updateTimeDisplay();

    const droneGroup = new THREE.Group();
    const primaryGeometry = new THREE.SphereGeometry(2, 16, 16);
    const primaryMaterial = new THREE.MeshBasicMaterial({ color: 0x0000ff });
    drones['primary'].mesh = new THREE.Mesh(primaryGeometry, primaryMaterial);
    droneGroup.add(drones['primary'].mesh);
    scene.add(droneGroup);

    simulatedFlights.forEach(flight => {
        const geometry = new THREE.SphereGeometry(2, 16, 16);
        const material = new THREE.MeshBasicMaterial({ color: 0x00ff00 });
        flight.mesh = new THREE.Mesh(geometry, material);
        droneGroup.add(flight.mesh);
        drones[flight.drone_id] = flight;
    });

    if (result.status === 'conflict') {
        result.conflicts.forEach(conflict => {
            const geometry = new THREE.SphereGeometry(3, 16, 16);
            const material = new THREE.MeshBasicMaterial({ color: 0xff0000 });
            const marker = new THREE.Mesh(geometry, material);
            marker.position.set(conflict.location[0], conflict.location[1], conflict.location[2]);
            scene.add(marker);
            conflictMarkers.push(marker);
        });
    }

    renderTrajectories();
    animate();
}

function updateTimeDisplay() {
    timeDisplay.textContent = new Date(simulationTime * 1000).toISOString();
}

function updateDronePositions() {
    Object.values(drones).forEach(drone => {
        const pos = interpolatePosition(drone, simulationTime);
        if (pos && drone.mesh) {
            drone.mesh.position.set(pos.x, pos.y, pos.z);
        }
    });
    renderer.render(scene, camera);
}

function clearScene() {
    Object.values(drones).forEach(drone => {
        if (drone.mesh) scene.remove(drone.mesh);
    });
    conflictMarkers.forEach(marker => scene.remove(marker));
    conflictMarkers.length = 0;
    renderTrajectories();
}

function animate() {
    if (!isPaused) {
        requestAnimationFrame(animate);
        simulationTime += simulationSpeed;
        timeSlider.value = (simulationTime - timeRange.min) / (timeRange.max - timeRange.min);
        updateTimeDisplay();
        updateDronePositions();
    } else {
        requestAnimationFrame(animate);
    }
}

function interpolatePosition(drone, time) {
    const waypoints = drone.waypoints;
    if (!waypoints || time < drone.start_time || time > drone.end_time) return null;
    for (let i = 0; i < waypoints.length - 1; i++) {
        const wp1 = waypoints[i];
        const wp2 = waypoints[i + 1];
        if (wp1.timestamp <= time && time <= wp2.timestamp) {
            const t = (time - wp1.timestamp) / (wp2.timestamp - wp1.timestamp) || 0;
            return {
                x: wp1.x + t * (wp2.x - wp1.x),
                y: wp1.y + t * (wp2.y - wp1.y),
                z: wp1.z + t * (wp2.z - wp1.z)
            };
        }
    }
    return waypoints[waypoints.length - 1];
}

fetchSimulatedFlights();