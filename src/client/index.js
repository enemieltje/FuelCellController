
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

    const fc = await getData('power/fuelcell');
    const battery = await getData('power/battery');
    const drone = await getData('power/drone');
    const pressure = await getData('pressure');
    const soc = await getData('battery');
    const thrust = await getData('thrust');

    updateValue('fuelCellPower', fc.power.toFixed(1) + ' W');
    updateValue('fuelCellVoltage', fc.voltage.toFixed(1) + ' V');
    updateValue('fuelCellCurrent', fc.current.toFixed(1) + ' A');

    updateValue('batteryPower', battery.power.toFixed(1) + ' W');
    updateValue('batteryVoltage', battery.voltage.toFixed(1) + ' V');
    updateValue('batteryCurrent', battery.current.toFixed(1) + ' A');
    updateValue('batterySOC', soc.toFixed(0) + ' %');
    updateValue('batteryPercentage', soc.toFixed(0) + ' %');

    updateValue('motorPower', drone.power.toFixed(1) + ' W');
    updateValue('motorVoltage', drone.voltage.toFixed(1) + ' V');
    updateValue('motorCurrent', drone.current.toFixed(1) + ' A');
    updateValue('motorThrust', thrust.toFixed(1) + ' kg');

    updateValue('pressureValue', pressure.toFixed(2) + ' bar');

    addData(fuelCellChart, now, fc.power);
    addData(batteryChart, now, battery.power);
    addData(motorChart, now, drone.power);
    addData(pressureChart, now, pressure);
    addData(socChart, now, soc);
    addData(thrustChart, now, thrust);


}

function getData(varName) {
    console.log(`Fetching Data: ${varName}`)
    return new Promise((resolve) => {
        fetch(`/api/get/${varName}`)
            .then(response => {
                // after the response has been received
                console.log(response)
                if (!response.ok)
                {
                    throw new Error("Network response was not ok");
                }
                return response.json(); // read the response data and convert to json
            })
            .then(data => {
                // after data has been converted
                console.log(data)
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
        cell.colSpan = 7;
        cell.innerText = 'No runs found';
        row.appendChild(cell);
        tbody.appendChild(row);
        return;
    }

    runs.forEach((run) => {
        const row = document.createElement('tr');
        const values = [
            run.id,
            run.name || '',
            formatDate(run.started_at),
            run.ended_at ? formatDate(run.ended_at) : 'Active',
            run.sample_count,
            run.notes || ''
        ];

        values.forEach((value) => {
            const cell = document.createElement('td');
            cell.innerText = value;
            row.appendChild(cell);
        });

        const actionCell = document.createElement('td');
        const downloadButton = document.createElement('button');
        downloadButton.type = 'button';
        downloadButton.innerText = 'Download';
        downloadButton.addEventListener('click', () => downloadRun(run.id));
        actionCell.appendChild(downloadButton);
        row.appendChild(actionCell);

        tbody.appendChild(row);
    });
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
    // fetch('/api/button/start')
    if (!interval)
        interval = setInterval(fetchValues, 1000);
});

document.getElementById('stopButton').addEventListener('click', () => {
    console.log('Stop system');
    // fetch('/api/button/stop')
    clearInterval(interval)
    interval = 0
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
    try
    {
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
