
// function start() {
//     fetch('/button/start')
// }
// function stop() {
//     fetch('/button/stop')
// }


// =============================
// Chart Configuration
// =============================

function createChart(canvasId, label, unit) {
    return new Chart(document.getElementById(canvasId), {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: label,
                data: [],
                tension: 0.25,
                fill: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: false,
            scales: {
                x: {
                    ticks: {
                        maxTicksLimit: 6
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: unit
                    }
                }
            }
        }
    });
}

const fuelCellChart = createChart('fuelCellChart', 'Fuel Cell Power', 'W');
const batteryChart = createChart('batteryChart', 'Battery Power', 'W');
const motorChart = createChart('motorChart', 'Motor Power', 'W');
const thrustChart = createChart('thrustChart', 'Thrust', 'kg');
const pressureChart = createChart('pressureChart', 'Pressure', 'bar');
const socChart = createChart('socChart', 'Battery SoC', '%');


// =============================
// Example Update Functions
// Replace these with your backend calls
// =============================

function updateValue(id, value) {
    document.getElementById(id).innerText = value;
}

function addData(chart, label, value) {
    chart.data.labels.push(label);
    chart.data.datasets[0].data.push(value);

    // Keep last 60 samples
    if (chart.data.labels.length > 60)
    {
        chart.data.labels.shift();
        chart.data.datasets[0].data.shift();
    }

    chart.update();
}

function formatDate(value) {
    if (!value)
    {
        return '';
    }

    return new Date(value).toLocaleString();
}

function downloadRun(runId) {
    if (!runId)
    {
        return;
    }

    window.location.href = `/api/runs/${runId}/csv`;
}

async function postJson(url, data = {}) {
    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    });

    if (!response.ok)
    {
        throw new Error(`Request failed: ${response.status}`);
    }

    return response.json();
}


// =============================
// Example Demo Data
// Replace with real sensor polling
// =============================


async function fetchValues() {

    const now = new Date().toLocaleTimeString();

    const sensorData = await getData('sensorData')
    // console.log(sensorData)

    updateValue('fuelCellPower', sensorData.FUELCELL_POWER.toFixed(1) + ' W');
    updateValue('fuelCellVoltage', sensorData.FUELCELL_VOLTAGE.toFixed(1) + ' V');
    updateValue('fuelCellCurrent', sensorData.FUELCELL_CURRENT.toFixed(1) + ' A');

    updateValue('batteryPower', sensorData.BATTERY_POWER.toFixed(1) + ' W');
    updateValue('batteryVoltage', sensorData.BATTERY_VOLTAGE.toFixed(1) + ' V');
    updateValue('batteryCurrent', sensorData.BATTERY_CURRENT.toFixed(1) + ' A');
    updateValue('batterySOC', sensorData.BATTERY_SOC.toFixed(0) + ' %');
    updateValue('batteryPercentage', sensorData.BATTERY_SOC.toFixed(0) + ' %');

    updateValue('motorPower', sensorData.LOAD_POWER.toFixed(1) + ' W');
    updateValue('motorVoltage', sensorData.LOAD_VOLTAGE.toFixed(1) + ' V');
    updateValue('motorCurrent', sensorData.LOAD_CURRENT.toFixed(1) + ' A');
    updateValue('motorThrust', sensorData.THRUST.toFixed(1) + ' kg');

    updateValue('pressureValue', sensorData.PRESSURE.toFixed(2) + ' bar');

    addData(fuelCellChart, now, sensorData.FUELCELL_POWER);
    addData(batteryChart, now, sensorData.BATTERY_POWER);
    addData(motorChart, now, sensorData.LOAD_POWER);
    addData(pressureChart, now, sensorData.PRESSURE);
    addData(socChart, now, sensorData.BATTERY_SOC);
    addData(thrustChart, now, sensorData.THRUST);
}

function getData(varName) {
    console.log(`Fetching Data: ${varName}`)
    return new Promise((resolve) => {
        fetch(`/api/get/${varName}`)
            .then(response => {
                // after the response has been received
                // console.log(response)
                if (!response.ok)
                {
                    throw new Error("Network response was not ok");
                }
                return response.json(); // read the response data and convert to json
            })
            .then(data => {
                // after data has been converted
                // console.log(data)
                resolve(data)
            })
            .catch(error => {
                console.error("Error fetching data:", error);
            });
    })
}

// =============================
// Test Run Controls
// =============================

let activeRun = null;

async function updateRun(id, data) {
    const response = await fetch(`/api/runs/${id}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    });

    if (!response.ok)
    {
        throw new Error('Failed to update run');
    }

    return response.json();
}

async function fetchCurrentRun() {
    const response = await fetch('/api/runs/current');

    if (!response.ok)
    {
        throw new Error(`Failed to fetch current run: ${response.status}`);
    }

    return response.json();
}

async function fetchRuns() {
    const response = await fetch('/api/runs');

    if (!response.ok)
    {
        throw new Error(`Failed to fetch runs: ${response.status}`);
    }

    return response.json();
}

function renderCurrentRun(run) {
    activeRun = run;

    const runId = document.getElementById('currentRunId');
    const runStatus = document.getElementById('currentRunStatus');
    const runName = document.getElementById('runName');
    const runNotes = document.getElementById('runNotes');
    const stopRunButton = document.getElementById('stopRunButton');
    const saveRunButton = document.getElementById('saveRunButton');
    const downloadCurrentRunButton = document.getElementById('downloadCurrentRunButton');

    if (!run)
    {
        runId.innerText = 'None';
        runStatus.innerText = 'Stopped';
        runName.value = '';
        runNotes.value = '';
        stopRunButton.disabled = true;
        saveRunButton.disabled = true;
        downloadCurrentRunButton.disabled = true;
        return;
    }

    runId.innerText = run.id;
    runStatus.innerText = run.ended_at ? 'Stopped' : 'Active';
    runName.value = run.name || '';
    runNotes.value = run.notes || '';
    stopRunButton.disabled = Boolean(run.ended_at);
    saveRunButton.disabled = false;
    downloadCurrentRunButton.disabled = false;
}

function renderRuns(runs) {
    const tbody = document.getElementById('runsTableBody');
    tbody.innerHTML = '';

    if (!runs.length)
    {
        const row = document.createElement('tr');
        const cell = document.createElement('td');
        cell.colSpan = 8;
        cell.innerText = 'No runs found';
        row.appendChild(cell);
        tbody.appendChild(row);
        return;
    }

    runs.forEach((run) => {
        const row = document.createElement('tr');

        // ID
        addCell(row, run.id);

        // Editable Name
        const nameInput = document.createElement('input');
        nameInput.type = 'text';
        nameInput.value = run.name || '';

        const nameCell = document.createElement('td');
        nameCell.appendChild(nameInput);
        row.appendChild(nameCell);

        // Started
        addCell(row, formatDate(run.started_at));

        // Ended
        addCell(row, run.ended_at ? formatDate(run.ended_at) : 'Active');

        // Samples
        addCell(row, run.sample_count);

        // Editable Notes
        const notesInput = document.createElement('textarea');
        notesInput.value = run.notes || '';

        const notesCell = document.createElement('td');
        notesCell.appendChild(notesInput);
        row.appendChild(notesCell);

        // Download button
        const downloadCell = document.createElement('td');

        const downloadButton = document.createElement('button');
        downloadButton.innerText = 'Download';
        downloadButton.addEventListener('click', () => downloadRun(run.id));

        downloadCell.appendChild(downloadButton);
        row.appendChild(downloadCell);

        // Save button
        const saveCell = document.createElement('td');

        const saveButton = document.createElement('button');
        saveButton.innerText = 'Save';

        saveButton.addEventListener('click', async () => {
            saveButton.disabled = true;

            try
            {
                await updateRun(run.id, {
                    name: nameInput.value,
                    notes: notesInput.value
                });

                saveButton.innerText = 'Saved';

                setTimeout(() => {
                    saveButton.innerText = 'Save';
                    saveButton.disabled = false;
                }, 1000);

            } catch (err)
            {
                console.error(err);
                saveButton.innerText = 'Error';
                saveButton.disabled = false;
            }
        });

        saveCell.appendChild(saveButton);
        row.appendChild(saveCell);

        tbody.appendChild(row);
    });
}

function addCell(row, value) {
    const cell = document.createElement('td');
    cell.innerText = value;
    row.appendChild(cell);
}

async function refreshRuns() {
    console.log('Refresh Runs');
    try
    {
        const [currentRun, runs] = await Promise.all([
            fetchCurrentRun(),
            fetchRuns()
        ]);

        renderCurrentRun(currentRun);
        renderRuns(runs);
    } catch (err)
    {
        console.error('Failed to refresh runs:', err);
    }
}


// =============================
// Button Hooks
// =============================


let interval

document.getElementById('startButton').addEventListener('click', () => {
    console.log('Start system');
    fetch('/api/button/start')
});

document.getElementById('stopButton').addEventListener('click', () => {
    console.log('Stop system');
    fetch('/api/button/stop')
});

document.getElementById('enableDrone').addEventListener('click', () => {
    console.log('Enable Drone');
    fetch('/api/button/enableDrone')
});

document.getElementById('disableDrone').addEventListener('click', () => {
    console.log('Disable Drone');
    fetch('/api/button/disableDrone')
});

document.getElementById('armDrone').addEventListener('click', () => {
    console.log('Arm Drone');
    fetch('/api/button/armDrone')
});

document.getElementById('calibrateDrone').addEventListener('click', () => {
    console.log('Calibrate Drone');
    fetch('/api/button/calibrateDrone')
});

document.getElementById('newRunButton').addEventListener('click', async () => {
    console.log('New Run');
    if (!interval)
        interval = setInterval(fetchValues, 1000);
    try
    {
        await postJson('/api/runs/start', {
            name: document.getElementById('runName').value,
            notes: document.getElementById('runNotes').value
        });
        await refreshRuns();
    } catch (err)
    {
        console.error('Failed to start run:', err);
    }
});

document.getElementById('saveRunButton').addEventListener('click', async () => {
    console.log('Save Run');
    if (!activeRun)
    {
        return;
    }

    try
    {
        await postJson('/api/runs/current', {
            name: document.getElementById('runName').value,
            notes: document.getElementById('runNotes').value
        });
        await refreshRuns();
    } catch (err)
    {
        console.error('Failed to save run:', err);
    }
});

document.getElementById('stopRunButton').addEventListener('click', async () => {
    console.log('Stop Run');
    clearInterval(interval)
    interval = 0
    try
    {
        await postJson('/api/runs/current', {
            name: document.getElementById('runName').value,
            notes: document.getElementById('runNotes').value
        });
        await postJson('/api/runs/stop');
        await refreshRuns();
    } catch (err)
    {
        console.error('Failed to stop run:', err);
    }
});

document.getElementById('downloadCurrentRunButton').addEventListener('click', () => {
    console.log('Download Run');
    if (activeRun)
    {
        downloadRun(activeRun.id);
    }
});

const throttleSlider = document.getElementById('throttleSlider');
const throttleValue = document.getElementById('throttleValue');

throttleSlider.addEventListener('input', async () => {

    const value = parseFloat(throttleSlider.value);

    // Update displayed value
    throttleValue.innerText = value.toFixed(2);

    // Send to backend
    try
    {

        await fetch('/api/set/throttle', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                throttle: value
            })
        });

    } catch (err)
    {
        console.error('Failed to send throttle value:', err);
    }

});

refreshRuns();
