INSERT INTO sensor_samples (
    run_id,
    timestamp,
    fuelcell_power,
    fuelcell_voltage,
    fuelcell_current,
    battery_power,
    battery_voltage,
    battery_current,
    load_power,
    load_voltage,
    load_current,
    battery_soc,
    pressure,
    thrust
)
VALUES (
    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
);
