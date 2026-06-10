# Create all the required files and folders
mkdir -p logs config data
if [ -f logs/latest.log ]; then
    mv logs/latest.log logs/old.log
fi
touch logs/latest.log

# Create a virtual environment (venv)
python -m venv --system-site-packages ./.venv
echo "Installing Packages..."

# Install python packages into the venv
# ./.venv/bin/pip install numpy --upgrade
./.venv/bin/pip3 install lgpio pigpio gpio   # gpio pins
./.venv/bin/pip3 install gpiozero            # Button input
./.venv/bin/pip3 install hx711               # Load cell
./.venv/bin/pip3 install pandas openpyxl     # CSV/Excel export
./.venv/bin/pip3 install rpi-hardware-pwm
./.venv/bin/pip3 install pyserial pymodbus bronkhorst-propar

# Start the program
echo "Done! Starting Program"
./.venv/bin/python3 ./src/main.py
