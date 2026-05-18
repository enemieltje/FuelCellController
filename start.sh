# Create a virtual environment (venv)
python -m venv --system-site-packages ./.venv
echo "Installing Packages..."

# Install python packages into the venv
# ./.venv/bin/pip install numpy --upgrade
./.venv/bin/pip install lgpio pigpio gpio   # gpio pins
./.venv/bin/pip install gpiozero            # Button input
./.venv/bin/pip install hx711               # Load cell

# Start the program
echo "Done! Starting Program"
./.venv/bin/python ./src/main.py
