# Fuel Cell Controller

Fuel Cell Controller is a Raspberry Pi application for a hydrogen fuel-cell test bench. It reads sensor values, controls fuel-cell and motor-load hardware, stores test runs in SQLite, and serves a local web dashboard for live monitoring and exports.

This project is hardware dependent. Many modules import Raspberry Pi GPIO, PWM, I2C, HX711, INA226, ADS1115, and Bronkhorst libraries, so the full program is expected to run on the Raspberry Pi connected to the test bench, not on a normal laptop.

## What Starts When The App Runs

`src/main.py` starts the application services in this order:

1. `Config` loads `config/default.ini`.
2. `Database` opens `data/sensors.db`, creates tables, and starts a worker thread.
3. `Drone` starts motor-load power and throttle control.
4. `Power_System` starts fuel-cell, battery, pressure, and power sensors.
5. `Server` serves the dashboard and API on the configured web port.

Sensor classes run small background threads. Each thread reads a physical device, then calls `Database.insert(...)`. The database service batches those samples before writing to SQLite so the sensors do not wait on disk writes.

## Project Layout

- `src/main.py` - program entry point and shutdown handling.
- `src/Server.py` - local HTTP server, dashboard files, and API endpoints.
- `src/Database.py` - SQLite storage, test-run metadata, CSV export, and Excel export.
- `src/Sensor.py` - base polling loop for sensors.
- `src/Power_System.py` - fuel-cell-side hardware setup and relay control.
- `src/Drone.py` - motor-load power, ESC arming, and throttle control.
- `src/Power_Meter.py` - INA226 power, voltage, and current readings.
- `src/Pressure_Sensor.py` - pressure transducer and Bronkhorst flow-controller readings.
- `src/Battery.py` - battery power and LiPo state-of-charge estimate.
- `src/Load_Cell.py` - HX711 load-cell calibration and thrust readings.
- `src/client/` - browser dashboard.
- `src/sql/` - SQL queries used by the database worker.
- `config/default.ini` - default web and calibration settings.
- `start.sh` - Raspberry Pi setup and startup helper.

## Raspberry Pi Setup

From the project folder on the Raspberry Pi:

```bash
chmod +x start.sh
./start.sh
```

The script creates `logs/`, `data/`, and `config/`, creates a virtual environment with system site packages, installs Python dependencies, and starts `src/main.py`.

The web dashboard defaults to port `8080`. On the Pi, open:

```text
http://<raspberry-pi-ip>:8080
```

## Configuration

`config/default.ini` contains:

- `WebConfig.port` - dashboard and API port.
- `Loadcell.*` - low/high calibration values used to convert raw load-cell readings into weight.

If a config value is missing, `Config` falls back to generated defaults from `src/Config.py`.

## Data And Exports

Runtime data is written to `data/sensors.db`. It is intentionally ignored by git because it is generated test data.

The dashboard can:

- Start and stop named test runs.
- Save notes for a run.
- Download a run as CSV.
- Download a run as Excel with charts.

