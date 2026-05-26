
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
